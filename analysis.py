from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag, FreqDist
import re

english_stop_words = list(set(stopwords.words("english")))
german_stop_words = list(set(stopwords.words("german")))


def remove_punctuation(sentence):
    sentence = re.sub(r'[^\w\s]', '', sentence)
    return sentence


def remove_stopwords(sentence, english=True):
    if english:
        return [w for w in sentence if not w.lower() in english_stop_words]
    return [w for w in sentence if not w.lower() in german_stop_words]


def tokenize(text):
    sentences = sent_tokenize(text)
    cleaned_sentences = [remove_punctuation(sentence) for sentence in sentences]
    sentences_word_tokenized = [word_tokenize(sentence) for sentence in cleaned_sentences]
    sentences_tokenized_filtered = [remove_stopwords(sentence) for sentence in sentences_word_tokenized]
    return sentences_tokenized_filtered


def part_of_speech_tagging(text):
    tokenized_text = tokenize(text)
    pos = [pos_tag(tokenized_sentence) for tokenized_sentence in tokenized_text]
    return pos


def get_word_list(text):
    """Returns a list of all words present in the text."""
    tokenized_text = tokenize(text)
    # Flatten the resulting array
    word_list = [item for sublist in tokenized_text for item in sublist]
    return word_list


def get_lemma(word):
    lemma = wordnet.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def most_frequent_words(text, n=10):
    tokens = get_word_list(text)
    return FreqDist(tokens).most_common(n)

def average_word_length(text):
    tokens = get_word_list(text)
    return sum(map(len, tokens)) / len(tokens)
