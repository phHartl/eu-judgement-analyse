# Quantitative analysis of judgments by the European Court of Justice
## Requirements
- [Python 3.7](https://www.python.org/downloads/release/python-379/) (3.8 unsupported)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/de/downloads/0)  
- To install packages, run `pip install -r requirements.txt`

## Usage
Please make sure an instance of MongoDB is installed and running.
### Corpus Acquisition 
Run `setup.py` and follow the prompts on the CLI to create a corpus of judgments for all specified languages.
### Analysis
Run `server.py` to start the server  on `localhost:5000`. Once running, you can send corpus and analysis requests via HTTP requests with JSON body.

## Server API
The API accepts a JSON-body when requesting data and returns results as JSON.
Path: `/eu-judgments/api/data`, method: GET

### JSON format
The JSON requires 3 mandatory keys to be specified:
key | data type | description
----|-----------|------------
language | `en`,`de` | language of corpus to use
corpus | `all`, Dictionary[ ] | (sub-)corpus query. See the [schema](#database-schema) and [query example](#creating-custom-sub-corpora).
analysis | Dictionary[ ] | Defenition of the analysis to perform. See [Analysis](#analysis-types) and [query example](#analysis-of-single-document).  

The keys of the JSON returned from the server matches the types specified for analysis.

#### Analysis `types`
`type`-value | arguments | type(return value) | description
-------------|-----------|--------------------|------------
n-grams | `n`, `limit` | (str, int)[ ] | the most common n-grams with length n (default 2). array size defined by limit (default 10)
tokens | `limit` | str[ ] | the most common tokens
token count | | int | # of tokens
word count | `remove stop words` | int | # of words
most frequent words | `remove stop words`, `lemmatise`, `limit` | (str, str)[ ] | Most frequently used words. Can be lemmatised and stop words removed
sentences | | str[ ] | all sentences of the document
sentence count | | int | # of sentences
lemmata | | (str, str)[ ] | a list of all words and their lemmata
pos tags | | (str, str)[ ] | a list of all tokens and their part of speech tags
named entities | | (str, str[ ])[ ] | a list of all categories and their entities
average word length | `remove stop words` | float | 
readability | | float | the readability score of the document
similarity | `other celex` (mandatory) | float | The similarity score of the corpus document with the other one. Requires a celex number.

#### Specific `types` : single doc
`type`-value | arguments | type(return value) | description
-------------|-----------|--------------------|------------
similarity | `other celex` | float | Similarity score between the single corpus doc and a `other` doc, specified by its `celex` identifier

#### Specific `types` : sub-corpus
The following `types` specify per-doc-analysis and return a list of their respective `type` described above:
- `tokens per doc`
- `sentences per doc`
- `pos tags per doc`
- `lemmata per doc`
- `named entities per doc`
In addition to these, `average readability` returns the average score across the defined corpus.

#### Analysis of single document
Example:
```json
{
    "language": "en",
    "corpus": 
        {
            "column" : "celex",
            "value": "61955CJ0008"
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
Sub-corpora can be created using values that must or must not be included in a document to be added. Use `column` to determine the column according to the database schema and `value` to determine its value. (Exception: `date` taking a `start date` and `end date`)  
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
            "value" : ["F", "C"]
        }
   ]
}
```

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
case_affecting | string[ ] | CELEX numbers of acts quoted in the operative part
affected_by_case | string[ ] | CELEX numbers of decisions affecting the act
author | { ids : string[], labels : string[] } |
subject_matter | { ids : string[ ], labels : string[ ] } | Subject matter descriptors
case_law_directory | { ids : string[ ], labels : string[ ] } | Assigned case-law directory code
applicant | { ids : string[ ], labels : string[ ] } | Entity, who submitted the application
defendant | { ids : string[ ], labels : string[ ] } | Entity defending
procedure_type | { ids : string[ ], labels : string[ ] } | Nature and outcome (where possible) of the proceedings
