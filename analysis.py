import re
import pickle
import math
from collections import Counter
import statistics
from joblib import Parallel, delayed
from functools import partialmethod, partial
from os import cpu_count

import gensim
# install version 2.1.8
import spacy
from spacy.util import minibatch
from spacy_iwnlp import spaCyIWNLP
# install version 0.9.1 here (to avoid conflicts with blackstone)
import textacy
import textacy.ke
import textacy.vsm
import textacy.tm
# This library uses an older version of spacy (2.1.8)
from blackstone.pipeline.sentence_segmenter import SentenceSegmenter
from blackstone.pipeline.compound_cases import CompoundCases
from blackstone.rules import CONCEPT_PATTERNS

import en_blackstone_proto
import de_core_news_md

import stanza

# Older text (1956 - 2003) formats always got the same headlines - remove them from the text to get better results
english_legal_words = ["Summary", "Parties", "Subject of the case",
                       "Grounds", "Operative part", "Keywords", "Decision on costs", "++"]
german_legal_words = ["Leitsätze", "Parteien", 'Schlüsselwörter',
                      'Entscheidungsgründe', 'Tenor', 'Kostenentscheidung', '++']

UNIVERSAL_POS_TAGS = ("ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
                      "PART", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X")

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

# https://regex101.com/r/5M9OWR/3/


def __remove_old_header_alt_language_pages(text):
    return re.sub(r"\w+\s((Sonderausgabe Seite)|(Ausgabe Seite)|(special edition Page)|(edition Page))\s\d+", "", text)

# https://regex101.com/r/iPVtVT/1 - improves tokenizer for older texts substantially


def __remove_white_spaces_before_punctuation(text):
    return re.sub(r"\s(?=\.)", "", text)


def __remove_white_spaces_before_parentheses(text):
    return re.sub(r"((?<=\w)\s(?=\)))|((?<=\()\s)", "", text)


def __remove_old_french_header_text(text):
    return re.sub(r"(Avis juridique important \|)\s\w+", "", text)


def normalize(language, text):
    """
    Pre-processes the legal texts, by removing typical messy data present. 

    Parameters
    ----------
    language : str
        either english (en) or german (de)
    text : str
        raw text data from eur-lex

    Returns
    -------
    str
        cleaned text
    """
    text = __remove_white_spaces_before_punctuation(text)
    text = __remove_white_spaces_before_parentheses(text)
    text = __remove_paragraph_numbers(text)
    text = __remove_legal_words(language, text)
    text = __remove_old_header_alt_language_pages(text)
    text = __remove_old_french_header_text(text)
    return text.lower().strip()

# TODO: Topic modeling (static, works basically but needs more parameter optimization aka running time) - on corpus basis,
# judgment classification (probably quite hard),


class CorpusAnalysis():
    """
    This class performs analysis for multiple texts in english (en) or german (de) (resp. a corpus).
    This class should only have static instances (aka one singleton per language) to prevent unnecessary pipeline setups,
    for each text individually. Execute the loaded pipeline for list of texts via exec_pipeline().

    Returns
    -------
    CorpusAnalysis
        instance of class

    Raises
    ------
    ValueError
        when an unsupported language is used
    """

    def __init__(self, language):
        if(language != "en" and language != "de"):
            raise ValueError("Language not supported")
        else:
            self.language = language

        if self.language == "en":
            # pip install https://blackstone-model.s3-eu-west-1.amazonaws.com/en_blackstone_proto-0.0.1.tar.gz
            # Use Blackstone model which has been trained on english legal texts (https://github.com/ICLRandD/Blackstone)
            self.nlp = textacy.load_spacy_lang("en_blackstone_proto", disable=("textcat"))
            if not ("sentence_segmenter" or "CompoundCases") in self.nlp.pipe_names:
                # Use a custom sentence segmenter for better tokenization
                sentence_segmenter = SentenceSegmenter(self.nlp.vocab, CONCEPT_PATTERNS)
                self.nlp.add_pipe(sentence_segmenter, before="parser")
                # https://github.com/ICLRandD/Blackstone#compound-case-reference-detection
                compound_pipe = CompoundCases(self.nlp)
                self.nlp.add_pipe(compound_pipe)
            else:
                print("Please only instantiate this class only once per language.")
            stanza.download("en", processors="tokenize, sentiment", logging_level="WARN")
            self.stanza_nlp = stanza.Pipeline(lang="en", processors="tokenize, sentiment",
                                              tokenize_pretokenized=True, logging_level="WARN")
        else:
            # python -m spacy download de_core_news_md
            self.nlp = textacy.load_spacy_lang("de_core_news_md", disable=("textcat"))
            # Textacy caches loaded pipeline components. So do not add them again if they are already present.
            if not ("sentence_segmenter" or "spacyiwnlp") in self.nlp.pipe_names:
                iwnlp = spaCyIWNLP(lemmatizer_path='data/IWNLP.Lemmatizer_20181001.json', ignore_case=True)
                self.nlp.add_pipe(iwnlp)
                sentence_segmenter = SentenceSegmenter(self.nlp.vocab, CONCEPT_PATTERNS)
                self.nlp.add_pipe(sentence_segmenter, before="parser")
            else:
                print("Please only instantiate this class only once per language.")
            stanza.download("de", processors="tokenize, sentiment", logging_level="WARN")
            self.stanza_nlp = stanza.Pipeline(lang="de", processors="tokenize, sentiment",
                                              tokenize_pretokenized=True, logging_level="WARN")

        self.corpus = None

    def exec_pipeline(self, texts, pipeline_components, normalize_texts=True):
        """
        Starts the NLP pipeline (https://miro.medium.com/max/700/1*tRJU9bFckl0uG5_wTR8Tsw.png) of spaCy defined in the constructor for a corpus.

        Parameters
        ----------
        texts : List[Dict]
            Expects a list of document dicts with their meta data
        pipeline_components : List[str]
            List of analysis types to consider for this pipeline
        normalize : bool, optional
            whether to clean the texts before processing, by default True (should only be false for debugging purposes)
        """

        self.corpus = textacy.Corpus(self.nlp)
        with self.nlp.disable_pipes(*self._remove_unused_components(pipeline_components)):
            partitions = minibatch(texts, math.ceil(len(texts) / cpu_count()))
            executor = Parallel(n_jobs=-1, require="sharedmem", prefer="threads")
            do = delayed(partial(self._exec_pipeline_for_sub_corpus, normalize_texts))
            tasks = (do(i, batch) for i, batch in enumerate(partitions))
            sub_corpora = executor(tasks)
            self.corpus.add_docs([doc for corpus in sub_corpora for doc in corpus])

    def _remove_unused_components(self, pipeline_components):
        # Internal function to remove unused pipeline components for the current analysis.
        # Saves memory and reduces calculation time.
        disabled_components = []
        if not any(component in pipeline_components for component in ("named_entities", "named_entities_per_doc")):
            disabled_components.append("ner")
            if self.language == "en":
                disabled_components.append("merge_entities")
                disabled_components.append("CompoundCases")
        if not any(component in pipeline_components for component in ("tokens", "token_count", "word_count", "average_token_length", "average_word_length",
                                                                      "most_frequent_words", "most_frequent_words_per_doc", "tokens_per_doc", "pos_tags", 
                                                                      "pos_tags_per_doc", "lemmata", "lemmata_per_doc", "unique_tokens", 
                                                                      "unique_tokens_per_doc", "keywords", "keywords_per_doc")):
            disabled_components.append("tagger")
            if self.language == "de":
                disabled_components.append("spaCyIWNLP")

        if not any(component in pipeline_components for component in ("sentences", "sentences_per_doc", "sentence_count")):
            if self.language == "de":
                if not any(component in pipeline_components for component in ("readability", "readability_per_doc")):
                    disabled_components.append("parser")
            else:
                disabled_components.append("parser")
        return disabled_components

    def _exec_pipeline_for_sub_corpus(self, normalize_texts, batch_id, docs):
        # Internal function to enable multi-threaded pipeline execution
        sub_corpus = textacy.Corpus(self.nlp)
        for doc in docs:
            if doc['text']:
                if normalize_texts:
                    spacy_doc = textacy.make_spacy_doc(
                        (normalize(self.language, doc['text']), {'celex': doc['celex']}), self.nlp)
                else:
                    spacy_doc = textacy.make_spacy_doc(doc['text'], {'celex': doc['celex']}, self.nlp)
                sub_corpus.add_doc(spacy_doc)
        return sub_corpus

    def get_celex_numbers(self):
        """
        Returns a list of celex numbers

        Returns
        -------
        List[str]
            list of ordered celex numbers as present in the corpus
        """
        return [doc._.meta['celex'] for doc in self.corpus]

    def get_tokens(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Returns a list of all tokens in the corpus.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tokens)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        List[str]
            a customizable list of all tokens in the corpus (if you exclude punctuation, it returns words instead).
        """
        # Flatten per document list and return it
        return [item for sublist in self.get_tokens_per_doc(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq_per_doc) for item in sublist]

    def get_tokens_per_doc(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Returns a list of all tokens in the corpus grouped by document.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        List[str]
            Returns a customizable list of all tokens in the corpus per document (if you exclude punctuation, it returns words instead).
        """
        if include_pos is None:
            include_pos = UNIVERSAL_POS_TAGS
        if exclude_pos is not None:
            include_pos = [pos_tag for pos_tag in include_pos if pos_tag not in exclude_pos]
        tokens = []
        for doc in self.corpus:
            tokens_per_doc = []
            for token in doc:
                if remove_stopwords:
                    if remove_punctuation:
                        if token.is_punct != True and token.is_stop != True and token.is_space != True:
                            tokens_per_doc.append(token)
                    else:
                        if token.is_stop != True and token.is_space != True:
                            tokens_per_doc.append(token)
                elif remove_punctuation:
                    if token.is_punct != True and token.is_space != True:
                        tokens_per_doc.append(token)
                else:
                    if token.is_space != True:
                        tokens_per_doc.append(token)
            tokens_per_doc = [token.text for token in tokens_per_doc if token.pos_ in include_pos]
            if min_freq_per_doc != 1:
                tokens_to_filter = [key for key, value in Counter(tokens_per_doc).items() if value >= min_freq_per_doc]
                tokens_per_doc = [token for token in tokens_per_doc if token not in tokens_to_filter]
            tokens.append(tokens_per_doc)
        return tokens

    def get_unique_tokens(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Returns a list of all unique tokens in the corpus.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        Set[str]
            a customizable set of all unique tokens in the corpus (if you exclude punctuation, it returns words instead).
        """
        return list(set(self.get_tokens(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq_per_doc)))

    def get_unique_tokens_per_doc(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Returns a list of all unique tokens in the corpus.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        Set[str]
            a customizable set of all unique tokens in the corpus grouped by document (if you exclude punctuation, it returns words instead).
        """
        return [list(set(doc)) for doc in self.get_tokens_per_doc(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq_per_doc)]

    def get_sentences(self):
        """
        Returns all sentences present in the corpus

        Returns
        -------
        List[Spacy.span]
            a list of all sentencens in the corpus. Can be transferred to string by using .text for each element
        """
        return [item for sublist in self.get_sentences_per_doc() for item in sublist]

    def get_sentences_per_doc(self):
        """
        Returns all sentences present in the corpus grouped by document.

        Returns
        -------
        List of lists of sentences
            a list of all sentencens in the corpus by document
        """
        return [list(doc.sents) for doc in [doc for doc in self.corpus]]

    def get_sentence_count_per_doc(self):
        """
        Calculates the amount of sentences present in the corpus. Shortcut for len(self.get_sentences())

        Returns
        -------
        List[int]
            quantity of sentences in the corpus
        """
        return [len(list(doc.sents)) for doc in [doc for doc in self.corpus]]

    def get_average_token_length(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq=1):
        """
        Calculates the mean token length in the corpus in dependence of various filters. Acts as a wrapper for get_tokens()

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        float
            average token length
        """
        tokens = self.get_tokens(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq)
        return sum(map(len, tokens)) / len(tokens)

    def get_token_count(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Calculates the amount of tokens present in the text.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1

        Returns
        -------
        int
            quantity of tokens in the corpus
        """
        return len(self.get_tokens(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq_per_doc))

    def get_token_count_per_doc(self, remove_punctuation=False, remove_stopwords=False, include_pos=None, exclude_pos=None, min_freq_per_doc=1):
        """
        Calculates the amount of tokens present in the text grouped by document.

        Parameters
        ----------
        remove_punctuation : bool, optional
            whether to remove punctuation, by default False
        remove_stopwords : bool, optional
            whether to remove stop words, by default False
        include_pos : tuple/list(str), optional
            part of speech tags which should be included, by default None (defaults to all tags)
        exclude_pos : tuple/list(str), optional
            part of speech tags which should be excluded, by default None
        min_freq_per_doc : int, optional
            min token frequency per document, by default 1:

        Returns
        -------
        List[int]
            quantity of tokens in the corpus grouped by document
        """
        return [len(doc) for doc in self.get_tokens_per_doc(remove_punctuation, remove_stopwords, include_pos, exclude_pos, min_freq_per_doc)]

    def get_pos_tags(self, include_pos=None, exclude_pos=None):
        """
        Gets all part of speech tags for the corpus.

        Returns
        -------
        List[Tuple[str, str]]
            a list of tuples with the base word and its part of speech tag
        """
        return [item for sublist in self.get_pos_tags_per_doc(include_pos, exclude_pos) for item in sublist]

    def get_pos_tags_per_doc(self, include_pos=None, exclude_pos=None):
        """
        Gets all part of speech tags for each for grouped by document.

        Returns
        -------
        List[List[Tuple(str, str)]]
            a list of list of tuples with all base words and their part of speech tag grouped by document
        """
        pos = []
        if include_pos is None:
            include_pos = UNIVERSAL_POS_TAGS
        if exclude_pos is not None:
            include_pos = [pos_tag for pos_tag in include_pos if pos_tag not in exclude_pos]
        for doc in self.corpus:
            pos.append([(word, word.pos_) for word in doc if word.pos_ in include_pos])
        return pos

    def get_lemmata_per_doc(self, remove_stopwords=True, include_pos=None, exclude_pos=None):
        """
        Gets all lemmata of each word present in the corpus grouped by document.

        Parameters
        ----------
        remove_stopwords : bool, optional
            whether stop words should be removed, by default True
        include_pos : List|Tuple, optional
            which part of speech tags should be kept, by default None (defaults to all tags)
        exclude_pos : List|Tuple, optional
            which part of speech tags should be removed, by default None

        Returns
        -------
        List[List[Tuple[str, str]]]
            list of tuples with base word and its lemma grouped by document
        """
        lemmata = []
        if include_pos is None:
            include_pos = UNIVERSAL_POS_TAGS
        if exclude_pos is not None:
            include_pos = [pos_tag for pos_tag in include_pos if pos_tag not in exclude_pos]
        for doc in self.corpus:
            lemmata_per_doc = []
            for token in doc:
                if token.is_punct != True and token.is_space != True and token.pos_ in include_pos:
                    if remove_stopwords:
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
                                lemmata_per_doc.append((token, token.lemma_))
            lemmata.append(lemmata_per_doc)
        return lemmata

    def get_lemmata(self, remove_stopwords=True, include_pos=None, exclude_pos=None):
        """
        Gets all lemmata of each word present in the corpus.

        Parameters
        ----------
        remove_stopwords : bool, optional
            whether stop words should be removed, by default True
        include_pos : List|Tuple, optional
            which part of speech tags should be kept, by default None (defaults to all tags)
        exclude_pos : List|Tuple, optional
            which part of speech tags should be removed, by default None

        Returns
        -------
        List[Tuple[str, str]]
            list of tuples with base word and its lemma for the whole corpus
        """
        return [item for sublist in self.get_lemmata_per_doc(remove_stopwords, include_pos, exclude_pos) for item in sublist]

    def get_named_entities(self):
        """
        Calculates all named entities in the text and groups them by assigned label.

        Returns
        -------
        List[Tuple[str, List[str]]]
            list of tuples, each tuple contains an assigned label and all entities for this label
        """
        ner = []
        labels = set([w.label_ for doc in self.corpus for w in doc.ents])
        for label in labels:
            entities = [e.string for doc in self.corpus for e in doc.ents if label == e.label_]
            entities = list(set(entities))
            ner.append((label, entities))
        compound_cases = [compound_case for doc in self.corpus for compound_case in doc._.compound_cases]
        if len(compound_cases) > 0:
            ner.append(("COMPOUND_CASES", compound_cases))
        return ner

    def get_named_entities_per_doc(self):
        """
        Calculates all named entities in the text and groups them by assigned label and document.

        Returns
        -------
        List[List[Tuple[str, List[str]]]]
            list of documents, each containing a list of tuples, each tuple contains an assigned label and all entities for this label
        """
        ner = []
        labels = set([w.label_ for doc in self.corpus for w in doc.ents])
        for doc in self.corpus:
            ner_per_doc = []
            for label in labels:
                entities = [e.string for e in doc.ents if label == e.label_]
                entities = list(set(entities))
                ner_per_doc.append((label, entities))
            compound_cases = [compound_case for compound_case in doc._.compound_cases]
            if len(compound_cases) > 0:
                ner_per_doc.append(("COMPOUND_CASES", compound_cases))
            ner.append(ner_per_doc)
        return ner

    def get_most_frequent_words(self, remove_stopwords=True, lemmatize=True, n=10):
        """
        Calculates the most frequent words in the corpus/document.

        Parameters
        ----------
        remove_stopwords : bool, optional
            whether stop words should be removed, by default True
        lemmatize : bool, optional
            whether all words should be lemmatized before calculation, by default True
        n : int, optional
            top n words, by default 10

        Returns
        -------
        List[Tuple[str, int]]
            List of tuples - each word with its occurrence count
        """
        if lemmatize:
            # Lemmatization is a good way to account for multiple variation of the same word
            lemmata = self.get_lemmata(remove_stopwords)
            tokens = [tupl[1] for tupl in lemmata]
        else:
            tokens = self.get_tokens(True, remove_stopwords)
        return Counter(tokens).most_common(n)

    def get_most_frequent_words_per_doc(self, remove_stopwords=True, lemmatize=True, n=10):
        """
        Calculates the most frequent words in the corpus/document.

        Parameters
        ----------
        remove_stopwords : bool, optional
            whether stop words should be removed, by default True
        lemmatize : bool, optional
            whether all words should be lemmatized before calculation, by default True
        n : int, optional
            top n words per document, by default 10

        Returns
        -------
        List[List[Tuple[str, int]]]
            List of tuples - each word with its occurrence count grouped by document
        """
        if lemmatize:
            # Lemmatization is a good way to account for multiple variation of the same word
            lemmata = self.get_lemmata_per_doc(remove_stopwords)
            tokens_per_doc = []
            for doc in lemmata:
                tokens = []
                for tupl in doc:
                    tokens.append(tupl[1])
                tokens_per_doc.append(tokens)
        else:
            tokens_per_doc = self.get_tokens_per_doc(True, remove_stopwords)
        return [Counter(doc).most_common(n) for doc in tokens_per_doc]

    def get_readability_score_per_doc(self):
        """
        Calculates the flesch reading ease score (different values for german & english!) for each document:
        English formula:
            https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
        German formula:
            https://de.wikipedia.org/wiki/Lesbarkeitsindex#Flesch-Reading-Ease

        Returns
        -------
        List[float]
            all scores for each document
        """
        return [textacy.TextStats(doc).flesch_reading_ease for doc in self.corpus]

    def get_readability_score(self):
        """
        Calculates the flesch reading ease score (different values for german & english!):
        English formula:
            https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
        German formula:
            https://de.wikipedia.org/wiki/Lesbarkeitsindex#Flesch-Reading-Ease

        Returns
        -------
        float
            the mean score for each document in the corpus.
        """
        return statistics.mean(self.get_readability_score_per_doc())

    def get_n_grams(self, n=2, filter_stop_words=True, filter_nums=True, min_freq=5):
        """
        This functions calculates a set of all n-grams (e.g. n=2 (bigram) 'the court').
        This corresponds to simple word collocations in the corpus.

        Parameters
        ----------
        n : int, optional
            type of n-gram to calculate, by default 2 (bigram)
        filter_stop_words : bool, optional
            whether stop words should be removed, by default True
        filter_nums : bool, optional
            whether numerics should be removed, by default True
        min_freq : int, optional
            minimum occurrence in the corpus, by default 5

        Returns
        -------
        List[str]
            of all n-grams.
        """
        merged_text = ""
        for doc in self.corpus:
            merged_text += doc.text
        doc = None
        with self.nlp.disable_pipes("tagger", "parser", "ner"):
            self.nlp.max_length = 100000000
            doc = self.nlp(merged_text)
        return list([token.text for token in textacy.extract.ngrams(doc, n, filter_stops=filter_stop_words, filter_punct=True, filter_nums=filter_nums, min_freq=min_freq)])

    def get_n_grams_per_doc(self, n=2, filter_stop_words=True, filter_nums=True, min_freq_per_doc=2):
        """
        This functions calculates a set of all n-grams (e.g. n=2 (bigram) 'the court').
        This corresponds to simple word collocations in the corpus.

        Parameters
        ----------
        n : int, optional
            type of n-gram to calculate, by default 2 (bigram)
        filter_stop_words : bool, optional
            whether stop words should be removed, by default True
        filter_nums : bool, optional
            whether numerics should be removed, by default True
        min_freq_per_doc : int, optional
            minimum occurrence in the corpus, by default 5

        Returns
        -------
        List[List[str]]
            of all n-grams grouped by document
        """
        n_grams_per_doc = []
        for doc in self.corpus:
            n_grams = list([token.text for token in textacy.extract.ngrams(
                doc, n, filter_stops=filter_stop_words, filter_punct=True, filter_nums=filter_nums, min_freq=min_freq_per_doc)])
            n_grams_per_doc.append(n_grams)
        return n_grams_per_doc

    def get_sentiment(self):
        """
        Uses a CNN (https://arxiv.org/abs/1408.5882) to classify the sentiment of each sentence.
        This might take a little longer on slower systems. 
        0 - negative, 1 - neutral, 2 - positive sentiment (https://stanfordnlp.github.io/stanza/sentiment.html)

        Returns
        -------
        int
            a normalized sentiment value for the whole corpus (median)
        """
        return int(statistics.median([sentiment for doc in self._get_sentiment_per_doc_and_sentence() for sentiment in doc]))

    def get_sentiment_per_doc(self):
        """
        Uses a CNN (https://arxiv.org/abs/1408.5882) to classify the sentiment of each sentence.
        This might take a little longer on slower systems. 
        0 - negative, 1 - neutral, 2 - positive sentiment (https://stanfordnlp.github.io/stanza/sentiment.html)

        Returns
        -------
        List[int]
            of normalized sentiment values (median) for each document in the corpus
        """
        return [int(statistics.median(doc)) for doc in self._get_sentiment_per_doc_and_sentence()]

    def _get_sentiment_per_doc_and_sentence(self):
        # This function pre-processes the corpus data so it is in the right format for stanza
        sentences_per_doc = self.get_sentences_per_doc()
        stanza_docs = []
        for doc in sentences_per_doc:
            temp_sentences = []
            for sentence in doc:
                temp_tokens = []
                for token in sentence:
                    temp_tokens.append(token.text)
                temp_sentences.append(temp_tokens)
            stanza_docs.append(temp_sentences)
        docs = [self.stanza_nlp(doc) for doc in stanza_docs]
        sentiment_per_doc = []
        for doc in docs:
            sentiment = []
            for sentence in doc.sentences:
                sentiment.append(sentence.sentiment)
            sentiment_per_doc.append(sentiment)
        return sentiment_per_doc

    def get_document_cosine_similarity(self):
        """
        Calculate similarity for two documents based on their word embeddings.

        Returns
        -------
        float
            vector cosine similarity

        Raises
        ------
        ValueError
            when the corpus has not two but any other number of documents
        """
        if self.corpus.n_docs != 2:
            raise ValueError("Document vector similarity only makes sense on two single documents")
        return self.corpus[0].similarity(self.corpus[1])

    def get_keywords(self, top_n=10):
        """
        We use PositionRank (a biased PageRank algorithm) to compute the keywords for documents.
        We do this, because european judgments start with a keyword section (similar to an Abstract in research papers, which this algorithm was optimized for).
        https://www.aclweb.org/anthology/P17-1102.pdf

        Parameters
        ----------
        top_n : int, optional
            top n keywords, by default 10

        Returns
        -------
        List[Tuple[str, int]]
            of tuples with keyterms and their corresponding weight

        Raises
        ------
        NotImplementedError
            when corpus length is greater than one, because this method is not suited for multiple documents at once
        """
        if self.corpus.n_docs != 1:
            raise NotImplementedError(
                "Keyword extraction does not work for the whole corpus. Use get_keywords_per_doc() instead.")
        return textacy.ke.textrank(self.corpus[0], normalize=self._get_single_lemma, window_size=10, edge_weighting="count", position_bias=True, topn=top_n)

    def get_keywords_per_doc(self, top_n=10):
        """
         We use PositionRank (a biased PageRank algorithm) to compute the keywords for documents.
        We do this, because european judgments start with a keyword section (similar to an Abstract in research papers, which this algorithm was optimized for).
        https://www.aclweb.org/anthology/P17-1102.pdf

        Parameters
        ----------
        top_n : int, optional
            top n keywords, by default 10

        Returns
        -------
        List[List[Tuple[str, int]]]
            A list of documents with their list of tuples of keyterms and weight
        """
        keywords = [textacy.ke.textrank(doc, normalize=self._get_single_lemma, window_size=10,
                                        edge_weighting="count", position_bias=True, topn=top_n) for doc in self.corpus]
        return keywords

    def _get_single_lemma(self, spacy_token):
        # This function returns the lemma for a single token
        if self.language == "de":
            if spacy_token._.iwnlp_lemmas is not None:
                return spacy_token._.iwnlp_lemmas[0]
        return spacy_token.lemma_

    # # LDA (static)
    # def prepare_text_for_lda(self):
    #     pos_tagged_tokens = self.get_pos_tags()
    #     tokens = [tupl[0] for tupl in pos_tagged_tokens if tupl[1] == "NOUN"]
    #     tokens = [token.text.strip() for token in tokens if len(token) > 3]
    #     # lemmata = self.get_pos_tags()
    #     # tokens = [tupl[1] for tupl in lemmata]
    #     return tokens

    # def compute_coherence_values_(self, corpus, texts, dictionary, k, a, b):
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
    #     min_topics = 10
    #     max_topics = 15
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

    # def make_bigrams(self, docs, bigram_mod):
    #     return [bigram_mod[doc] for doc in docs]

    # def make_trigrams(self, docs, trigram_mod, bigram_mod):
    #     return [trigram_mod[bigram_mod[doc]] for doc in docs]

    # def generate_topic_models(self, topics=10):
    #     # Build the bigram and trigram models
    #     tokens_per_doc = []
    #     for doc in self.get_lemmata_per_doc(True, include_pos=("NOUN", "ADJ", "VERB", "ADV")):
    #         tokens = []
    #         for tupl in doc:
    #             tokens.append(tupl[1])
    #         tokens_per_doc.append(tokens)
    #     bigram = gensim.models.Phrases(tokens_per_doc, min_count=5, threshold=10)
    #     trigram = gensim.models.Phrases(bigram[tokens_per_doc], threshold=10)

    #     # Faster way to get a sentence clubbed as a trigram/bigram
    #     bigram_mod = gensim.models.phrases.Phraser(bigram)
    #     trigram_mod = gensim.models.phrases.Phraser(trigram)

    #     tokens_bigrams = self.make_trigrams(tokens_per_doc, trigram_mod, bigram_mod)

    #     id2word = gensim.corpora.Dictionary(tokens_bigrams)
    #     docs = tokens_bigrams
    #     corpus = [id2word.doc2bow(text) for text in docs]
    #     # model_list, coherence_values = self.compute_coherence_values(id2word,corpus,docs,200,50,10)
    #     # print("")
    #     # lda_model = gensim.models.wrappers.LdaMallet('data/mallet-2.0.8/bin/mallet',corpus, num_topics=topics, id2word=id2word)
    #     # coherence_model_lda = gensim.models.CoherenceModel(
    #     #     model=lda_model, texts=docs, dictionary=id2word, coherence='c_v'
    #     # )
    #     # coherence_lda = coherence_model_lda.get_coherence()
    #     # print(coherence_lda)
    #     # topics = lda_model.print_topics()
    #     # doc_lda = lda_model[corpus]
    #     # for topic in topics:
    #     #     print(topic)

    # def compute_coherence_values(self, dictionary, corpus, texts, limit, start=2, step=3):
    #     """
    #     Compute c_v coherence for various number of topics

    #     Parameters:
    #     ----------
    #     dictionary : Gensim dictionary
    #     corpus : Gensim corpus
    #     texts : List of input texts
    #     limit : Max num of topics

    #     Returns:
    #     -------
    #     model_list : List of LDA topic models
    #     coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    #     """
    #     coherence_values = []
    #     model_list = []
    #     for num_topics in range(start, limit, step):
    #         model = gensim.models.wrappers.LdaMallet(
    #             "data/mallet-2.0.8/bin/mallet", corpus=corpus, id2word=dictionary, num_topics=num_topics)
    #         model_list.append(model)
    #         coherencemodel = gensim.models.CoherenceModel(
    #             model=model, texts=texts, dictionary=dictionary, coherence='c_v')
    #         coherence_values.append(coherencemodel.get_coherence())

    #     return model_list, coherence_values
