## Quantitative analysis of judgments by the European Court of Justice
### Database schema
Currently all values are stored as string[], since most of them seem to have a small chance of containing multiple pieces of data.

key | value-type | description
----|------------|------------
_id | string | MongoDB UID
reference | string[] | Cellar API reference number
text | string[] | Full text of the judgment
keywords | string[] |
parties | string[] | Parties involved in the judgment
subject | string[] | Subject of the case
endorsements | string[] |
grounds | string[] | Legal grounds
decisions_on_costs | string[] |
operative_part | string[] | 
celex | string[] | CELEX number of the judgment
author | string[] |
subject_matter | string[] | Subject matter descriptors
case_law_directory | string[] | Assigned case-law directory code
ecli | string[] | European 5-part unique document identifier
date | string[] | Adoption, signature or publication date (varies)
case_affecting | string[] | CELEX numbers of acts quoted in the operative part
applicant | string[] | Entity, who submitted the application
defendant | string[] | Entity defending
affected_by_case | string[] | CELEX numbers of decisions affecting the act
procedure_type | string[] | Nature and outcome (where possible) of the proceedings
