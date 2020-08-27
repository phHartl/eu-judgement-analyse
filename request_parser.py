from collections import OrderedDict
from datetime import datetime

import xmltodict

from data_dump import dump_to_files

DEBUG = 0
DEBUG_TAG = 'affected_by_case'
parse_counter = 0

def extract_data(data):
    list_data = []
    id_label_dict = {}

    # iterate over the data tree recursively, depending on whether the current data is an OrderedDict or a list
    # distinguish between aiming for a VALUE or an IDENTIFIER
    def recursive_crawl(data):
        if isinstance(data, OrderedDict):
            for key, value in data.items():
                # data with the 'VALUE' key is usually singular.
                # however duplicates can occur, encapsulating each in an OrderedDict, hence why we use the recursion here as well.
                if key == 'VALUE':
                    list_data.append(value)
                elif key == 'IDENTIFIER':
                    _id = value
                    _label = data.get('PREFLABEL')
                    id_label_dict[_id] = _label
                elif key == 'SAMEAS':
                    if isinstance(value, list):
                        recursive_crawl(value)
                elif key == 'URI':
                    list_data.append(value.get('IDENTIFIER'))
                elif isinstance(value, OrderedDict):
                    recursive_crawl(value)
                elif key == 'CASE-LAW_IS_ABOUT_CONCEPT':
                    recursive_crawl(value)
                elif key == 'NESTEDLIST':
                    recursive_crawl(value)

        elif isinstance(data, list):
            for item in data:
                if (isinstance(item,
                               OrderedDict)):  # skip non-complex entries, which hold unneeded info. prevents calling data.values() on a list item
                    recursive_crawl(item)
        else:
            if (DEBUG):
                print("Recursive crawl: Object is neither type 'list' nor 'OrderedDict'")

    recursive_crawl(data)

    if id_label_dict:
        return id_label_dict    # all {id : label} pairs
    else:
        filtered_list_data = list(set(list_data))  # remove duplicates
        return filtered_list_data   # case_affecting and affected_by_case


def parse_to_json(response):
    if DEBUG:
        global parse_counter
        print(parse_counter)

    if not response:
        print("request dict is empty")
        return None

    mongo_dict = {
        "reference": None,
        "title": None,
        "text": None,
        "keywords": None,
        "parties": None,
        "subject": None,
        "endorsements": None,
        "grounds": None,
        "decisions_on_costs": None,
        "operative_part": None,
        "celex": None,
        "author": None,
        "subject_matter": None,
        "case_law_directory": None,
        "ecli": None,
        "date": None,
        "case_affecting": None,
        "applicant": None,
        "defendant": None,
        "affected_by_case": None,
        "procedure_type": None,
    }

    mongo_dict["reference"] = response.get("reference").split(':')[1]

    # check every tag that could be empty in a judgment file; avoids get() on NoneTypes
    #
    # there is no text for non-english documents
    content_url = response.get('content').get('CONTENT_URL')
    if content_url:
        if isinstance(content_url, list):
            mongo_dict["text"] = content_url[0].get('DRECONTENT')
        else:
            mongo_dict['text'] = content_url.get('DRECONTENT')

    expression = response.get('content').get('NOTICE').get('EXPRESSION')
    if expression:
        title = expression.get("EXPRESSION_TITLE")
        if title:
            # list with length 1, use only the first value
            mongo_dict['title'] = extract_data(title)[0]

    manifestation = response.get('content').get('NOTICE').get('MANIFESTATION')
    if manifestation:
        mongo_dict['subject'] = manifestation.get('MANIFESTATION_CASE-LAW_SUBJECT')
        mongo_dict['endorsements'] = manifestation.get('MANIFESTATION_CASE-LAW_ENDORSEMENTS')

        keywords = manifestation.get('MANIFESTATION_CASE-LAW_KEYWORDS')
        if keywords:
            mongo_dict["keywords"] = extract_data(keywords)[0]

        parties = manifestation.get('MANIFESTATION_CASE-LAW_PARTIES')
        if parties:
            mongo_dict['parties'] = extract_data(parties)[0]

        grounds = manifestation.get('MANIFESTATION_CASE-LAW_GROUNDS')
        if grounds:
            mongo_dict['grounds'] = extract_data(grounds)[0]

        costs = manifestation.get('MANIFESTATION_CASE-LAW_COSTS_DECISIONS')
        if costs:
            mongo_dict['decisions_on_costs'] = extract_data(costs)[0]

        operative = manifestation.get('MANIFESTATION_CASE-LAW_OPERATIVE_PART')
        if operative:
            mongo_dict['operative_part'] = extract_data(operative)[0]

    work = response.get('content').get('NOTICE').get('WORK')
    if work:
        celex = work.get('ID_CELEX')
        if celex:
            mongo_dict['celex'] = extract_data(celex)[0]

        date = work.get('WORK_DATE_DOCUMENT')
        if date:
            date = datetime.strptime(extract_data(date)[0], '%Y-%m-%d')
            mongo_dict['date'] = date

        ecli = work.get('ECLI')
        if ecli:
            mongo_dict['ecli'] = extract_data(ecli)[0]

        memberlist = work.get('CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST')
        if memberlist:
            # MongoDB cannot handle dots in key-strings. replace them with commas
            _temp_dict = extract_data(memberlist)
            _dict_dots_replaced = {}
            for key, value in _temp_dict.items():
                if '.' in key:
                    _dict_dots_replaced[key.replace('.', ',')] = value
                else:
                    _dict_dots_replaced[key] = value
            mongo_dict['case_law_directory'] = _dict_dots_replaced

        author_data = work.get('WORK_CREATED_BY_AGENT')
        if author_data:
            mongo_dict['author'] = extract_data(author_data)

        subject_matter = work.get('RESOURCE_LEGAL_IS_ABOUT_SUBJECT-MATTER')
        if subject_matter:
            mongo_dict['subject_matter'] = extract_data(subject_matter)

        case_affecting = work.get('CASE-LAW_CONFIRMS_RESOURCE_LEGAL')
        if case_affecting:
            mongo_dict['case_affecting'] = extract_data(case_affecting)

        requested_by_agent = work.get('CASE-LAW_REQUESTED_BY_AGENT')
        if requested_by_agent:
            mongo_dict['applicant'] = extract_data(requested_by_agent)

        defended_by_agent = work.get('CASE-LAW_DEFENDED_BY_AGENT')
        if defended_by_agent:
            mongo_dict['defendant'] = extract_data(defended_by_agent)

        procedure_type = work.get(
            'CASE-LAW_HAS_TYPE_PROCEDURE_CONCEPT_TYPE_PROCEDURE')
        if procedure_type:
            mongo_dict['procedure_type'] = extract_data(procedure_type)

    inverse = response.get('content').get('NOTICE').get('INVERSE')
    if inverse:
        affected_by_case = inverse.get(
            'RESOURCE_LEGAL_INTERPRETATION_REQUESTED_BY_CASE-LAW')
        if affected_by_case:
            print('AFFECTED BY CASE FOUND! check dump and backup file')
            mongo_dict['affected_by_case'] = extract_data(affected_by_case)

    parse_counter += 1
    return mongo_dict


def parse_response_for_mongo(response, debug_mode=False, dump_mode=None):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]

    if dump_mode == 'response' or dump_mode == 'all':
        dump_to_files(results_dict, dump_type='response')

    if debug_mode:
        global DEBUG
        DEBUG = 1

    parsed_responses = []
    for response in results_dict:
        parsed_responses.append(parse_to_json(response))

    if dump_mode == 'parse' or dump_mode == 'all':
        dump_to_files(parsed_responses, dump_type='parse')

    if DEBUG:
        print()
        print('Data parsed:')
        print()

        i = 0
        for data in parsed_responses:
            print('Document #', i, ': ', data[DEBUG_TAG])
            i += 1
    return parsed_responses
