from mongo import *
from analysis import CorpusAnalysis
from flask import render_template, Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from collections import OrderedDict
from api_functions import *

# Create the application instance
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/judgment_corpus"
app.config['TESTING'] = True
mongo = PyMongo(app)
db = mongo.db
collection = mongo.db.judgements


def __singular_doc_requested(args):
    if isinstance(args, list):
        return False
    # https://www.geeksforgeeks.org/python-get-the-first-key-in-dictionary/
    if isinstance(args.get('value'), list):
        return False
    uids = ['celex', 'ecli', 'reference']
    if args.get('column') not in uids:
        return False
    return True

@app.before_first_request          
def load_models():
    add_analyser("en")
    add_analyser("de")


# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')


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

    # define the corpus
    # whole corpus or custom subcorpus
    if corpus_args == 'all':
        corpus = get_all_docs(language)
    else:
        corpus = get_docs_by_custom_query(corpus_args, language)

    # analyse and save for in every way specified in the request
    # for arg in analysis_args:
    #     analysis_data[arg] = analyse_selected_corpus(corpus, arg)
    analysis_data = analyse_corpus(corpus, analysis_args, language)
    response = make_response(jsonify(analysis_data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

    # If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
