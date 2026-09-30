#Phase 4 - Business Strategy and Insights

#Capital Works Allocation
    If the Victorian Government has a fixed budget to build three new schools by 2031, the three Local Government Areas that should recieve priority funding are Casey, Wyndham and Melton based on the absolute gap between 2025 and 2031 projected school age population(Demand Squeeze Analysis)

#Data
    LGA         2025 Enrolment          2031 Demand        Absolute Gap
    Casey       66,705                   102,220              35,515
    Wyndham     65,465                   95,930               30,465
    Melton      36,742                   64,670               27,929

    Casey shows the largest shortfall, with a gap of approximately 35,515 between its current enrolment and 2031 projected demand. It is followed by Wyndham and Melton.

    This is based on absolute gap rathe than proportional growth. Smaller lGAs like Golden Plains, Surf Coast, etc are experiencing rapid relative change i.e. high percentange growth but represent a smaller absolute number of students requiring new school places.

    All three recommended LGAs are in outer Melbourne growth corridors, which are consistent with residential development patterns giving futher credibility to this absolute gap driven ranking.


#Limitation
    Identifying at least two schools currently at >110% capacity located in an LGA where school-age population is projected to plateau or decline:

    This project's Peak Enrolment measure compares each school's current enrolment to its own historical maximum recorded value. So the measure can never exceed 100%. There is no data for official classroom and building capacity, so >110% finding is not obtainable from this dataaset.

#But two of many schools at their historical peak located in LGAs where 2031 demand is flat or declining are as follow;

LGA_Name_Clean      current_enrolment_2025      demand_2031
Boroondara	        34173.3	                    33110.0
Greater Dandenong	29317.5	                    29310.0

#Recommended operational strategy:
    For schools in genuinely declining population LGAs, relocatable portables are the appropriate response for their low cost, temporary pressure avoiding investement in permanent way which would become underutilised as population declines.
    
    For schools in LGAs with positive growth of population, a permanent extension of schools is more appropriate for durable capacity increase.

#Recommendation for improving this analysis

    A genuine >110% overcrowding assessment requires official school capacity data such as classroom counts, building area, enrolment ceilings, etc.

#Other limitation
    Data capturing mismatch: The school locations dataset represent 2025 data, while enrolment data is recieved from three years 2023 to 2025.  This produced 34 enrolment records with no matching school, most likely due to renumbering, closing or merging.

    Age-band mismatch: The population projections is in 5-year age bands not single years. So it required a proportional split of 40%/60% of the shared 10-14 age band acress Primary and Secondary students.

    School identity data quality: 187 school names are shared by multiple distinct schools across different LGAs. This required a display name School Name+LGA to ensure accurate analysis at the individual school level.

#Summary
    This analysis identifies Casey, Wyndham and Melton as the highest priority LGAs for new school capital works by 2031, based on the largest absolute gap between current enrolment and projected demand. Genuine overcrowding analysis depend on access to school capacity data which is not available in the public dataaset used in this project.