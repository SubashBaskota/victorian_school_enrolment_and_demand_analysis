

--Victorian School Capacity Analysis — MS SQL Server Setup (Docker)


--Create database
CREATE DATABASE VicSchoolsDB;
GO

USE VicSchoolsDB;
GO


--Drop any prior incompatible structures
DROP TABLE IF EXISTS fact_enrolments;
DROP TABLE IF EXISTS dim_schools;
DROP TABLE IF EXISTS dim_population_projection;
GO

--Create dim_schools
CREATE TABLE dim_schools (
    Education_Sector NVARCHAR(50),
    Entity_Type INT,
    School_No INT,
    School_Name NVARCHAR(255) NOT NULL,
    School_Type NVARCHAR(50),
    School_Status NVARCHAR(50),
    Address_Line_1 NVARCHAR(255),
    Address_Town NVARCHAR(100),
    Address_Postcode NVARCHAR(10),
    Region NVARCHAR(100),
    Area NVARCHAR(100),
    LGA_ID INT,
    LGA_Name NVARCHAR(100),
    LGA_TYPE NVARCHAR(50),
    X FLOAT,
    Y FLOAT,
    LGA_Name_Clean NVARCHAR(100),
    CONSTRAINT UQ_School_Sector UNIQUE (School_No, Education_Sector)
);
GO

--Create fact_enrolments
CREATE TABLE fact_enrolments (
    School_No INT,
    Education_Sector NVARCHAR(50),
    Entity_Type INT,
    School_Name NVARCHAR(255),
    School_Type NVARCHAR(50),
    School_Status NVARCHAR(50),
    [Prep Total] FLOAT,
    [Year 1 Total] FLOAT,
    [Year 2 Total] FLOAT,
    [Year 3 Total] FLOAT,
    [Year 4 Total] FLOAT,
    [Year 5 Total] FLOAT,
    [Year 6 Total] FLOAT,
    [Primary Ungraded Total] FLOAT,
    [Primary Total] FLOAT,
    [Year 7 Total] FLOAT,
    [Year 8 Total] FLOAT,
    [Year 9 Total] FLOAT,
    [Year 10 Total] FLOAT,
    [Year 11 Total] FLOAT,
    [Year 12 Total] FLOAT,
    [Secondary Ungraded Total] FLOAT,
    [Secondary Total] FLOAT,
    [Grand Total] FLOAT,
    Year INT,
    LGA_Name NVARCHAR(100),
    Region_Name NVARCHAR(100),
    Area_Name NVARCHAR(100),
    LGA_TYPE NVARCHAR(50),
    LGA_Name_Clean NVARCHAR(100)
);
GO


--Create dim_population_projection
--Column is named LGA_Name here for BULK INSERT positional mapping,
-- but actually receives already-cleaned LGA names from population_clean.csv.
-- Renamed to LGA_Name_Clean immediately after load (see Step 8).
CREATE TABLE dim_population_projection (
    LGA_Name NVARCHAR(100),
    Year INT,
    Primary_Demand FLOAT,
    Secondary_Demand FLOAT
);
GO



--Bulk load all 3 CSVs
-- Prerequisite: CSVs copied into the container first via:
--docker cp etl_pipeline/clean_data/schools_clean.csv mssql_server:/var/opt/mssql/
--docker cp etl_pipeline/clean_data/fact_enrolments.csv mssql_server:/var/opt/mssql/
--docker cp etl_pipeline/clean_data/population_clean.csv mssql_server:/var/opt/mssql/
BULK INSERT dim_schools
FROM '/var/opt/mssql/schools_clean.csv'
WITH (
    FORMAT = 'CSV', 
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0a'
);
GO

BULK INSERT fact_enrolments
FROM '/var/opt/mssql/fact_enrolments.csv'
WITH (
    FORMAT = 'CSV', 
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0a'
);
GO

BULK INSERT dim_population_projection
FROM '/var/opt/mssql/population_clean.csv'
WITH (
	FORMAT = 'CSV',
	FIRSTROW = 2, 
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '0x0a');
GO

--Verify row counts
SELECT COUNT(*) AS total_schools FROM dim_schools;              -- expect 2301
SELECT COUNT(*) AS total_enrolments FROM fact_enrolments;       -- expect 6886
SELECT COUNT(*) AS total_population_rows FROM dim_population_projection; -- expect 240

--Fix the population table's column naming
EXEC sp_rename 'dim_population_projection.LGA_Name', 'LGA_Name_Clean', 'COLUMN';
GO


--Spot-check the data
SELECT TOP 10 * FROM dim_schools;
SELECT TOP 10 * FROM dim_population_projection;

ALTER TABLE dim_schools ADD Record_ID INT IDENTITY(1,1);
ALTER TABLE fact_enrolments ADD Enrolment_ID INT IDENTITY(1,1);

SELECT TOP 5 Record_ID, School_No, School_Name FROM dim_schools;


SELECT TOP 5 Record_ID, School_No, School_Name FROM dim_schools;
