
from pymongo import MongoClient, errors
from argparse import ArgumentParser
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from mongo import init_db
from request import request_all_data
import functools
import timeit

client = MongoClient('localhost', 27017)
db = client.judgment_corpus
collection = client.judgment_corpus.judgments_en    # english as default language
AVAILABLE_LANGUAGES = {
    'Bulgarian' : 'bg',
    'Croatian' : 'hr',
    'Czech' : 'cs',
    'Danish' : 'da',
    'Dutch' : 'nl',
    'English' : 'en',
    'Estonian' : 'et',
    'Finnish' : 'fi',
    'French' : 'fr',
    'German' : 'de',
    'Greek' : 'el',
    'Hungarian' : 'hu',
    'Irish' : 'ga',
    'Italian' : 'it',
    'Latvian' : 'lv',
    'Lithuanian' : 'lt',
    'Maltese' : 'mt',
    'Polish' : 'pl',
    'Portuguese' : 'pt',
    'Romanian' : 'ro',
    'Slovak' : 'sk',
    'Slovenian' : 'sl',
    'Spanish' : 'es',
    'Swedish' : 'sv'
    }

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})




def query_data_options():
    questions = [{
            'type': 'list',
            'name': 'data size',
            'message': 'What should your data contain?',
            'choices': [
                {'name': 'single language'},
                {'name': 'all available languages (24)'},
                {'name': 'specify languages'},
                ],
            'default': 'single language',
            }]
    answers = prompt(questions, style=style)
    return answers.get('data size')

def query_single_language():
    questions = [{
        'type': 'input',
        'name': 'language',
        'message': 'Which language should your corpus be created for?',
        'default': 'English',
        'validate': lambda feedback: "This language is not supported"
            if feedback not in AVAILABLE_LANGUAGES.keys() else True
    }]
    answers = prompt(questions, style=style)
    return answers.get('language')

def query_specific_languages():
    available_choices = []
    for item in AVAILABLE_LANGUAGES.keys():
        available_choices.append({'name': item})

    questions = [{
        'type': 'checkbox',
        'name': 'language list',
        'message': 'Please select all language to include.',
        'choices' : available_choices,
    }]
    answers = prompt(questions, style=style)

    # validation seems to be broken for checkboxes. validate entry and re-prompt if necessary
    if len(answers.get('language list')) == 0:
        print('')
        print('ERROR: At least one language must be selected')
        query_specific_languages()
    return answers.get('language list')

def confirm_corpus_scope(corpus_scope):
    questions = [{
        'type': 'confirm',
        'name': 'corpus confirmation',
        'message': 'Should the corpus be created for: {}'.format(corpus_scope),
    }]
    answers = prompt(questions, style=style)
    return answers.get('corpus confirmation')

def confirm_data_acquisition():
    questions = [{
        'type': 'confirm',
        'name': 'request data confirmation',
        'message': 'Do you want to acquire corpus data from EUR-Lex? WARNING: This can take a very long time!',
    }]
    answers = prompt(questions, style=style)
    return answers.get('request data confirmation')


def main():
    print('First: Initialise database for your data:')
    data_size = query_data_options()
    if data_size == 'single language':
        answer = query_single_language()
        corpus_scope = [answer]
    elif data_size == 'all available languages (24)':
        corpus_scope = list(AVAILABLE_LANGUAGES.keys())
    elif data_size == 'specify languages':
        corpus_scope = query_specific_languages()
        # corpus_scope = []
        # for item in verbose_languages:
        #     corpus_scope.append(AVAILABLE_LANGUAGES.get(item))

    corpus_confirmation = confirm_corpus_scope(corpus_scope)
    if corpus_confirmation: # initialise database based on input using language identifiers in AVAILABLE_LANGUAGES
        lang_list = []
        for item in corpus_scope:
            lang_list.append(AVAILABLE_LANGUAGES.get(item))
        init_db(lang_list)

    print('')
    acquire_data = confirm_data_acquisition()
    if acquire_data:
        request_all_data(lang_list)
        ## benchmark:
        # print('Data acquisition started. Completion time will be printed once finished')
        # t1 = timeit.Timer(functools.partial(request_all_data, lang_list))
        # time_needed = t1.timeit(1)
        # print('Requested and parsed all documents. Completion time:')
        # print(time_needed)


if __name__ == "__main__":
    main()
