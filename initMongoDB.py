import sys
from pymongo import MongoClient
from collections import OrderedDict

client = MongoClient('localhost', 27017)
db = client.test_database

db.judgements.drop()

db.create_collection("judgements",)  # Force create!

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
                "bsonType": "int",
                "minimum": 1956,
                "maximum": 2099,
                "exclusiveMaximum": False,
                "description": "must be an integer in [ 2017, 3017 ] and is required"
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

try:
    db.judgements.insert_one({"x": 1})
    print("NOT good; the insert above should have failed.")

except:
    print("OK. Expected exception:", sys.exc_info())


try:
    okdoc = {"name": "test", "year": 2019, "content": {
        "test1": "test",
        "test2": "test",
        "test3": 1964
    }}
    db.judgements.insert_one(okdoc)
    print("All good.")

except:
    print("exc:", sys.exc_info())
