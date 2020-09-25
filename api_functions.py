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

def __to_sentence_list(span_list):
    sentences = []
    for span in span_list:
        sentences.append(str(span))
    return sentences

def __to_tuple_list(token_tuples):
    tuples = []
    for item in token_tuples:
        tuples.append((str(item[0]), str(item[1])))
    return tuples

def __analyse_generic_parameters(analyser, args, language):
    analysis_data = None
    if args.get('type') == 'n-grams':
        analysis_data = __get_top_n_grams(analyser, args)
    if args.get('type') == 'readability':
        analysis_data = analyser.get_readability_score()
    if args.get('type') == 'tokens':
        analysis_data = __get_top_tokens(analyser, args)
    if args.get('type') == 'sentences':
        analysis_data = __to_sentence_list(analyser.get_sentences())
    if args.get('type') == 'lemmata':
        analysis_data = __to_tuple_list(analyser.get_lemmata())
    if args.get('type') == 'pos tags':
        analysis_data = __to_tuple_list(analyser.get_pos_tags())
    if args.get('type') == 'named entities':
        analysis_data = analyser.get_named_entities()
    return analysis_data

def analyse_selected_corpus(corpus, args, language):
    # setup
    analyser = CorpusAnalysis(language)
    texts = []
    analysis_data = {}

    for doc in corpus:
        texts.append(doc.get('text'))
    analyser.init_pipeline(texts)

    if args.get('type') == 'n-grams':
        analysis_data['n-grams'] = __get_top_n_grams(analyser, args)

    del analyser
    return analysis_data

def analyse_selected_doc(doc, args_list, language):
    # setup
    analyser = Analysis(language)
    analysis_data = {}
    analyser.init_pipeline(doc.get('text'))

    # analysis
    for args in args_list:
        analysis_data[args.get('type')] = __analyse_generic_parameters(analyser, args, language)
        if args.get('type') == 'similarity':
            other_analyser = Analysis(language)
            text = get_docs_by_value('celex', args.get('other celex'), language)[0].get('text')
            other_analyser.init_pipeline(text)
            analysis_data[args.get('type')] = analyser.get_document_cosine_similarity(other_analyser)
            del other_analyser

    del analyser
    return analysis_data

#-------------------
# test custom query
#-------------------
test_query = [
        # {
        #     "operator": "NOT",
        #     "search identifier": True,
        #     "column": "case_law_directory",
        #     "value": 'F'
        # },
        # {
        #     "operator" : "NOT",
        #     "search identifier": True,
        #     "column": 'applicant',
        #     "value": 'Person'
        # },
        {
            "column": 'celex',
            "value": ['61956CJ0007', '61958CJ0022', '61959CJ0025']
        },
        {
            "column": "date",
            "start date": "1958-07-17",
            "end date": "1959-07-17" 
        }
]
# 61956CJ0007 has cld = C and F
# 61958CJ0022 has cld not Fm applicant PART
# 61959CJ0025 has cld not F, applicant not PART
# cur = get_docs_by_custom_query(test_query,'en')
# print(len(list(cur)))
