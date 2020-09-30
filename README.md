# Quantitative analysis of judgments by the European Court of Justice
## Requirements
- [Python 3.7](https://www.python.org/downloads/release/python-379/) (3.8 only supported under Linux)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/de/downloads/0) (Windows only) 
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
analysis | Dictionary[ ] | Defenition of the analysis to perform. See [Analysis](#analysis-metrics-whole-corpus) and [query example](#analysis-of-single-document).  

The keys of the JSON returned from the server matches the types specified for analysis.

#### Analysis `metrics`: whole corpus
`metric` | arguments | type(return value) | description
---------|--------------|---------|------------
tokens | `remove_punctuation`, `remove_stop_words`,`include_pos`, `exclude_pos`, `min_freq_per_doc` | List[str] | A customizable list of all tokens in the corpus.
unique tokens | `remove_punctuation`, `remove_stop_words`,`include_pos`, `exclude_pos`, `min_freq_per_doc` | Set[str] | A customizable set of all unique tokens in the corpus.
token count | | int | # of all tokens.
average token length | `remove_punctuation`, `remove_stop_words`,`include_pos`, `exclude_pos`, `min_freq_per_doc` | float | Mean token length in corpus based on different filter options.
word count | `remove_stop_words` | int | # of all words.
average word length | `remove_stop_words`| float | Mean word length in corpus.
most frequent words | `remove_stop_words`, `lemmatise`, `n` | List[Tuple[str, int]] | Most frequently used words. Can be lemmatised and stop words removed
sentences | | List[str] | All sentences in the corpus.
sentence count | | int | # of sentences.
lemmata | | List[Tuple[str, str] | A list of all words and their lemmata.
pos tags | | (List[Tuple[str, str] | A list of all tokens and their part of speech tags.
named entities | | List[Tuple[str, List[str]]] | Calculates all named entities in the corpus and groups them by their label.
readability | | float | The average readability score of the corpus ([Flesch-Reading-Ease](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease))
n-grams | `n`, `filter_stop_words`, `filter_nums`, `min_freq` | List[str] | The most common n-grams (collocations) with length n (default 2). Can be optionally be filtered.
sentiment | | int | A normalized sentiment value for the whole corpus (0 - negative, 1 - neutral, 2 - positive sentiment ([Paper](https://arxiv.org/abs/1408.5882)). 

#### Specific `metrics` : specific sub-corpora
`type`-value | arguments | type(return value) | description
-------------|-----------|--------------------|------------
keywords | `top_n` | List[Tuple[str, int]] | List of keyterms computed with the [PositionRank](https://www.aclweb.org/anthology/P17-1102.pdf) algorithm, with their corresponding weight in the document. Only available on single documents or per document basis.
similarity |  | float | Calculates the vector similarity of two documents. Only available when comparing two documents. 

#### Specific `metrics` : sub-corpus
The following `metrics` specify per-doc-analysis and return a list of their respective `metric` for each document described above:
- `tokens per doc`
- `sentences per doc`
- `pos tags per doc`
- `lemmata per doc`
- `named entities per doc`
- `readbility per doc`
- `sentiment per doc`
- `keywords per doc`

Note: `keywords per doc` is only available per document and cannot be computed on a corus at once, because PositionRank is not suited for more than one document.

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
author | { ids : string[ ], labels : string[ ] } |
subject_matter | { ids : string[ ], labels : string[ ] } | Subject matter descriptors
case_law_directory | { ids : string[ ], labels : string[ ] } | Assigned case-law directory code
applicant | { ids : string[ ], labels : string[ ] } | Entity, who submitted the application
defendant | { ids : string[ ], labels : string[ ] } | Entity defending
procedure_type | { ids : string[ ], labels : string[ ] } | Nature and outcome (where possible) of the proceedings
