import string
import re
import pickle
from collections import Counter

import gensim
import textstat

from blackstone.pipeline.sentence_segmenter import SentenceSegmenter
from blackstone.rules import CITATION_PATTERNS, CONCEPT_PATTERNS
import spacy
from spacy_iwnlp import spaCyIWNLP

# Older text (1956 - 2003) formats always got the same headlines - remove them from the text to get better results
english_legal_words = ["Summary", "Parties", "Subject of the case",
                       "Grounds", "Operative part", "Keywords", "Decision on costs"]
german_legal_words = ["Leitsätze", "Parteien", 'Schlüsselwörter', 'Entscheidungsgründe', 'Tenor', 'Kostenentscheidung']

class Analysis():
    # Maybe the text also should be an input parameter to better cache different calculations later on?
    # Eg. safe Analysis-Object for text selection 'A' and re-use it when necessary instead of recalculating everything
    def __init__(self, language):
        if(language != "en" and language != "de"):
            raise ValueError("Language not supported")
        else:
            self.language = language

        if self.language == "en":
            # python -m spacy download en_core_web_md
            # self.nlp = spacy.load("en_core_web_md") - uncomment this line to use a general model instead
            # pip install https://blackstone-model.s3-eu-west-1.amazonaws.com/en_blackstone_proto-0.0.1.tar.gz
            # Use Blackstone model which has been trained on english legal texts (https://github.com/ICLRandD/Blackstone)
            self.nlp = spacy.load("en_blackstone_proto")
            sentence_segmenter = SentenceSegmenter(self.nlp.vocab, CITATION_PATTERNS)
            self.nlp.add_pipe(sentence_segmenter, before="parser")
        else:
            # python -m spacy download de_core_news_md
            self.nlp = spacy.load("de_core_news_sm", disable = ["textcat"])
            iwnlp = spaCyIWNLP(lemmatizer_path='data/IWNLP.Lemmatizer_20181001.json', ignore_case = True)
            self.nlp.add_pipe(iwnlp)

        self.doc = None

    def __remove_punctuation(self, sentence):
        sentence = re.sub(r'[^\w\s\/]', '', sentence)
        return sentence

    # https://regex101.com/r/2AgRRW/2
    def __remove_paragraph_numbers(self, text):
        # Look for paragraph numbers in the new format
        return re.sub(r"(?i)(?<!(rt\.\s)|(bs\.\s)|(nr\.\s))(?<=[.’'\"]\s)(\d+\.*\s)(?=[A-Z])", "", text)

    def __remove_enumerations(self, text):
        return re.sub(r"(?<=\s)(\d\s?\.\s)", "", text)

    def __remove_legal_words(self, text):
        if self.language == "en":
            for word in english_legal_words:
                text = text.replace(word, "")
        else:
            for word in german_legal_words:
                text = text.replace(word, "")
        return text

    # https://regex101.com/r/iPVtVT/1 - improves tokenizer for older texts substantially
    def __remove_white_spaces_before_punctation(self, text):
        return re.sub(r"\s(?=\.)", "", text)

    # https://www.datacamp.com/community/tutorials/fuzzy-string-python
    # def __filter_text(self, document):
    #     paragraphs = ['title', 'keywords', 'parties', 'subject', 'grounds',
    #                   'decisions_on_costs', 'operative_part', 'endorsements']
    #     text = document['text'].strip()
    #     text_merged = ""
    #     for paragraph in paragraphs:
    #         if document[paragraph] is not None:
    #             text_merged += document[paragraph]
    #     # for paragraph in paragraphs:
    #     #     if document[paragraph] is not None:
    #     #         print(paragraph)
    #     #         print(fuzz.partial_ratio(document[paragraph], text))
    #     ratio = fuzz.token_sort_ratio(text_merged, text)
    #     if ratio < 90:
    #         return text
    #     else:
    #         text_merged = ""
    #         for paragraph in paragraphs[2:]:
    #             if document[paragraph] is not None:
    #                 text_merged += document[paragraph]
    #         return text_merged

    def init_pipeline(self, text):
        text = self.normalize(text)
        self.doc = self.nlp(text)

    def get_tokens(self, remove_punctuation=False, remove_stop_words=False):
        """Returns a list of all words present in the text."""
        if remove_stop_words:
            if remove_punctuation:
                tokens = [token.text for token in self.doc if token.is_punct != True and token.is_stop != True]
            else:
                tokens = [token.text for token in self.doc if token.is_stop != True]
        elif remove_punctuation:
            tokens = [token.text for token in self.doc if token.is_punct != True]
        else:
            tokens = [token.text for token in self.doc]
        return tokens

    def get_sentences(self):
        """
        Returns a list of all sentences present in the text. This objects can be iterated to get each token.
        """
        return list(self.doc.sents)

    def get_lemmas(self, remove_stop_words=True):
        """Returns a list of tuples with all base words and their lemmata"""
        lemmas = []
        for token in self.doc:
            if token.is_punct != True:
                if remove_stop_words:
                    if token.is_stop != True:
                        if self.language == "en":
                            lemmas.append((token, token.lemma_))
                        else:
                            if token._.iwnlp_lemmas is not None:
                                lemmas.append((token, token._.iwnlp_lemmas[0]))
                            else:
                                lemmas.append((token, token.lemma_))
                else:
                    if self.language == "en":
                        lemmas.append((token, token.lemma_))
                    else:
                        if token._.iwnlp_lemmas is not None:
                            lemmas.append((token, token._.iwnlp_lemmas[0]))
                        else:
                            lemmas.append((token, token.token_))
        return lemmas

    def get_pos_tags(self):
        """Returns a list of tuples with all base words and their part of speech tag"""
        pos = []
        for word in self.doc:
            pos.append((word, word.pos_))
        return pos

    def get_named_entities(self):
        ner = []
        labels = set([w.label_ for w in self.doc.ents])
        for label in labels:
            entities = [e.string for e in self.doc.ents if label == e.label_]
            entities = list(set(entities))
            ner.append((label, entities))
        return ner


    def get_token_count(self):
        """
        Gets all tokens including punctuation and stop words
        """
        return len(self.get_tokens(False, False))

    def get_word_count(self, remove_stop_words):
        """
        Gets all tokens excluding punctuation aka all words
        """
        return len(self.get_tokens(True, remove_stop_words))

    def get_most_frequent_words(self, remove_stop_words=True, lemmatize=True, n=10):
        if lemmatize:
            # Lemmatization is a good way to account for multiple variation of the same word
            lemmas = self.get_lemmas(remove_stop_words)
            tokens = [tupl[1] for tupl in lemmas]
        else:
            tokens = self.get_tokens(True, remove_stop_words)
        return Counter(tokens).most_common(n)

    def get_average_word_length(self, remove_stop_words):
        tokens = self.get_tokens(True, remove_stop_words)
        return sum(map(len, tokens)) / len(tokens)

    def get_document_cosine_similarity(self, other):
        """
        Calculate similarity for a whole document based on word embeddings. Expects an other initalized analysis object
        """
        return self.doc.similarity(other.doc)

    # TODO: Sentiment analysis (dynamic, if non-ML approach aka. dictionary), Co-occurrence (dynamic), diachronic analysis, judgment classification, inter-textuality

    # TODO: Remove header aka title and keywords to optimize tokenization:
    # Option 1: check whether text is the same if added together and remove keywords and title (header)
    # Option 2: check when first paragraph number appears and cut text from there (keywords also got paragraph numbers sometimes)
    # Option 3: tokenize title, keywords & whole text and remove tile and keyword tokens from main text (greedy aka only first one)

    def normalize(self, text):
        text = self.__remove_white_spaces_before_punctation(text)
        text = self.__remove_paragraph_numbers(text)
        text = self.__remove_legal_words(text)
        return text.lower()

    # Text-complexity (dynamic, Flesch-Kincaid reading ease formula (en & de supported))
    def readability_score(self, text):
        if self.language == "en":
            textstat.set_lang("en")
        else:
            textstat.set_lang("de")
        return textstat.flesch_reading_ease(text)

    # LDA (static)
    def prepare_text_for_lda(self, text):
        tokens = self.get_word_list(text)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [self.__get_lemma(token) for token in tokens]
        return tokens

    def generate_topic_models(self, text, topics=1):
        text_data = self.prepare_text_for_lda(text)
        dictionary = gensim.corpora.Dictionary(([text_data]))
        corpus = [dictionary.doc2bow(text) for text in [text_data]]
        lda_model = gensim.models.ldamodel.LdaModel(corpus, topics, dictionary, passes=15)
        topics = lda_model.print_topics()
        for topic in topics:
            print(topic)

# Deprecated code: to be removed in a future commit but still here if we need to revert

# def read_lemmata_from_tiger_corpus(tiger_corpus_file, valid_cols_n=15, col_words=1, col_lemmata=2):
#     lemmata_mapping = {}

#     with open(tiger_corpus_file) as f:
#         for line in f:
#             parts = line.split()
#             if len(parts) == valid_cols_n:
#                 w, lemma = parts[col_words], parts[col_lemmata]
#                 if w != lemma and w not in lemmata_mapping and not lemma.startswith('--'):
#                     lemmata_mapping[w] = lemma

#     return lemmata_mapping


# def train_german_pos_tagger():
#     """
#     Trains a supervised classificator with an accuracy of ~95%. Use with caution - takes time!
#     """

#     import nltk
#     corp = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09',
#                                          ['ignore', 'words', 'ignore', 'ignore', 'pos'],
#                                          encoding='utf-8')

#     import random

#     tagged_sents = list(corp.tagged_sents())
#     random.shuffle(tagged_sents)

#     # set a split size: use 90% for training, 10% for testing
#     split_perc = 0.1
#     split_size = int(len(tagged_sents) * split_perc)
#     train_sents, test_sents = tagged_sents[split_size:], tagged_sents[:split_size]

#     from ClassifierBasedGermanTagger import ClassifierBasedGermanTagger
#     tagger = ClassifierBasedGermanTagger(train=train_sents)

#     accuracy = tagger.evaluate(test_sents)

#     print(accuracy)

#     print(tagger.tag(['Das', 'ist', 'ein', 'einfacher', 'Test']))

#     with open('nltk_german_classifier_data.pickle', 'wb') as f:
#         pickle.dump(tagger, f)


# def train_punct_tokenzier(full_text, language='en'):
#     full_text = re.sub(r"\s(?=[^\w\s\/])", "", full_text)
#     tokenizer = PunktSentenceTokenizer(full_text)
#     if language == "en":
#         with open('nltk_english_sentence_classifer_data.pickle', 'wb') as f:
#             pickle.dump(tokenizer, f)
#     else:
#         with open('nltk_german_sentence_classifer_data.pickle', 'wb') as f:
#             pickle.dump(tokenizer, f)

