from mongo import get_docs_by_date
from flask import render_template, Flask, request
from flask_pymongo import PyMongo

# Create the application instance
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test_database"
mongo = PyMongo(app)
db = mongo.db
collection = mongo.db.judgements


# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')


@app.route('/api/data', methods=['GET'])
def query():
    # args = request.args
    # print(args)
    return get_docs_by_date()
    

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)