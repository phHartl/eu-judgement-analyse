import datetime
import random
import sys
from collections import OrderedDict

from bson.json_util import loads, dumps
from pymongo import MongoClient, errors
client = MongoClient('localhost', 27017)
db = client.test_database
collection = client.test_database.judgements


def init_db():
    collist = db.list_collection_names()
    if "judgements" in collist:
        print("Collection exists already")
    else:
        db.create_collection("judgements", )
        collection.create_index([('reference', -1)], unique=True)
    # Force create!


def insert_doc(doc):
    try:
        collection.insert_one(doc)
    except errors.DuplicateKeyError as e:
        print("document exists already !!!")
        print(e)


def get_docs_by_date():
    start = datetime.datetime(2000, 1, 1)
    end = datetime.datetime(2005, 1, 1)
    cursor = collection.find({'year': {'$lt': end, '$gte': start}})
    cursor = dumps(cursor, separators=(',', ': '))
    return cursor


# test shit
def test():
    init_db()
    try:
        db.judgements.insert_one({"x": 1})
        print("NOT good; the insert above should have failed.")

    except:
        print("OK. Expected exception:", sys.exc_info())

    try:
        for x in range(1, 10):
            rnd_date = random.randrange(2000, 2010, 1)
            okdoc = {"name": "test", "year": datetime.datetime(rnd_date, 1, 1), "content": {
                "test1": "test",
                "test2": "test",
                "test3": 1964
            }}
            insert_doc(collection, okdoc)
            print("All good.")

    except:
        print("exc:", sys.exc_info())

    start = datetime.datetime(2000, 1, 1)
    end = datetime.datetime(2005, 1, 1)
    for doc in db.judgements.find({'year': {'$lt': end, '$gte': start}}):
        print(doc)
    # test shit
    print(get_docs_by_date())

init_db()

