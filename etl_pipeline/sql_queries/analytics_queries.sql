USE VicSchoolsDB;
GO

--Verifying the composite key prevented duplicates

SELECT School_No, Education_Sector, COUNT(*) AS cnt
FROM dim_schools
GROUP BY School_No, Education_Sector
HAVING COUNT(*)>1

--Relational Join on the composite key
SELECT e.School_Name, e.Year, e.[Grand Total], s.LGA_Name_Clean
FROM fact_enrolments e
INNER JOIN dim_schools s
    ON e.School_No = s.School_No
    AND e.Education_Sector = s.Education_Sector;

--Validate the row count, should be 6852 same as sqlite
--34 row gap, 2023-2025 snapshot mismatch

SELECT COUNT(*) AS joined_count
FROM fact_enrolments e
INNER JOIN dim_schools s
    ON e.School_No = s.School_No
    AND e.Education_Sector = s.Education_Sector;

--YoY growth window function
SELECT
    School_No, Education_Sector, School_Name, Year,
    [Grand Total] AS enrolment,
    LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year) AS prev_year_enrolment,
    ROUND(
        ([Grand Total] - LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year)) * 100.0
        / NULLIF(LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year), 0), 2
    ) AS yoy_growth_pct
FROM fact_enrolments
ORDER BY School_No, Education_Sector, Year;

--Outlier check
SELECT TOP 20 *
FROM (
    SELECT
        School_No, Education_Sector, School_Name, Year,
        [Grand Total] AS enrolment,
        LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year) AS prev_year_enrolment,
        ([Grand Total] - LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year)) * 100.0
        / NULLIF(LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year), 0) AS yoy_growth_pct
    FROM fact_enrolments
) t
WHERE ABS(yoy_growth_pct) > 100
ORDER BY yoy_growth_pct DESC;

--Demand Squeeze -ratio and absolute, excluding Unincorporated Vic

--Ratio version
WITH current_enrolments AS (
    SELECT LGA_Name_Clean, SUM([Grand Total]) AS total_current
    FROM fact_enrolments
    WHERE Year = 2025 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
),
future_demand AS (
    SELECT LGA_Name_Clean, SUM(Primary_Demand + Secondary_Demand) AS total_future_demand
    FROM dim_population_projection
    WHERE Year = 2031 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
)
SELECT TOP 5
    c.LGA_Name_Clean, c.total_current, f.total_future_demand,
    ROUND(f.total_future_demand * 1.0 / c.total_current, 2) AS demand_squeeze_ratio
FROM current_enrolments c
INNER JOIN future_demand f ON c.LGA_Name_Clean = f.LGA_Name_Clean
ORDER BY demand_squeeze_ratio DESC;

--Absolute gap version
WITH current_enrolments AS (
    SELECT LGA_Name_Clean, SUM([Grand Total]) AS total_current
    FROM fact_enrolments
    WHERE Year = 2025 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
),
future_demand AS (
    SELECT LGA_Name_Clean, SUM(Primary_Demand + Secondary_Demand) AS total_future_demand
    FROM dim_population_projection
    WHERE Year = 2031 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
)
SELECT TOP 5
    c.LGA_Name_Clean, c.total_current, f.total_future_demand,
    ROUND(f.total_future_demand - c.total_current, 0) AS absolute_demand_gap
FROM current_enrolments c
INNER JOIN future_demand f ON c.LGA_Name_Clean = f.LGA_Name_Clean
ORDER BY absolute_demand_gap DESC;

--Save as Views
DROP VIEW IF EXISTS vw_school_growth_trends;
GO

CREATE VIEW vw_school_growth_trends AS
SELECT
    School_No, Education_Sector, School_Name, Year,
    [Grand Total] AS enrolment,
    LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year) AS prev_year_enrolment,
    ROUND(
        ([Grand Total] - LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year)) * 100.0
        / NULLIF(LAG([Grand Total]) OVER (PARTITION BY School_No, Education_Sector ORDER BY Year), 0), 2
    ) AS yoy_growth_pct
FROM fact_enrolments;
GO

CREATE VIEW vw_lga_demand_ratio AS
WITH current_enrolments AS (
    SELECT LGA_Name_Clean, SUM([Grand Total]) AS total_current
    FROM fact_enrolments
    WHERE Year = 2025 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
),
future_demand AS (
    SELECT LGA_Name_Clean, SUM(Primary_Demand + Secondary_Demand) AS total_future_demand
    FROM dim_population_projection
    WHERE Year = 2031 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
)
SELECT c.LGA_Name_Clean, c.total_current, f.total_future_demand,
    ROUND(f.total_future_demand * 1.0 / c.total_current, 2) AS demand_squeeze_ratio
FROM current_enrolments c
INNER JOIN future_demand f ON c.LGA_Name_Clean = f.LGA_Name_Clean;
GO

CREATE VIEW vw_lga_demand_absolute AS
WITH current_enrolments AS (
    SELECT LGA_Name_Clean, SUM([Grand Total]) AS total_current
    FROM fact_enrolments
    WHERE Year = 2025 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
),
future_demand AS (
    SELECT LGA_Name_Clean, SUM(Primary_Demand + Secondary_Demand) AS total_future_demand
    FROM dim_population_projection
    WHERE Year = 2031 AND LGA_Name_Clean != 'Unincorporated Vic'
    GROUP BY LGA_Name_Clean
)
SELECT c.LGA_Name_Clean, c.total_current, f.total_future_demand,
    ROUND(f.total_future_demand - c.total_current, 0) AS absolute_demand_gap
FROM current_enrolments c
INNER JOIN future_demand f ON c.LGA_Name_Clean = f.LGA_Name_Clean;
GO


