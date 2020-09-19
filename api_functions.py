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

def generate_subcorpus(corpus_args):
    pass

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