from pymongo import MongoClient, errors

client = MongoClient('localhost', 27017)
db = client.judgment_corpus
collection = client.judgment_corpus.judgments_en

PRINT_DUPLICATE_ERRORS = 0


def init_db(english_corpus_used = True, german_corpus_used = False):
    collist = db.list_collection_names()
    if english_corpus_used:
        if "judgments_en" in collist:
            print("Collection already created for: English corpus")
        else:
            db.create_collection("judgments_en", )
            collection.create_index([('reference', -1)], unique=True)
    if german_corpus_used:
        if "judgments_de" in collist:
            print("Collection already created for: German corpus")
        else:
            db.create_collection("judgments_de", )
            collection.create_index([('reference', -1)], unique=True)


def insert_doc(doc, corpus):
    if corpus == 'en':
        collection = client.judgment_corpus.judgments_en
    elif corpus == 'de':
        collection = client.judgment_corpus.judgments_de

    try:
        collection.insert_one(doc)
    except errors.DuplicateKeyError as e:
        if PRINT_DUPLICATE_ERRORS:
            print("document exists already")
            print(e)


def get_docs_between_dates(start, end):
    # retrieves documents between two dates (dates must be in the format: y-m-dT00:00:00.000+00:00)
    cursor = collection.find({'date': {'$lt': end, '$gte': start}})
    return cursor


def get_docs_by_title(title):
    # retrieves documents by the title
    cursor = collection.find({'title': title})
    return cursor


def get_docs_by_reference(reference):
    # retrieves documents by the reference number
    cursor = collection.find({'reference': reference})
    return cursor


def get_docs_by_id(_id):
    # retrieves documents by the mongoDb _id
    cursor = collection.find({'_id': _id})
    return cursor


def get_docs_by_celex(celex):
    # retrieves documents by the celex number
    cursor = collection.find({'celex': celex})
    return cursor


def get_docs_by_date(date):
    # retrieves documents by the date (date must be in the format: y-m-dT00:00:00.000+00:00)
    cursor = collection.find({'date': date})
    return cursor


def get_docs_by_ecli(ecli):
    # retrieves documents by the ecli number
    cursor = collection.find({'ecli': ecli})
    return cursor


def get_docs_by_case_affecting(case_affecting):
    # retrieves documents by the case_affecting value
    cursor = collection.find({'case_affecting': case_affecting})
    return cursor


def get_docs_by_object_value(column, value):
    # retrieves documents by searching a object column for a specified value
    # this DB request requires JavaScript
    cursor = collection.find({"$where":
    '''
        function() {
            for (var field in this.''' + column + ''') {
                if (this.''' + column + '''[field] == ''' + '"' + value + '"' + ''') {
                    return true;
                }
            }
        return false;
        }
    '''
    })
    return cursor


def get_docs_by_object_key(column, key):
    # retrieves documents by searching a object column for a specified value
    cursor = collection.find({column + "." + key: {"$exists": True}})
    return cursor


def get_docs_search_string(column, search):
    # retrieves documents by searching a string column with specified words (words separated by whitespace)
    search_words = search.split(" ")
    search_string = ""
    for word in search_words:
        regex_c_group = "(.*" + word + ".*)"
        search_string += regex_c_group
    print(search_string)
    cursor = collection.find({column: {"$regex": search_string, "$options": "i"}})
    return cursor


init_db(english_corpus_used = True, german_corpus_used = True)

# for doc in get_docs_by_object_value("author", "Court of Justice"):
#     print(doc.get('author'))
