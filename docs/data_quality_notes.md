Data Quality Notes - Victorian School Enrolment and Demand Analysis

This document has recorded the data quality issues, modelling decisions, terminology corrections during the development of this project(ETL). Each entry follows the same structure: what was found, why it happened and how it was resolved.

1. Source Data Inconsistencies (Phase 1 - ETL)
1.1 Multi-row Excel Headers (VIF population file)
    Issue: The VIF Excel file's real column headers were not on row 0, and were in two rows with year label and age band label
    Fix: Used Pandas to correctly parse the two-row header

1.2 Inconsistent LGA naming across sources
    Issue: LGA names appeared as Casey (C) in some files and like Latrobe (C) (Vic.) 
    Fix: Built a recursive regex function (clean_lga_name()) that strips the trailing suffixes repeatedly

1.3 Missing 2023 geography data
    Issue: 14 schools could not be matched to an LGA via automated lookup.
    Fix: They were manually entered from public school registration records.

1.4 VIF data source version change
    I first did this ETL project using python and sqlite but then I re-started the project and used MS SQL Server. The original VIF file was not reliably discovered via automated extraction script, may be due to new release, but the ranking of LGAs with highest demand gap remain consistent with Casey, Wyndham, Melton, Whittlesea and Hume.
    The figures were identical across SQL Server and Power BI

2. Database Design Issues (Phase-2 SQL)
2.1 School_No was not a unique identifier
    Issue: Same school numbers where shared across various Education Sectors, e.g. School_No=1 for both Alberton Primary School (Government) and Wesly College (Independent). 
    Implemented a composite key of School_No + Education_Sector across all tables and joins

2.2 Mismatch between enrolment years and school locations
    Issue: 34 enrolment records (25 from 2023 and 9 from 2024) have no matching school in the 2025 School Locations snapshot, since dim_schools represents a single point in time capture
    Fix: Documented and excluded form joins rather than force matched; confirmed identical in both SQL and Power BI, validating consistency across different layers of data engineering

3. Power BI / DAX Issues (Phase-3 PBI)
3.1 Many-to-many relationship (LGA dimension)
    Issue: Neither dim_schools[LGA_Name_Clean] nor dim_population_projection[LGA_Name_Clean] contained unique values, production a many-to-many relationship warning
    Fix: Built a proper dim_lga table and to sit between the two and making a one-to-many Start Schema structure

3.2 Hidden duplicate LGA value
    Issue: dim_lga initially contained 81 rows instead of expected 80 as South Gippsland appeared twice due to inconsistent whitespace/formatting not caught by initial deduplication.
    Fix: Applied Trim and Clean transform in Power Query before deduplicating

3.3 DAX filter context instability
    Issue: The 3-Year Peak Enrolment measure produced inconsistent results depending on which other fields were present in the visual, correct in a simple tablem, incorrect once a category field was added to the chart
    Root cause: Unstable interaction between ALLEXCEPT / SELECTEDVALUE and visual-level filter context
    Fix: Rewrote the measure to capture row values into variable before applying CALCULATE(...), making the result fully independent of visual context

3.4 School name ambiguity
    Issue:187 school names are shared by multiple distint schools across different LGAs. Grouping a table by School_Name caused SELECTEDVALUE to return blank due to the ambiquity
    Fix: Created a School Display Name calculated column(Name+LGA) and used in all school-level visuals to guarentee uniqueness

4. Terminology and Naming Corrections
4.1 Over/Under Capacity category labels
    Issue: Original strain category labels implied knowledge of real physical school capacity which does not exist in any source dataset. The enrolment numbers only compare to the 3-Years Peak value from 2023 to 2025. 
    Fix: Re-labeled categories to At/Near/Below 3-Year Peak and changes the underlying measure from Capacity Threshold to Peak Enrolment (2023 - 2025)

4.2 Project title
    Issue: Victorian School Capacity Analysis implied the project measures physical school capactiy directly
    Fix: Renamed to "Victorian School Enrolment and Demand Analysis" accurately reflecting the two data soruces with no overclaiming

5. Limitations
    - No official school capacity(building/classroom) data exists in any source file
    - Population projections apply LGA-wide age-band proportions and do not account for residential zoning and catchement boundaries
    - The VIF population projection release used by the automated pipeline(Sept 2023) is less precise(rounded to nearest 10) than the originally explored December 2023     release


