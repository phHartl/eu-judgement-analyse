from collections import Counter
from mongo import *
from analysis import Analysis, CorpusAnalysis

def __get_top_n_grams(analyser, args):
    # get n-grams
    n_grams = []
    if args.get('n'):
        n_grams = analyser.get_n_grams(n=args['n'])
    else:
        n_grams = analyser.get_n_grams()

    # find most frequent ones and return them
    for item in n_grams:
        item = str(item) # strings don't match unless explicitly cast

    top_ngrams = Counter(n_grams).most_common(args.get('limit'))
    return top_ngrams

def __get_top_tokens(analyser, args):
    tokens = analyser.get_tokens()
    return_limit = 50  # default: most frequent tokens returned
    if isinstance(args.get('tokens').get('limit'), int):
        return_limit = args.get('tokens').get('limit')
    top_tokens = Counter(tokens).most_common(return_limit)
    return top_tokens

# analysis for singular docs and whole corpora
def __get_specified_analysis(analyser, args):
    data = {}
    if args.get('type') == 'n-grams':
        data['n-grams'] = __get_top_n_grams(analyser, args)
    return data

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
    # analyser.init_pipeline(doc.get('text'))
    analysis_data = {}

    # if args.get('type') == 'n-grams':
    #     analysis_data['n-grams'] = __get_top_n_grams(analyser, args)
    # if args.get('type') == 'readability':
    #     analysis_data['readability score'] = analyser.get_readability_score()
    # if args.get('type') == 'tokens':
    #     analysis_data['tokens'] = __get_top_tokens(analyser, args)

    # del analyser
    return analysis_data

