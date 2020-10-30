from celery import Celery
import celery_config

from mongo import init_client, close_client
from api_functions import get_all_docs, get_docs_by_custom_query, analyse_corpus

celery = celery = Celery(config_source=celery_config)

@celery.task(name="huge_corpus")
def execute_analyser_big(corpus_args, analysis_args, language):
    # define the corpus
    # whole corpus or custom subcorpus
    init_client()
    if corpus_args == 'all':
        corpus = get_all_docs(language)
    else:
        corpus = get_docs_by_custom_query(corpus_args, language)
    data = analyse_corpus(corpus, analysis_args, language)
    close_client()
    return data

@celery.task(name="small_corpus")
def execute_analyser_small(corpus_args, analysis_args, language):
    # define the corpus
    # whole corpus or custom subcorpus
    init_client()
    if corpus_args == 'all':
        corpus = get_all_docs(language)
    else:
        corpus = get_docs_by_custom_query(corpus_args, language)
    data = analyse_corpus(corpus, analysis_args, language)
    close_client()
    return data