import configparser
from analysis import CorpusAnalysis
from flask import render_template, Flask, request, jsonify, make_response
from mongo import init_client, db_is_running, close_client
from api_functions import get_all_docs, get_docs_by_custom_query, analyse_corpus
from tasks import execute_analyser_small, execute_analyser_big

config = configparser.ConfigParser()
config.read("config.ini")

# Create the application instance
app = Flask(__name__)

def execute_analyser(corpus_args, analysis_args, language):
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

@app.route('/eu-judgments/api/data', methods=['POST'])
def query():
    req = request.get_json()
    language = req.get('language')
    corpus_args = req.get('corpus')
    analysis_args = req.get('analysis')
    corpus = {}
    analysis_data = {}

    if (not language
        or not corpus_args
        or not analysis_args):
        # missing info
        return "incorrect request parameters"

    if config.getboolean("execution_mode", "server_mode"):
        init_client()
        if corpus_args == 'all':
            corpus = get_all_docs(language)
        else:
            corpus = get_docs_by_custom_query(corpus_args, language)
        print(corpus.count())
        if(corpus.count() > 10):
            # celery -A tasks.celery worker -Q huge_corpus -c10 -Ofair
            analysis_data = execute_analyser_big.apply_async(args=[corpus_args, analysis_args, language], queue="huge_corpus")
            result = analysis_data.get()
        else:
            # celery -A tasks.celery worker -Q celery -c2
            analysis_data = execute_analyser_small.delay(corpus_args, analysis_args, language)
            result = analysis_data.get()
    else:
        result = execute_analyser(corpus_args, analysis_args, language)
    
    response = make_response(jsonify(result))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

    # If we're running in stand alone mode, run the application
if __name__ == '__main__':
    if db_is_running():
        app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
