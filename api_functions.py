from collections import Counter
from mongo import *
from analysis import CorpusAnalysis

class Api():
    # Converted all API functions to class for faster processing. This way, the Analysis class doesn't need to load the models from disk on each api request.
    # On systems with a lot of available memory both models can be kept in memory (about 2.5 GB of RAM per language) hence no switching (~10 seconds) would be needed
    def __init__(self):
        self.english_analyser = None
        self.german_analyser = None
        self.analyser = None
    
    def setup_analyzer(self, language):
        if language == "en" and self.english_analyser is None:
            print("Loading english models...")
            self.english_analyser = CorpusAnalysis("en")
            self.german_analyser = None
            self.analyser = self.english_analyser
        elif language == "de" and self.german_analyser is None:
            print("Loading german models")
            self.german_analyser = CorpusAnalysis("de")
            self.english_analyser = None
            self.analyser = self.german_analyser
        

    def __get_top_occurrences(self,_list, limit=None):
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

    def __get_top_n_grams(self, analyser, args):
        # get n-grams
        n_grams = []
        if args.get('n'):
            n_grams = analyser.get_n_grams(n=args['n'])
        else:
            n_grams = analyser.get_n_grams()
        ngram_occurrences = self.__get_top_occurrences(n_grams, args.get('limit'))
        return ngram_occurrences

    def __get_top_tokens(self, analyser, args):
        rem_punct = args.get('remove punctuation')
        rem_stopw = args.get('remove stop words')
        tokens = analyser.get_tokens(remove_punctuation = rem_punct,
                                    remove_stop_words = rem_stopw)
        token_occurrences = self.__get_top_occurrences(tokens, args.get('limit'))
        return token_occurrences

    def __to_sentence_list(self, span_list):
        sentences = []
        for span in span_list:
            sentences.append(str(span))
        return sentences

    def __to_tuple_list(self, token_tuples):
        tuples = []
        for item in token_tuples:
            tuples.append((str(item[0]), str(item[1])))
        return tuples

    def __analyse_generic_parameters(self, analyser, args, language):
        analysis_data = None
        arg_type = args.get('type')
        if arg_type == 'n-grams':
            analysis_data = self.__get_top_n_grams(analyser, args)
        elif arg_type == 'readability':
            analysis_data = analyser.get_readability_score()
        elif arg_type == 'tokens':
            analysis_data = self.__get_top_tokens(analyser, args)
        elif arg_type == 'sentences':
            analysis_data = self.__to_sentence_list(analyser.get_sentences())
        elif arg_type == 'lemmata':
            analysis_data = self.__to_tuple_list(analyser.get_lemmata())
        elif arg_type == 'pos tags':
            analysis_data = self.__to_tuple_list(analyser.get_pos_tags())
        elif arg_type == 'named entities':
            analysis_data = analyser.get_named_entities()
        elif arg_type == 'sentence count':
            analysis_data = analyser.get_sentence_count()
        elif arg_type == 'average word length':
            analysis_data = analyser.get_average_word_length(args.get('remove stop words'))
        elif arg_type == 'token count':
            analysis_data = analyser.get_token_count()
        elif arg_type == 'word count':
            analysis_data = analyser.get_word_count(args.get('remove stop words'))
        elif arg_type == 'most frequent words':
            analysis_data = analyser.get_most_frequent_words(args.get('remove stop words'),
                args.get('lemmatise'), args.get('limit'))

        return analysis_data

    def analyse_corpus(self, corpus, args_list, language):
        
        if self.analyser is None:
            self.setup_analyzer(language)
        
        texts = []
        analysis_data = {}

        for doc in corpus:
            texts.append(doc.get('text'))
        self.analyser.exec_pipeline(texts)

        for args in args_list:
            arg_type = args.get('type')
            # generic analysis
            analysis_data[arg_type] = self.__analyse_generic_parameters(self.analyser, args, language)
            
            if analysis_data.get(arg_type):
                continue

            # corpus specific analysis
            if arg_type == 'tokens per doc':
                results = []
                for doc_result in self.analyser.get_tokens_per_doc(args.get('remove punctuation'),
                    args.get('remove stop words')):
                    results.append(self.__get_top_occurrences(doc_result))
                analysis_data[arg_type] = results
            elif arg_type == 'sentences per doc':
                results = []
                for doc_result in self.analyser.get_sentences_per_doc():
                    results.append(self.__to_sentence_list(doc_result))
                analysis_data[arg_type] = results
            elif arg_type == 'pos tags per doc':
                results = []
                for doc_result in self.analyser.get_pos_tags_per_doc():
                    results.append(self.__to_tuple_list(doc_result))
                analysis_data[arg_type] = results
            elif arg_type == 'lemmata per doc':
                results = []
                for doc_result in self.analyser.get_lemmata_per_doc(args.get('remove stop words')):
                    results.append(self.__to_tuple_list(doc_result))
                analysis_data[arg_type] = results
            elif arg_type == 'named entities per doc':
                analysis_data[arg_type] = self.analyser.get_named_entities_per_doc()
            elif arg_type == 'average readability':
                analysis_data[arg_type] = self.analyser.get_average_readability_score()

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
