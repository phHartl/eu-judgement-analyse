import string
import re

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.text import Text
from nltk import pos_tag, FreqDist
import gensim
import textstat

english_stop_words = list(set(stopwords.words("english")))
german_stop_words = list(set(stopwords.words("german")))


class Analysis():

    # Maybe the text also should be an input parameter to better cache different calculations later on?
    # Eg. safe Analysis-Object for text selection 'A' and re-use it when necessary instead of recalculating everything
    def __init__(self, language):
        if(language != "en" and language != "de"):
            raise ValueError("Language not supported")
        else:
            self.language = language

    def set_lang(self, language):
        """
        Used to switch language when necessary (should almost never be the case).
        """
        if(language != "en" and language != "de"):
            pass
        else:
            self.language = language

    def __remove_punctuation(self, sentence):
        sentence = re.sub(r'[^\w\s]', '', sentence)
        return sentence

    def __remove_stopwords(self, sentence):
        if self.language == "en":
            return [w for w in sentence if not w.lower() in english_stop_words]
        return [w for w in sentence if not w.lower() in german_stop_words]

    def tokenize(self, text):
        sentences = sent_tokenize(text)
        cleaned_sentences = [self.__remove_punctuation(sentence) for sentence in sentences]
        sentences_word_tokenized = [word_tokenize(sentence) for sentence in cleaned_sentences]
        sentences_tokenized_filtered = [self.__remove_stopwords(sentence) for sentence in sentences_word_tokenized]
        return sentences_tokenized_filtered

    def part_of_speech_tagging(self, text):
        tokenized_text = self.tokenize(text)
        pos = [pos_tag(tokenized_sentence) for tokenized_sentence in tokenized_text]
        return pos

    def get_word_list(self, text):
        """Returns a list of all words present in the text."""
        tokenized_text = self.tokenize(text)
        # Flatten the resulting array
        word_list = [item for sublist in tokenized_text for item in sublist]
        return word_list

    def get_lemma(self, word):
        lemma = wordnet.morphy(word)
        if lemma is None:
            return word
        else:
            return lemma

    def get_lemma2(self, word):
        return WordNetLemmatizer().lemmatize(word)

    def most_frequent_words(self, text, n=10):
        tokens = self.get_word_list(text)
        return FreqDist(tokens).most_common(n)

    def average_word_length(self, text):
        tokens = self.get_word_list(text)
        return sum(map(len, tokens)) / len(tokens)

    # TODO: Sentiment analysis (dynamic, if non-ML approach aka. dictionary), Co-occurrence (dynamic)

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
        tokens = [self.get_lemma2(token) for token in tokens]
        return tokens

    def generate_topic_models(self, text, topics=1):
        text_data = self.prepare_text_for_lda(text)
        dictionary = gensim.corpora.Dictionary(([text_data]))
        corpus = [dictionary.doc2bow(text) for text in [text_data]]
        lda_model = gensim.models.ldamodel.LdaModel(corpus, topics, dictionary, passes=15)
        topics = lda_model.print_topics()
        for topic in topics:
            print(topic)
