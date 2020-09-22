from pymongo import MongoClient, errors

client = MongoClient('localhost', 27017)
db = client.judgment_corpus
collection = client.judgment_corpus.judgments_en    # english as default language

PRINT_DUPLICATE_ERRORS = 0

AVAILABLE_LANGUAGES = {
    'Bulgarian' : 'bg',
    'Croatian' : 'hr',
    'Czech' : 'cs',
    'Danish' : 'da',
    'Dutch' : 'nl',
    'English' : 'en',
    'Estonian' : 'et',
    'Finnish' : 'fi',
    'French' : 'fr',
    'German' : 'de',
    'Greek' : 'el',
    'Hungarian' : 'hu',
    'Irish' : 'ga',
    'Italian' : 'it',
    'Latvian' : 'lv',
    'Lithuanian' : 'lt',
    'Maltese' : 'mt',
    'Polish' : 'pl',
    'Portuguese' : 'pt',
    'Romanian' : 'ro',
    'Slovak' : 'sk',
    'Slovenian' : 'sl',
    'Spanish' : 'es',
    'Swedish' : 'sv'
    }

def change_cur_coll(language):
    if language in AVAILABLE_LANGUAGES.values():
        _collection = db["judgments_{}".format(language)]
        return _collection

def init_db(used_languages = ['en']):
    collist = db.list_collection_names()

    for lang in used_languages:
        if lang not in AVAILABLE_LANGUAGES.values():
            continue

        coll_name = "judgments_" + lang
        if coll_name in collist:
            print("DB: collection already created for:'{}'".format(lang))
        else:
            db.create_collection(coll_name)
            collection.create_index([('reference', -1)], unique=True)
            # possibility that two collections are created at once
            # update collist repeatedly to ensure no crashes due to "collection has already been created"
            collist = db.list_collection_names()

def insert_doc(doc, language):
    if language in AVAILABLE_LANGUAGES.values():
        collection = change_cur_coll(language)
        try:
            collection.insert_one(doc)
        except errors.DuplicateKeyError as e:
            if PRINT_DUPLICATE_ERRORS:
                print("document exists already")
                print(e)
    else:
        print("DB: insert_doc(): unsuported language")

def get_all_docs(language):
    collection = change_cur_coll(language)
    cursor = collection.find({})
    return cursor

def get_docs_between_dates(start, end, language):
    # retrieves documents between two dates (dates must be in the format: y-m-dT00:00:00.000+00:00)
    cursor = collection.find({'date': {'$lt': end, '$gte': start}})
    return cursor

def get_docs_by_object_value(column, value, language):
    # retrieves documents by searching a object column for a specified value
    # this DB request requires JavaScript
    collection = change_cur_coll(language)
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


def get_docs_by_object_key(column, key, language):
    # retrieves documents by searching a object column for a specified value
    collection = change_cur_coll(language)
    cursor = collection.find({column + "." + key: {"$exists": True}})
    return cursor


def get_docs_search_string(column, search, language):
    # retrieves documents by searching a string column with specified words (words separated by whitespace)
    collection = change_cur_coll(language)
    search_words = search.split(" ")
    search_string = ""
    for word in search_words:
        regex_c_group = "(.*" + word + ".*)"
        search_string += regex_c_group
    cursor = collection.find({column: {"$regex": search_string, "$options": "i"}})
    return cursor

def get_docs_by_value(column, value, language):
    collection = change_cur_coll(language)
    cursor = collection.find({column: value})
    return cursor
  
def get_docs_by_custom_query(query_args, language):
    search_dict = {}
    keys_containing_dicts = ["author", "subject_matter", "case_law_directory",
                            "applicant", "defendant", "procedure_type"]
    change_cur_coll(language)

    for item in query_args:
        if item.get('column') in keys_containing_dicts:
            if item.get('search identifier'):
                if isinstance(item.get('value'), list):
                    if item.get('operator') == 'NOT':
                        search_dict[item.get('column')+".ids"] = {"$nin" : item.get('value')}
                    else:
                        search_dict[item.get('column')+".ids"] = {"$in" : item.get('value')}
                else:
                    if item.get('operator') == 'NOT':
                        search_dict[item.get('column')+".ids"] = {"$ne" : item.get('value')}
                    else:
                        search_dict[item.get('column')+'.ids'] = item.get('value')
            else:
                if isinstance(item.get('value'), list):
                    if item.get('operator') == 'NOT':
                        search_dict[item.get('column')+".labels"] = {"$nin" : item.get('value')}
                    else:
                        search_dict[item.get('column')+".labels"] = {"$in" : item.get('value')}
                else:
                    if item.get('operator') == 'NOT':
                        search_dict[item.get('column')+".labels"] = {"$ne": item.get('value')}
                    else:
                        search_dict[item.get('column')+".labels"] = item.get('value')
        else:
            if isinstance(item.get('value'), list):
                if item.get('operator') == 'NOT':
                    search_dict[item.get('column')] = {"$nin" : item.get('value')}
                else:
                    search_dict[item.get('column')] = {"$in" : item.get('value')}
            else:
                if item.get('operator') == 'NOT':
                    search_dict[item.get('column')] = {"$ne" : item.get('value')}
                else:
                    search_dict[item.get('column')] = item.get('value')

    cursor = collection.find(search_dict)
    return cursor
        