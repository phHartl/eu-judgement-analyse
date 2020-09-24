import re
import pickle
from collections import Counter

import gensim
from fuzzywuzzy import fuzz
# install version 2.18
import spacy
from spacy_iwnlp import spaCyIWNLP
# install version 0.9.1 here (to avoid conflicts with blackstone)
import textacy
import textacy.ke
import textacy.vsm
# This library uses an older version of spacy (2.1.8)
from blackstone.pipeline.sentence_segmenter import SentenceSegmenter
from blackstone.rules import CITATION_PATTERNS

# Older text (1956 - 2003) formats always got the same headlines - remove them from the text to get better results
english_legal_words = ["Summary", "Parties", "Subject of the case",
                       "Grounds", "Operative part", "Keywords", "Decision on costs"]
german_legal_words = ["Leitsätze", "Parteien", 'Schlüsselwörter', 'Entscheidungsgründe', 'Tenor', 'Kostenentscheidung']

# Pre-processing methods

def __remove_punctuation(sentence):
    sentence = re.sub(r'[^\w\s\/]', '', sentence)
    return sentence

# https://regex101.com/r/2AgRRW/2

def __remove_paragraph_numbers(text):
    # Look for paragraph numbers in the new format
    return re.sub(r"(?i)(?<!(rt\.\s)|(bs\.\s)|(nr\.\s))(?<=[.’'\"]\s)(\d+\.*\s)(?=[A-Z])", "", text)


def __remove_enumerations(text):
    return re.sub(r"(?<=\s)(\d\s?\.\s)", "", text)


def __remove_legal_words(language, text):
    if language == "en":
        for word in english_legal_words:
            text = text.replace(word, "")
    else:
        for word in german_legal_words:
            text = text.replace(word, "")
    return text

# https://regex101.com/r/iPVtVT/1 - improves tokenizer for older texts substantially
def __remove_white_spaces_before_punctuation(text):
    return re.sub(r"\s(?=\.)", "", text)

# https://www.datacamp.com/community/tutorials/fuzzy-string-python - expects a document dict
def __filter_text(document):
    # The idea behind this function is to remove the messy header which is always present
    paragraphs = ['title', 'keywords', 'parties', 'subject', 'grounds',
                  'decisions_on_costs', 'operative_part', 'endorsements']
    text = document['text'].strip()
    text_merged = ""
    for paragraph in paragraphs:
        if document[paragraph] is not None:
            text_merged += document[paragraph]
    # for paragraph in paragraphs:
    #     if document[paragraph] is not None:
    #         print(paragraph)
    #         print(fuzz.partial_ratio(document[paragraph], text))
    ratio = fuzz.token_sort_ratio(text_merged, text)
    if ratio < 90:
        return text
    else:
        text_merged = ""
        for paragraph in paragraphs[2:]:
            if document[paragraph] is not None:
                text_merged += document[paragraph]
        return text_merged


def normalize(language, text):
    text = __remove_white_spaces_before_punctuation(text)
    text = __remove_paragraph_numbers(text)
    text = __remove_legal_words(language, text)
    return text.lower()

# TODO: Topic modeling (static, works basically but needs more parameter optimization aka running time) - on corpus basis,
# Sentiment analysis (dynamic, if non-ML approach aka. dictionary) - on document basis (average value for corpus),
# Co-occurrences for a corpus (dynamic),
# diachronic analysis (can be achieved by comparing different base stats of corpora),
# judgment classification (probably quite hard),
# inter-textuality (probably won't make it)


class CorpusAnalysis():
    """
    This class represents a state of analysis for a multiple texts (aka. a corpus). 
    Init with a language (en or de) and a list of texts.
    """

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
            self.nlp = textacy.load_spacy_lang("en_blackstone_proto", disable=("textcat"))
            # Use a custom sentence segmenter for better tokenization
            sentence_segmenter = SentenceSegmenter(self.nlp.vocab, CITATION_PATTERNS)
            self.nlp.add_pipe(sentence_segmenter, before="parser")
        else:
            # python -m spacy download de_core_news_md
            self.nlp = textacy.load_spacy_lang("de_core_news_md", disable=("textcat"))
            iwnlp = spaCyIWNLP(lemmatizer_path='data/IWNLP.Lemmatizer_20181001.json', ignore_case=True)
            self.nlp.add_pipe(iwnlp)

        self.corpus = None

    def init_pipeline(self, texts):
        """This function uses spaCy to initialize a processed corpus based on the input texts"""
        texts = [normalize(self.language, text) for text in texts]
        self.corpus = textacy.Corpus(self.nlp, data=texts)

    def get_tokens(self, remove_punctuation=False, remove_stop_words=False):
        """Returns a list of all tokens (if you exclude punctuation, it returns words instead)"""
        # Flatten per document list and return it
        return [item for sublist in self.get_tokens_per_doc(remove_punctuation,remove_stop_words) for item in sublist]

    def get_tokens_per_doc(self, remove_punctuation=False, remove_stop_words=False):
        """Returns a list of all tokens (if you exclude punctuation, it returns words instead) per document."""
        tokens = []
        for doc in self.corpus:
            tokens_per_doc = []
            for token in doc:
                if remove_stop_words:
                    if remove_punctuation:
                        if token.is_punct != True and token.is_stop != True:
                            tokens_per_doc.append(token)
                    else:
                        if token.is_stop != True:
                            tokens_per_doc.append(token)
                elif remove_punctuation:
                    if token.is_punct != True:
                        tokens_per_doc.append(token)
                else:
                    tokens_per_doc.append(token)
            tokens.append(tokens_per_doc)
        return tokens

    def get_sentences(self):
        """Returns all sentences present in the corpus"""
        return [item for sublist in self.get_sentences_per_doc() for item in sublist]

    def get_sentences_per_doc(self):
        """
        Returns all sentences present in the text grouped by document.
        """
        return [list(doc.sents) for doc in [doc for doc in self.corpus]]

    def get_sentence_count(self):
        return len(self.get_sentences())

    def get_average_word_length(self, remove_stop_words):
        tokens = self.get_tokens(True, remove_stop_words)
        return sum(map(len, tokens)) / len(tokens)

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

    def get_pos_tags(self):
        """Returns a list of tuples with all base words and their part of speech tag"""
        return [item for sublist in self.get_pos_tags_per_doc() for item in sublist]

    def get_pos_tags_per_doc(self):
        """Returns a list of tuples with all base words and their part of speech tag grouped by document"""
        pos = []
        for doc in self.corpus:
            pos.append([(word, word.pos_) for word in doc])
        return pos

    def get_lemmata_per_doc(self, remove_stop_words=True):
        """Returns a list of tuples with all base words and their lemmata grouped by document"""
        lemmata = []
        for doc in self.corpus:
            lemmata_per_doc = []
            for token in doc:
                if token.is_punct != True:
                    if remove_stop_words:
                        if token.is_stop != True:
                            if self.language == "en":
                                lemmata_per_doc.append((token, token.lemma_))
                            else:
                                if token._.iwnlp_lemmas is not None:
                                    lemmata_per_doc.append((token, token._.iwnlp_lemmas[0]))
                                else:
                                    lemmata_per_doc.append((token, token.lemma_))
                    else:
                        if self.language == "en":
                            lemmata_per_doc.append((token, token.lemma_))
                        else:
                            if token._.iwnlp_lemmas is not None:
                                lemmata_per_doc.append((token, token._.iwnlp_lemmas[0]))
                            else:
                                lemmata_per_doc.append((token, token.token_))
            lemmata.append(lemmata_per_doc)
        return lemmata

    def get_lemmata(self, remove_stop_words=True):
        """Returns a list of tuples with all base words and their lemmata"""
        return [item for sublist in self.get_lemmata_per_doc(remove_stop_words) for item in sublist]

    def get_named_entities(self):
        """Returns a list of tuples. Each contains an assigned label and all entities for this label"""
        ner = []
        labels = set([w.label_ for doc in self.corpus for w in doc.ents])
        for label in labels:
            entities = [e.string for doc in self.corpus for e in doc.ents if label == e.label_]
            entities = list(set(entities))
            ner.append((label, entities))
        return ner
    
    def get_named_entities_per_doc(self):
        """
        Returns a list of lists of tuples. 
        Each tuple contains an assigned label and all entities for this label in the corresponding document.
        """
        ner = []
        labels = set([w.label_ for doc in self.corpus for w in doc.ents])
        for doc in self.corpus:
            ner_per_doc = []
            for label in labels:
                entities = [e.string for e in doc.ents if label == e.label_]
                entities = list(set(entities))
                ner_per_doc.append((label, entities))
            ner.append(ner_per_doc)
        return ner

    def get_most_frequent_words(self, remove_stop_words=True, lemmatize=True, n=10):
        if lemmatize:
            # Lemmatization is a good way to account for multiple variation of the same word
            lemmata = self.get_lemmata(remove_stop_words)
            tokens = [tupl[1] for tupl in lemmata]
        else:
            tokens = self.get_tokens(True, remove_stop_words)
        return Counter(tokens).most_common(n)

    def get_average_readability_score(self):
        """
        Returns flesch reading ease score (different values for german & english!):
        English formula:
            https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
        German formula:
            https://de.wikipedia.org/wiki/Lesbarkeitsindex#Flesch-Reading-Ease
        """
        scores = []
        for doc in self.corpus:
            text_stats = textacy.TextStats(doc)
            scores.append(text_stats.flesch_reading_ease)
        return sum(scores) / len(scores)

    def get_n_grams(self, n=2, filter_stop_words=True, filter_nums=True, min_freq=5):
        """
        This functions returns all n-grams (e.g. n=2 (bigram) 'the court'). Should be used to analyse collocations.
        """
        return list(textacy.extract.ngrams(self.corpus, n, filter_stops=filter_stop_words, filter_punct=True, filter_nums=filter_nums, min_freq=min_freq))

        # LDA (static)
    # def prepare_text_for_lda(self):
    #     pos_tagged_tokens = self.get_pos_tags()
    #     tokens = [tupl[0] for tupl in pos_tagged_tokens if tupl[1] == "NOUN"]
    #     tokens = [token.text.strip() for token in tokens if len(token) > 3]
    #     # lemmata = self.get_pos_tags()
    #     # tokens = [tupl[1] for tupl in lemmata]
    #     return tokens

    # def compute_coherence_values(self, corpus, texts, dictionary, k, a, b):
    #     lda_model = gensim.models.LdaMulticore(corpus=corpus,
    #                                            id2word=dictionary,
    #                                            num_topics=k,
    #                                            random_state=100,
    #                                            chunksize=10,
    #                                            passes=10,
    #                                            alpha=a,
    #                                            eta=b,
    #                                            per_word_topics=True,
    #                                            workers=4)

    #     coherence_model_lda = gensim.models.CoherenceModel(
    #         model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')

    #     return coherence_model_lda.get_coherence()

    # def train_lda_parameters(self):
    #     import numpy as np
    #     import pandas as pd
    #     import tqdm
    #     tokens = []
    #     for doc in self.corpus:
    #         for token in doc:
    #             if not token.is_stop and not token.is_punct and (token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "ADJ") and len(token) > 3:
    #                 tokens.append(token.text)
    #     dictionary = gensim.corpora.Dictionary([d.split() for d in tokens])
    #     docs = []
    #     for doc in self.corpus:
    #         tokens_per_doc = []
    #         for token in doc:
    #             if not token.is_punct and not token.is_stop and (token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "ADJ") and len(token) > 3:
    #                 tokens_per_doc.append(token.text)
    #         docs.append(tokens_per_doc)
    #     corpus = [dictionary.doc2bow(text) for text in docs]
    #     grid = {}
    #     grid['Validation_Set'] = {}  # Topics range
    #     min_topics = 2
    #     max_topics = 11
    #     step_size = 1
    #     topics_range = range(min_topics, 150, 20)  # Alpha parameter
    #     alpha = list(np.arange(0.01, 1, 0.3))
    #     alpha.append('symmetric')
    #     alpha.append('asymmetric')  # Beta parameter
    #     beta = list(np.arange(0.01, 1, 0.3))
    #     beta.append('symmetric')  # Validation sets
    #     num_of_docs = len(corpus)
    #     corpus_sets = [  # gensim.utils.ClippedCorpus(corpus, num_of_docs*0.25),
    #         # gensim.utils.ClippedCorpus(corpus, num_of_docs*0.5),
    #         gensim.utils.ClippedCorpus(corpus, int(num_of_docs*0.75)),
    #         corpus]
    #     corpus_title = ['75% Corpus', '100% Corpus']
    #     model_results = {'Validation_Set': [],
    #                      'Topics': [],
    #                      'Alpha': [],
    #                      'Beta': [],
    #                      'Coherence': []
    #                      }
    #     # Can take a long time to run
    #     if 1 == 1:
    #         pbar = tqdm.tqdm(total=len(corpus_sets)*len(topics_range)*len(alpha)*len(beta))

    #         # iterate through validation corpuses
    #         for i in range(len(corpus_sets)):
    #             # iterate through number of topics
    #             for k in topics_range:
    #                 # iterate through alpha values
    #                 for a in alpha:
    #                     # iterare through beta values
    #                     for b in beta:
    #                         # get the coherence score for the given parameters
    #                         cv = self.compute_coherence_values(corpus=corpus_sets[i], dictionary=dictionary, texts=docs,
    #                                                            k=k, a=a, b=b)
    #                         # Save the model results
    #                         model_results['Validation_Set'].append(corpus_title[i])
    #                         model_results['Topics'].append(k)
    #                         model_results['Alpha'].append(a)
    #                         model_results['Beta'].append(b)
    #                         model_results['Coherence'].append(cv)

    #                         pbar.update(1)
    #         pd.DataFrame(model_results).to_csv('lda_tuning_results.csv', index=False)
    #         pbar.close()

    # def generate_topic_models(self, topics=100):
    #     tokens = []
    #     for doc in self.corpus:
    #         for token in doc:
    #             if not token.is_stop and not token.is_punct and (token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "ADJ") and len(token) > 3:
    #                 tokens.append(token.text)
    #     dictionary = gensim.corpora.Dictionary([d.split() for d in tokens])
    #     docs = []
    #     for doc in self.corpus:
    #         tokens_per_doc = []
    #         for token in doc:
    #             if not token.is_punct and not token.is_stop and (token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "ADJ") and len(token) > 3:
    #                 tokens_per_doc.append(token.text)
    #         docs.append(tokens_per_doc)
    #     corpus = [dictionary.doc2bow(text) for text in docs]
    #     # model_list, coherence_values = self.compute_coherence_values(dictionary=dictionary, corpus=corpus, texts=docs, limit=2000)
    #     # print("")
    #     lda_model = gensim.models.LdaMulticore(corpus, topics, dictionary, chunksize=5,
    #                                            alpha="symmetric", per_word_topics=True)
    #     coherence_model_lda = gensim.models.CoherenceModel(
    #         model=lda_model, texts=docs, dictionary=dictionary, coherence='c_v'
    #     )
    #     coherence_lda = coherence_model_lda.get_coherence()
    #     print(coherence_lda)
    #     topics = lda_model.print_topics()
    #     doc_lda = lda_model[corpus]
    #     for topic in topics:
    #         print(topic)


class Analysis(CorpusAnalysis):
    """
    This class represents a state of analysis for a single text. Init with a language (en or de) and the complete text.
    """

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
            self.nlp = textacy.load_spacy_lang("en_blackstone_proto")
            # Use a custom sentence segmenter for better tokenization
            # sentence_segmenter = SentenceSegmenter(self.nlp.vocab, CITATION_PATTERNS)
            # self.nlp.add_pipe(sentence_segmenter, before="parser")
        else:
            # python -m spacy download de_core_news_md
            self.nlp = textacy.load_spacy_lang("de_core_news_md", disable=("textcat"))
            iwnlp = spaCyIWNLP(lemmatizer_path='data/IWNLP.Lemmatizer_20181001.json', ignore_case=True)
            self.nlp.add_pipe(iwnlp)

        self.doc = None

    def init_pipeline(self, text):
        """Starts the NLP pipeline (https://miro.medium.com/max/700/1*tRJU9bFckl0uG5_wTR8Tsw.png) of spaCy"""
        text = normalize(self.language, text)
        self.doc = textacy.make_spacy_doc(text, lang=self.nlp)

    def get_tokens(self, remove_punctuation=False, remove_stop_words=False):
        """Returns a list of all tokens present in the text."""
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

    def get_lemmata(self, remove_stop_words=True):
        """Returns a list of tuples with all base words and their lemmata"""
        lemmata = []
        for token in self.doc:
            if token.is_punct != True:
                if remove_stop_words:
                    if token.is_stop != True:
                        if self.language == "en":
                            lemmata.append((token, token.lemma_))
                        else:
                            if token._.iwnlp_lemmas is not None:
                                lemmata.append((token, token._.iwnlp_lemmas[0]))
                            else:
                                lemmata.append((token, token.lemma_))
                else:
                    if self.language == "en":
                        lemmata.append((token, token.lemma_))
                    else:
                        if token._.iwnlp_lemmas is not None:
                            lemmata.append((token, token._.iwnlp_lemmas[0]))
                        else:
                            lemmata.append((token, token.token_))
        return lemmata

    def get_pos_tags(self):
        """Returns a list of tuples with all base words and their part of speech tag"""
        pos = []
        for word in self.doc:
            pos.append((word, word.pos_))
        return pos

    def get_named_entities(self):
        """Returns a list of tuples. Each contains an assigned label and all entities for this label"""
        ner = []
        labels = set([w.label_ for w in self.doc.ents])
        for label in labels:
            entities = [e.string for e in self.doc.ents if label == e.label_]
            entities = list(set(entities))
            ner.append((label, entities))
        return ner

    def get_document_cosine_similarity(self, other):
        """
        Calculate similarity for a whole document based on word embeddings. Expects an other initalized analysis object.
        """
        return self.doc.similarity(other.doc)

    def get_n_grams(self, n=2, filter_stop_words=True, filter_nums=True, min_freq=5):
        """
        This functions returns all n-grams (e.g. n=2 (bigram) 'the court'). Should be used to analyse collocations.
        """
        return list(textacy.extract.ngrams(self.doc, n, filter_stops=filter_stop_words, filter_punct=True, filter_nums=filter_nums, min_freq=min_freq))

    # Text-complexity (there are a few more metrics present if we want to also show them to the user)
    def get_readability_score(self):
        """
        Returns flesch reading ease score:
        English formula:
            https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
        German formula:
            https://de.wikipedia.org/wiki/Lesbarkeitsindex#Flesch-Reading-Ease
        """
        text_stats = textacy.TextStats(self.doc)
        return text_stats.flesch_reading_ease
