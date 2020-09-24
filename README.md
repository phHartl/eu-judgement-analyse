# Quantitative analysis of judgments by the European Court of Justice
## Database schema

key | value-type | description
----|------------|------------
_id | string | MongoDB UID
reference | string | Cellar API reference number
title | string | Document title
text | string | Full text of the judgment
keywords | string |
parties | string | Parties involved in the judgment
subject | string | Subject of the case
endorsements | string |
grounds | string | Legal grounds
decisions_on_costs | string |
operative_part | string | 
celex | string | CELEX number of the judgment
ecli | string | European 5-part unique document identifier
date | string | Adoption, signature or publication date (varies)
case_affecting | string[] | CELEX numbers of acts quoted in the operative part
affected_by_case | string[] | CELEX numbers of decisions affecting the act
author | { id : label } |
subject_matter | { id : label } | Subject matter descriptors
case_law_directory | { id : label } | Assigned case-law directory code
applicant | { id : label } | Entity, who submitted the application
defendant | { id : label }| Entity defending
procedure_type | { id : label } | Nature and outcome (where possible) of the proceedings

## Server API
The API accepts a JSON-body when requesting data and returns results as JSON.
Path: `/eu-judgments/api/data`, method: GET

### JSON format
The JSON requires 3 mandatory keys to be specified:
- "language": The language of documents to be used. Values: `en`, `de`
- "corpus": The corpus to be used for analysis. Either "all" or specified with a Dictionary of database keys and values. 
- "analysis": Type of analysis to perform. A List of Dictionaries, specifying a "type" and optional arguments for each.
The keys of the JSON returned from the server match the types specified for analysis.

#### Analysis `types`
`type`-value | arguments | type(return value) | description
-----|----------------------|--------------------|------------
n-grams | `n`, `limit` | (str, int)[] | the most common n-grams with length n (default 2). array size defined by limit (default 10)
tokens | `limit` | str[] | the most common tokens
sentences | | str[] | all sentences of the document
lemata | | (str, str)[] | a list of all words and their lemmata
pos tags | | (str, str)[] | a list of all tokens and their part of speech tags
named entities | | (str, str[])[] | a list of all categories and their entities
readability | | float | the readability score of the document
similatiry | `other celex` (mandatory) | float | The similarity score of the corpus document with the other one. Requires a celex number.


#### Analysis of single document
Example:
```json
{
    "language": "en",
    "corpus": 
        {
            "celex": "61955CJ0008"
        },
    "analysis": [
        {
            "type": "n-grams",
            "n": 2,
            "limit": 10
        },
        {
            "type": "readability"
        },
        {
            "type": "tokens",
            "limit": 50
        }
    ]
}
```

#### Creating custom sub-corpora
Sub-corpora can be created using values that must or must included in a document to be added.  
Set the `search identifier` flag to `true`, if you want to search for abbriviations (ids) instead of verbose descriptions (labels).  
Set `operator` to `NOT`, if you want to exclude all documents containing this value from your sub-corpus.  
When using an array of values, all documents matching any of the values in the array will be in- or exluded.  

Example custom subcorpus:
```json
{
    "language": "en",
    "corpus": [
        {
            "column" : "date",
            "start date" : "1958-07-17",
            "end date" : "1975-02-25"
        },
        {
            "column" : "author",
            "value" : "Court of Justice"
        },
        {
            "operator" : "NOT",
            "search identifier" : true,
            "column" : "case_law_directory",
            "value" ["F", "C"]
        }
   ]
}
```
