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


def get_docs_by_author_cj(CJ):
    cursor = collection.find({'author.CJ': CJ})
    return cursor


def get_docs_by_author_side(SIDE):
    cursor = collection.find({'subject_matter.SIDE': SIDE})
    return cursor


def get_docs_by_subject_matter_finc(FINC):
    cursor = collection.find({'subject_matter.FINC': FINC})
    return cursor


def get_docs_by_author_pere(PERE):
    cursor = collection.find({'subject_matter.PERE': PERE})
    return cursor


def get_docs_by_author_ceca(CECA):
    cursor = collection.find({'subject_matter.CECA': CECA})
    return cursor


def get_docs_search_string(column, search):
    search_words = search.split(" ")
    search_string = ""
    for word in search_words:
        regex_c_group = "(.*" + word + ".*)"
        search_string += regex_c_group
    print(search_string)
    cursor = collection.find({column: {"$regex": search_string, "$options": "i"}})
    return cursor


init_db()

for doc in get_docs_search_string("title", "judgment 1958"):
    print(doc)
