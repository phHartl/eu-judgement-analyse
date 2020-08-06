import datetime
import random
import sys
from collections import OrderedDict

from bson.json_util import loads, dumps
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.test_database
collection = client.test_database.judgements


def init_db():
    db.judgements.drop()
    db.create_collection("judgements", )  # Force create!

    #  $jsonSchema expression type is prefered.  New since v3.6 (2017):
    vexpr = {"$jsonSchema":
        {
            "bsonType": "object",
            "required": ["name", "year", "content"],
            "properties": {
                "title": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "year": {
                    "bsonType": "date",
                    "description": "must be an datetime and is required"
                },
                "content": {
                    "bsonType": "object",
                    "description": "must be a object and is required"
                }
            }
        }
    }

    cmd = OrderedDict([('collMod', 'judgements'),
                       ('validator', vexpr),
                       ('validationLevel', 'moderate')])

    db.command(cmd)


def insert_doc(coll, doc):
    if not isinstance(doc, list):
        coll.insert_one(doc)
    else:
        coll.insert_many(doc)


def get_docs_by_date():
    start = datetime.datetime(2000, 1, 1)
    end = datetime.datetime(2005, 1, 1)
    # start = datetime.strptime(start, '%d/%m/%y %H:%M:%S')
    # end = datetime.strptime(end, '%d/%m/%y %H:%M:%S')
    cursor = collection.find({'year': {'$lt': end, '$gte': start}})
    cursor = dumps(cursor, separators=(',', ': '))
    return cursor.replace('/', r'\/')


# test shit
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
