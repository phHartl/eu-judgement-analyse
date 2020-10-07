from collections import Counter
from mongo import *
from analysis import CorpusAnalysis

# Converted all API functions to class for faster processing. This way, the Analysis class doesn't need to load the models from disk on each api request.
# On systems with a lot of available memory both models can be kept in memory (about 2.5 GB of RAM per language) hence no switching (~10 seconds) would be needed
analysers = {
    "en": None,
    "de": None
}

def add_analyser(language):
    global analysers
    if language == "en" and not analysers.get("en"):
        print("Loading english models...")
        analysers["en"] = CorpusAnalysis("en")
    elif language == "de" and not analysers.get("de"):
        print("Loading german models")
        analysers["de"] = CorpusAnalysis("de")
    

def __get_top_occurrences(_list, limit=None):
    # create list with parsed strings because custom types like Token cannot be string compared
    string_list = []
    for item in _list:
        string_list.append(str(item))

    # count occurrences for every token
    # ensure type int to prevent crashing
    if isinstance(limit, int):
        occurrence_list = Counter(string_list).most_common(limit)
    else:
        occurrence_list = Counter(string_list).most_common()
    return occurrence_list

def __get_top_n_grams(analyser, args):
    # get n-grams
    n_grams = []
    if args.get('n'):
        n_grams = analyser.get_n_grams(n=args['n'])
    else:
        n_grams = analyser.get_n_grams()
    ngram_occurrences = __get_top_occurrences(n_grams, args.get('limit'))
    return ngram_occurrences

def __get_top_tokens(analyser, args):
    rem_punct = args.get('remove punctuation')
    rem_stopw = args.get('remove stop words')
    tokens = analyser.get_tokens(remove_punctuation = rem_punct,
                                remove_stop_words = rem_stopw)
    token_occurrences = __get_top_occurrences(tokens, args.get('limit'))
    return token_occurrences

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

def __run_analysis(analyser, args):
    analysis_data = None
    arg_type = args.get('type')

    if arg_type == 'n-grams':
        analysis_data = __get_top_n_grams(analyser, args)
    elif arg_type == 'average_readability':
        analysis_data = analyser.get_readability_score()
    elif arg_type == 'tokens':
        analysis_data = __get_top_tokens(analyser, args)
    elif arg_type == 'sentences':
        analysis_data = __to_sentence_list(analyser.get_sentences())
    elif arg_type == 'lemmata':
        analysis_data = __to_tuple_list(analyser.get_lemmata())
    elif arg_type == 'pos_tags':
        analysis_data = __to_tuple_list(analyser.get_pos_tags())
    elif arg_type == 'named_entities':
        analysis_data = analyser.get_named_entities()
    elif arg_type == 'sentence_count':
        analysis_data = len(analyser.get_sentences())
    elif arg_type == 'average_word_length':
        analysis_data = analyser.get_average_token_length(True, args.get('remove_stopwords'))
    elif arg_type == 'token_count':
        analysis_data = analyser.get_token_count()
    elif arg_type == 'word_count':
        analysis_data = analyser.get_token_count(True, args.get('remove_stopwords'))
    elif arg_type == 'most_frequent_words':
        analysis_data = analyser.get_most_frequent_words(args.get('remove_stopwords'),
            args.get('lemmatise'), args.get('limit'))
    elif arg_type == 'named_entities_per_doc':
        analysis_data = analyser.get_named_entities_per_doc()
    elif arg_type == 'average_readability':
        analysis_data = analyser.get_average_readability_score() 
    elif arg_type == 'sentences_per_doc':
        results = []
        for doc_result in analyser.get_sentences_per_doc():
            results.append(__to_sentence_list(doc_result))
        analysis_data = results
    elif arg_type == 'pos tags per doc':
        results = []
        for doc_result in analyser.get_pos_tags_per_doc():
            results.append(__to_tuple_list(doc_result))
        analysis_data = results
    elif arg_type == 'lemmata_per_doc':
        results = []
        for doc_result in analyser.get_lemmata_per_doc(args.get('remove_stopwords')):
            results.append(__to_tuple_list(doc_result))
        analysis_data = results
    elif arg_type == 'tokens_per_doc':
        results = []
        for doc_result in analyser.get_tokens_per_doc(args.get('remove_punctuation'),
            args.get('remove_stopwords')):
            results.append(__get_top_occurrences(doc_result))
        analysis_data = results

    return analysis_data

def analyse_corpus(corpus, args_list, language):
    global analysers
    if not analysers.get(language):
        add_analyser(language)
    
    texts = []
    analysis_data = {}

    for doc in corpus:
        texts.append(doc)
        if not doc.get('text'):
            print("No text found for: " + doc.get('celex'))

    analysis_types = []
    for args in args_list:
        analysis_types.append(args.get('type'))
    
    analysers[language].exec_pipeline(texts, pipeline_components = analysis_types)

    for args in args_list:
        arg_type = args.get('type')
        analysis_data[arg_type] = __run_analysis(analysers.get(language), args)

    # del analyser
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
