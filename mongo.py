from pymongo import MongoClient, errors

client = MongoClient('localhost', 27017)
db = client.test_database
collection = client.test_database.judgements

PRINT_DUPLICATE_ERRORS = 0


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
        if PRINT_DUPLICATE_ERRORS:
            print("document exists already")
            print(e)


def get_docs_between_dates(start, end):
    cursor = collection.find({'date': {'$lt': end, '$gte': start}})
    return cursor


def get_docs_by_title(title):
    cursor = collection.find({'title': title})
    return cursor


def get_docs_by_reference(reference):
    cursor = collection.find({'reference': reference})
    return cursor


def get_docs_by_id(_id):
    cursor = collection.find({'_id': _id})
    return cursor


def get_docs_by_celex(celex):
    cursor = collection.find({'celex': celex})
    return cursor


def get_docs_by_date(date):
    cursor = collection.find({'date': date})
    return cursor


def get_docs_by_ecli(ecli):
    cursor = collection.find({'ecli': ecli})
    return cursor


def get_docs_by_case_affecting(case_affecting):
    cursor = collection.find({'case_affecting': case_affecting})
    return cursor


init_db()
for doc in get_docs_by_case_affecting("dec:1957:2:oj"):
    print(doc)

