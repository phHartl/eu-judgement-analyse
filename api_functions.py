from collections import Counter
from mongo import *
from analysis import Analysis, CorpusAnalysis

def __get_top_n_grams(analyser, args):
    return_limit = 10   # default

    # get n-grams
    n_grams = []
    if args.get('n'):
        n_grams = analyser.get_n_grams(n=args['n'])
    else:
        n_grams = analyser.get_n_grams()

    # most frequent n-grams. return size determined by limit
    newlist = []
    for item in n_grams:
        newlist.append(str(item))
    top_ngram_list = Counter(newlist).most_common(args.get('limit'))

    # list of tuples -> dict
    top_ngram_dict = {}
    for _tuple in top_ngram_list:
        top_ngram_dict[_tuple[0]] = _tuple[1]

    return top_ngram_dict

def __get_top_tokens(analyser, args):
    # TODO: add tokenizer parameter to args
    tokens = analyser.get_tokens(remove_punctuation=True, remove_stop_words = True)
    return_limit = 50  # default: most frequent tokens returned
    if isinstance(args.get('limit'), int):
        return_limit = args.get('limit')
    top_tokens_list = Counter(tokens).most_common(return_limit)

    # list of tuples -> dict
    top_tokens_dict = {}
    for _tuple in top_tokens_list:
        top_tokens_dict[_tuple[0]] = _tuple[1]

    return top_tokens_dict

def __get_tuples(query, language):
    operator = 'and'
    if query.get('operator'):
        operator = query.get('operator')
    if not query.get('search identifier'):
        cursor = get_docs_by_value(query.get('search column'), query.get('search value'), language)
        return (operator, cursor)
    else:
        return (operator, {
            "column": query.get('search column'),
            "value" : query.get('search value')
        })

def generate_subcorpus(corpus_args, language):
    corpus = []
    op_curs_tuples = []
    object_queries = []
    keys_containing_dicts = ["author", "subject_matter", "case_law_directory",
                            "applicant", "defendant", "procedure_type"]
    docs = get_docs_by_custom_query(corpus_args, language)
    # for query in corpus_args:
    #     op_curs_tuples.append(__get_tuples(query, language))
    # print(op_curs_tuples)
    # if isinstance(corpus_args, list):
    #     pass
    # else:
    #     for k,v in corpus_args.items():
    #         if k not in keys_containing_dicts:
    #             corpus.append(get_docs_by_value(k, v, language))
    # for item in corpus:
    #     print(corpus.get('celex'))

args = [
        {
            "column": "author",
            "value": "Court of Justice"
        },
        {
            "operator": "NOT",
            "search identifier": True,
            "column": "case_law_directory",
            "value": 'F'
        },
        {
            "column": 'applicant',
            "value": 'Person'
        }
]
get_docs_by_custom_query(args,'en')

def analyse_selected_corpus(corpus, args, language):
    # setup
    analyser = CorpusAnalysis(language)
    texts = []
    for doc in corpus:
        texts.append(doc.get('text'))

    analyser.init_pipeline(texts)
    analysis_data = {}

    if args.get('type') == 'n-grams':
        analysis_data['n-grams'] = __get_top_n_grams(analyser, args)

    del analyser
    return analysis_data

def analyse_selected_doc(doc, args, language):
    # setup
    analyser = Analysis(language)
    analyser.init_pipeline(doc.get('text'))
    analysis_data = {}

    if args.get('type') == 'n-grams':
        analysis_data = __get_top_n_grams(analyser, args)
    if args.get('type') == 'readability':
        analysis_data = analyser.get_readability_score()
    if args.get('type') == 'tokens':
        analysis_data = __get_top_tokens(analyser, args)

    del analyser
    return analysis_data
