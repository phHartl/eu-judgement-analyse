from analysis import CorpusAnalysis
from flask import render_template, Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from collections import OrderedDict
from celery import Celery
from api_functions import *

# Create the application instance
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:32768/judgment_corpus"
app.config.update(
    # Change port here
    backend='redis://localhost:32775',
    broker='redis://localhost:32775',
)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['backend'],
        broker=app.config['broker']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task(name="execute_analyser")
def execute_analyser(corpus_args, analysis_args, language):
    # define the corpus
    # whole corpus or custom subcorpus
    init_client()
    if corpus_args == 'all':
        corpus = get_all_docs(language)
    else:
        corpus = get_docs_by_custom_query(corpus_args, language)
    return analyse_corpus(corpus, analysis_args, language)

@app.route('/eu-judgments/api/data', methods=['POST'])
def query():
    # args = request.args
    # print(args)
    req = request.get_json(force=True)
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

    analysis_data = execute_analyser.delay(corpus_args, analysis_args, language)
    result = analysis_data.get()
    response = make_response(jsonify(result))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

    # If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
