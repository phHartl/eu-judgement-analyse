# Quantitative analysis of judgments by the European Court of Justice
## Requirements
- [EU account](https://webgate.ec.europa.eu/cas/login)
- [EUR-Lex API access](https://eur-lex.europa.eu/content/help/faq/reuse-contents-eurlex-details.html)
- [Python 3.7](https://www.python.org/downloads/release/python-379/) (3.8 only supported under Linux)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/de/downloads/0) (Windows only) 
- [nodejs](https://nodejs.org/en/)
- [Redis](https://redis.io/) (Optional, only if you want to use the server mode)
- To install the python packages, run `pip install -r requirements.txt`
- To install the node packages, `npm install` inside the `webapp` folder

## Usage
### EUR-LEX access
Create a file called `eur_lex.ini` in the root directory of the project with your EUR-LEX username and password specified as follows:
```
[eur-lex]
username=APIUsername
password=APIPassword
```
### Corpus Acquisition 
Run `setup.py` and follow the prompts on the CLI to create a corpus of judgments for all specified languages. If you want to use the API and the web application please make sure to have an instance of MongoDB running or select `Export to corpus.csv` instead if you wish to only use the dataset.

### Analysis
Run `server.py` to start the server  on `localhost:5000`. Once running, you can send corpus and analysis requests via HTTP requests with JSON body.

### Progressive web application
Run `npm start`inside the webapp subfolder to start the webapplication on `localhost:3000`. Once running, you can open the website on your web browser of choice.

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
Unless specified otherways we always use the pre-trained [blackstone](https://research.iclr.co.uk/blackstone) by The Incorporated Council of Law Reporting for England and Wales for english and the standard medium [german model](https://spacy.io/models/de#de_core_news_md) of spaCy for all metrics. Furthermore every text also gets preprocessed and normalized. This enhances the quality of word & sentence separation significantly. Specifically we remove paragraph numbers, white spaces before punctuation & parentheses, certain legal reoccurring legal headlines as well as an ever present header in older texts.

`metric` | arguments | type(return value) | description
---------|--------------|---------|------------
tokens | `remove_punctuation`, `remove_stopwords`,`include_pos`, `exclude_pos`, `min_freq_per_doc` , `limit` | List[str] | A customizable list of all tokens in the corpus.
unique_tokens | `remove_punctuation`, `remove_stopwords`,`include_pos`, `exclude_pos`, `min_freq_per_doc` | Set[str] | A customizable set of all unique tokens in the corpus.
token_count | `remove_punctuation`, `remove_stopwords`,`include_pos`, `exclude_pos`, `min_freq_per_doc` | int | # of all tokens.
average_token_length | `remove_punctuation`, `remove_stopwords`,`include_pos`, `exclude_pos`, `min_freq` | float | Mean token length in corpus based on different filter options.
average_word_length | `remove_stopwords`,`include_pos`, `exclude_pos`, `min_freq`| float | Mean word length in corpus.
most_frequent_words | `remove_stopwords`, `lemmatise`, `n` | List[Tuple[str, int]] | Most frequently used words. Can be lemmatised and stop words removed
sentences | | List[str] | All sentences in the corpus.
sentence_count | | int | # of sentences.
lemmata | `remove_stopwords`,`include_pos`, `exclude_pos` | List[Tuple[str, str] | A list of all words and their lemmata (we use [3] for german lemmatisation).
pos_tags | `include_pos`, `exclude_pos` | (List[Tuple[str, str] | A list of all tokens and their [universal part of speech tags](https://universaldependencies.org/u/pos/) .
named_entities | | List[Tuple[str, List[str]]] | Calculates all named entities in the corpus and groups them by their label.
readability | | float | The average readability score of the corpus ([Flesch-Reading-Ease](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease). Identical to `Defensiveness` used by [5].
n-grams | `n`, `filter_stopwords`, `filter_nums`, `min_freq` | List[str] | The most common n-grams (collocations) with length n (default 2). Can be optionally be filtered. Similar to work done by [6].
sentiment | | int | A normalized sentiment value for the whole corpus (0 - negative, 1 - neutral, 2 - positive sentiment) by [2]. An almost identical method is used by [5] (called `Friendliness` in their work), which this feature is inspired from. 

#### Specific `metrics` : specific sub-corpora
`type`-value | arguments | type(return value) | description
-------------|-----------|--------------------|------------
keywords | `top_n` | List[Tuple[str, int]] | List of keyterms computed with the [PositionRank](https://www.aclweb.org/anthology/P17-1102.pdf) algorithm, with their corresponding weight in the document. Only available on single documents or per document basis.
similarity |  | float | Calculates the vector similarity (0 - 1) of two documents based on their word embeddings (similiar to [4]). Only available when comparing two documents, returns -1 instead if more or less than two documents are specified.

#### Specific `metrics` : sub-corpus
The following `metrics` specify per-doc-analysis and return a list of their respective `metric` for each document described above:
- `tokens_per_doc`
- `token_count_per_doc`
- `unique_tokens_per_doc`
- `most_frequent_words_per_doc`
- `sentences_per_doc`
- `sentence_count_per_doc`
- `pos_tags_per_doc`
- `lemmata_per_doc`
- `named_entities_per_doc`
- `readability_per_doc`
- `sentiment_per_doc`
- `keywords_per_doc`
- `n-grams_per_doc`

Note: `keywords` is only available per document and cannot be computed on a corpus at once, because PositionRank is not suited for more than one document.

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
## Customisation
By default the API is configured to on a single system without any scaling options enabled except multi-threading. The configuration file `config.ini` then looks something like this:

```
[execution_mode]
server_mode=False 
[mongo_db]
host=localhost
port=27017
collection=judgment_corpus
[celery]
broker=redis
host=localhost
port=6379
[analysis]
threads=-1
```
Besides the configuration of the database in the secion `mongo_db`, it is also possible to limit the analysis to certain number of threads by changing `threads` to a number of threads. By default it uses all threads (specified by -1). In this configuration however it is not possible to execute multiple request at the same time as there is only one analysis instance at a time. If you want to change this set `server_mode` to `True` and make sure `celery` & `redis` are installed and the later is running on your setup. If necessary change the redis port in the configuration file. Celery then acts as load distribution system (task queue) while redis acts as task broker. We provide two different task queues. One for small analysis tasks with less than ten documents in a corpus and one for bigger corpora. These are defined in `tasks.py`. To enable both queues open to separte terminals before starting your server and execute:

```
celery -A tasks.celery worker -Q celery -c2
```
This command starts a task queue with two processes (aka analysis instances) for time efficient analysis tasks. Note the `-c2` parameter here. This specifies the number of sub processes spawned for this queue. So if you want more than two process use another number here. Each process accepts multiple tasks (we use the default value of four here), before using a new process. In conclusion this configuration offers eight slots (two processes a four tasks) of time efficient calculation. 

```
celery -A tasks.celery worker -Q huge_corpus -c10 -Ofair
```
This command starts a task queue with ten processes (aka analysis instances). However here each process can only accept one task at a time. So if a new request is taken care of a whole new process is used to ensure proper parallelisation up the limit specified with `-c10` (in this case ten processes). After this limit has been reached, each new task must wait for an other task to be finished before being processed. To save memory we decided to end each process after execution if it exceeds a memory limit of 6 GB. The parameter `-Ofair` ensures each broker only accepts one task. Unfortunately this configuration parameter is currently ignored when set via Python so we need to specify it via command line (https://stackoverflow.com/questions/42433770/celery-multiple-workers-but-one-queue).


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

## Running the Web-App

- Install [nodejs](https://nodejs.org/en/), which comes with npm pre-packed
- Open a command line and navigate to the [webapp](./webapp) folder
- Install the required node modules with `npm install` (this only needs to be performed once for the first time install)
- Start the node server with `npm start`

After starting the server, the webapp can be reached on `localhost:3000` on your preferred browser by default. 
Make sure the python - Server is running as well, since it handles the queries sent through the webapp (see [Analysis](#analysis)).



## References

[1] Florescu, C., & Caragea, C. (2017,
 July). Positionrank: An unsupervised approach to keyphrase extraction from scholarly documents. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) (pp. 1105-1115).

[2] Kim, Y. (2014). Convolutional neural networks for sentence classification. arXiv preprint arXiv:1408.5882.

[3] Liebeck, M., & Conrad, S. (2015, July). Iwnlp: Inverse wiktionary for natural language processing. In Proceedings
 of the 53rd Annual Meeting of the Association for Computational 
Linguistics and the 7th International Joint Conference on Natural

[4] Ash, E., Chen, D. L., & Ornaghi, A. (2018). Implicit bias in the judiciary: Evidence from judicial language associations. Technical report. 4.1, 4.3

[5] Carlson, K., Livermore, M. A., & Rockmore, D. (2015). A quantitative analysis of writing style on the US Supreme Court. Wash. UL Rev., 93, 1461.

[6] Abegg, A., & Bubenhofer, N. (2016). Empirische Linguistik im Recht: 
Am Beispiel des Wandels des Staatsverständnisses im Sicherheitsrecht, 
öffentlichen Wirtschaftsrecht und Sozialrecht der Schweiz. Ancilla Iuris, (1), 1-41.
