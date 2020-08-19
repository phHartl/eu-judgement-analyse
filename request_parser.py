from collections import OrderedDict
from bs4 import BeautifulSoup as bs

import xmltodict
import json
import unicodedata
import os

parse_counter = 0
DEBUG = 1
DEBUG_TAG = 'ecli'
CREATE_PARSING_DUMP = 1

def extract_data(data):
    list_data = []

    # iterate over the data tree recursively, depending on whether the current data is an OrderedDict or a list
    # distinguish between aiming for a VALUE or an IDENTIFIER
    def recursive_crawl(data):
        if isinstance(data, OrderedDict):
            for key, value in data.items():
                # data with the 'VALUE' key is usually singular.
                # however duplicates can occur, encapsulating each in an OrderedDict, hence why we use the recursion here as well. 
                if key == 'VALUE':
                    list_data.append(value)
                elif isinstance(value, OrderedDict):  # skip non-complex dict entries

                    # individual people IDs are inside ['URI'] OrderedDicts.
                    # cellar numbers can be a possible result and are filtered
                    # any remaining None's get filtered
                    if value.get('URI'):
                        list_data.append(value.get('URI').get('IDENTIFIER'))
                    elif value.get('TYPE') != 'cellar':
                        if value.get('IDENTIFIER'):
                            list_data.append(value.get('IDENTIFIER'))
                
        elif isinstance(data, list):
            for item in data:
                if(isinstance(item, OrderedDict)):  # skip non-complex entries, which hold unneeded info. prevents calling data.values() on a list item
                    recursive_crawl(item)
        else:
            if(DEBUG):
                print("Recursive crawl: Object is neither type 'list' nor 'OrderedDict'")
                print(data)

    recursive_crawl(data)

    filtered_list_data = list(set(list_data)) # remove duplicates
    return filtered_list_data


def response_to_file(response):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]

    counter = 0
    json_dump_directory = os.path.dirname(__file__) + '/json_dumps/'
    if not os.path.exists(json_dump_directory):
        os.mkdir(json_dump_directory)

    for result in results_dict:
        json_data = json.dumps(results_dict[counter], indent=4)
        with open(json_dump_directory + 'data_' + str(counter) +'.json', 'w') as json_file:
            json_file.write(json_data)
            json_file.close()
        counter += 1


def parse_result_to_file(dict, parse_counter):
    json_dump_directory = os.path.dirname(__file__) + '/parse_dumps/'
    if not os.path.exists(json_dump_directory):
        os.mkdir(json_dump_directory)

    json_data = json.dumps(dict, indent=4)
    with open(json_dump_directory + 'parse_' + str(parse_counter) +'.json', 'w') as json_file:
        json_file.write(json_data)
        json_file.close()


def parse_to_json(response):
    if DEBUG:
        global parse_counter
        print(parse_counter)

    if not response:
        print("request dict is empty")
        return None

    mongo_dict = {
            "reference": None,
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
    
    # there is no text for non-english documents
    content_url = response.get('content').get('CONTENT_URL')
    if content_url:
        if isinstance(content_url, list):
            mongo_dict["text"] = content_url[0].get('DRECONTENT')
        else:
            mongo_dict['text'] = content_url.get('DRECONTENT')
    # check every tag that could be empty in a judgment file; avoids get() on NoneTypes
    manifestation = response.get('content').get('NOTICE').get('MANIFESTATION')   
    if manifestation:
        mongo_dict["keywords"] = manifestation.get('MANIFESTATION_CASE-LAW_KEYWORDS')
        mongo_dict['subject'] = manifestation.get('"MANIFESTATION_CASE-LAW_SUBJECT')
        mongo_dict['endorsements'] = manifestation.get('MANIFESTATION_CASE-LAW_ENDORSEMENTS')

        parties = manifestation.get('MANIFESTATION_CASE-LAW_PARTIES')
        if parties:
            mongo_dict['parties'] = extract_data(parties)

        grounds = manifestation.get('MANIFESTATION_CASE-LAW_GROUNDS')
        if grounds:
            mongo_dict['grounds'] = extract_data(grounds)

        costs = manifestation.get('MANIFESTATION_CASE-LAW_COSTS_DECISIONS')
        if costs:
            mongo_dict['decisions_on_costs'] = extract_data(costs)

        operative = manifestation.get('MANIFESTATION_CASE-LAW_OPERATIVE_PART')
        if operative:
            mongo_dict['operative_part'] = extract_data(operative)
    
    work = response.get('content').get('NOTICE').get('WORK')
    if work:
        celex = work.get('ID_CELEX')
        if celex:
            mongo_dict['celex'] = extract_data(celex)

        date = work.get('WORK_DATE_DOCUMENT')
        if date:
            mongo_dict['date'] = extract_data(date)

        ecli = work.get('ECLI')
        if ecli:
            mongo_dict['ecli'] = extract_data(ecli)

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

        procedure_type = work.get('CASE-LAW_HAS_TYPE_PROCEDURE_CONCEPT_TYPE_PROCEDURE')
        if procedure_type:
            mongo_dict['procedure_type'] = extract_data(procedure_type)

        # specific .get() for list/dict distinction for this tag.
        # handle outside generic recursive function
        memberlist = work.get('CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST')
        if memberlist and not isinstance(memberlist, list):
            concept = memberlist.get('CASE-LAW_IS_ABOUT_CONCEPT')
            if concept:
                mongo_dict['case_law_directory'] = extract_data(concept)
        elif memberlist:
            print('memberlist list')
            for item in memberlist: # no 'if concept', memberlist is definitely not empty
                mongo_dict['case_law_directory'] = extract_data(item.get('CASE-LAW_IS_ABOUT_CONCEPT'))



    inverse = response.get('content').get('NOTICE').get('INVERSE')
    if inverse:
        mongo_dict['affected_by_case'] = inverse.get('RESOURCE_LEGAL_INTERPRETATION_REQUESTED_BY_CASE-LAW')


    if CREATE_PARSING_DUMP:
        parse_result_to_file(mongo_dict, parse_counter)

    parse_counter += 1
    return mongo_dict


def parse_response_for_mongo(response):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]
    parsed_responses = []
    for response in results_dict:
        parsed_responses.append(parse_to_json(response))
    
    print()
    print('Data parsed:')
    print()
    i = 0
    for data in parsed_responses:
        print('Document #', i, ': ', data[DEBUG_TAG])
        i += 1

def parse_response_for_mongo_xml(response):
    root = bs(response.content, "lxml", from_encoding = 'UTF-8')
    parsed_responses = []
    for element in root.find_all('result'):
        parsed_responses.append(parse_to_mongo_format_xml(element))
    if DEBUG:
        print('CELEX Numbers of documents parsed:')
        for data in parsed_responses:
            print(data['celex'])
    

# XML Implementation:

def find_simple_value_tag(root, tag):
    node = root.find(tag)
    if node is not None:
        return unicodedata.normalize("NFKD", node.value.string)
    else:
        return None

def find_multiple_sub_elements(root, tag, subtag):
    data = set()
    node = root.find(tag)
    if node is not None:
        for element in node.find_all(subtag):
            data.add(unicodedata.normalize("NFKD", element.text))
    return data

def find_multiple_sub_elements_for_multiple_tag(root, tag, subtag):
    data = set()
    elements = root.find_all(tag)
    for element in elements:
        if(element is not None):
            for node in element.find_all(subtag):
                data.add(node.text)
    return data

def parse_to_mongo_format_xml(element):
    mongo_dict = {
            "reference": None,
            "text": None,
            "keywords": None,
            "party names": None,
            "subject": None,
            "endorsements": None,
            "grounds": None,
            "decisions on costs": None,
            "operative part": None,
            "celex": None,
            "author": None,
            "subject matter": None,
            "case law directory": None,
            "ecli": None,
            "document date": None,
            "case affecting": None, 
            "applicant": None,        
            "defendant": None,
            "affected case": None,
            "procedure type": None,
    }

    mongo_dict['reference'] = element.reference.string.split(":")[1]

    text = element.find('drecontent') or None

    if(text is not None):
        text = unicodedata.normalize("NFKD", text.string)

    mongo_dict['text'] = text

    metadata_root = element.content.notice

    if metadata_root:
        mongo_dict['keywords'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_keywords')
        mongo_dict['subject'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_subject')
        mongo_dict['endorsements'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_endorsements')
        mongo_dict['operative part'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_operative_part')
        mongo_dict['decisions on cost'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_costs_decisions')
        mongo_dict['law grounds'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_grounds')
        mongo_dict['parties'] = find_simple_value_tag(metadata_root, 'manifestation_case-law_parties')
        mongo_dict['celex'] = find_simple_value_tag(metadata_root, 'id_celex')
        mongo_dict['ecli'] = find_simple_value_tag(metadata_root, 'ecli')
        mongo_dict['document date'] = find_simple_value_tag(metadata_root, 'work_date_document')

        mongo_dict['author'] = find_multiple_sub_elements_for_multiple_tag(metadata_root, 'work_created_by_agent', 'identifier')
        mongo_dict['subject matter'] = find_multiple_sub_elements_for_multiple_tag(metadata_root, 'resource_legal_is_about_subject-matter', 'preflabel')
        mongo_dict['case law directory'] = find_multiple_sub_elements(metadata_root, 'case-law_is_about_concept.memberlist', 'preflabel')
        mongo_dict['case affecting'] = find_multiple_sub_elements(metadata_root, 'case-law_confirms_resource_legal', 'identifier')
        mongo_dict['applicant'] = find_multiple_sub_elements(metadata_root, 'case-law_requested_by_agent', 'identifier')
        mongo_dict['defendant'] = find_multiple_sub_elements(metadata_root, 'case-law_defended_by_agent', 'identifier')
        mongo_dict['procedure type'] = find_multiple_sub_elements(metadata_root, 'case-law_has_type_procedure_concept_type_procedure', 'identifier')

        # Affected by case got three different tags
        affected_by_case_tags = metadata_root.find_all(["resource_legal_preliminary_question-submitted_by_communication_case", "resource_legal_preliminary_question-submitted_by_communication_case_new", "resource_legal_interpretation_requested_by_case-law",])
        
        if(affected_by_case_tags is not None):
            data = set()
            for element in affected_by_case_tags:
                if(element is not None):
                    for identifier in element.find_all('identifier'):
                        data.add(identifier.text)
            mongo_dict['affected case'] = data
    return mongo_dict
    # print(mongo_dict)