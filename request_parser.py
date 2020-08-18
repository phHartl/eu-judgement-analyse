from collections import OrderedDict
from bs4 import BeautifulSoup as bs

import xmltodict
import json
import unicodedata

def extract_ids(data, context=''):
    list_id = []
    
    def recursive_crawl(data, context):
        if isinstance(data, OrderedDict):
            for key, value in data.items():
                if isinstance(value, OrderedDict):  # skip non-complex dict entries

                    # author specific: individual people IDs are inside ['SAMEAS']['URI']. both are OrderedDicts
                    # only add individuals. skip cellar IDs
                    if context == 'author_data':
                        if value.get('URI'):                        
                            list_id.append(value.get('URI').get('IDENTIFIER'))
                        elif value.get('TYPE') != 'cellar':
                            list_id.append(value.get('IDENTIFIER'))

                    # non-specific complex structures
                    else:
                        list_id.append(value.get('IDENTIFIER'))
                                        
        elif isinstance(data, list):
            for item in data:
                if(isinstance(item, OrderedDict)):  # skip non-complex entries, which hold unneeded info. prevents calling data.values() on a list item
                    recursive_crawl(item, context)
        else:
            if(DEBUG):
                print("Recursive crawl: Object is neither type 'list' nor 'OrderedDict'")


    recursive_crawl(data, context)
    
    # remove duplicates
    filtered_list_id = list(set(list_id))
    return filtered_list_id


def response_to_file(response):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]

    counter = 0
    for result in results_dict:
        json_data = json.dumps(results_dict[counter], indent=4)
        with open("data_" + str(counter) +".json", "w") as json_file:
            json_file.write(json_data)
            json_file.close()
        counter += 1


def parse_to_json(response):
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
            "case affecting": None, 
            "applicant": None,        
            "defendant": None,
            "affected_by_case": None,
            "procedure_type": None,
    }


    # assign values to variables if present, otherwise assign 'None'
    mongo_dict["reference"] = response.get("reference").split(':')[1] or None
    
    # there is no text for non-english documents
    content_url = response.get('content').get('CONTENT_URL') or None
    if content_url:
        mongo_dict["text"] = response.get("content").get("CONTENT_URL").get("DRECONTENT") or None

    # check every tag that could be empty in a judgment file; avoids get() on NoneTypes
    manifestation = response.get('content').get('NOTICE').get('MANIFESTATION') or None   
    if manifestation:
        mongo_dict["keywords"] = manifestation.get('MANIFESTATION_CASE-LAW_KEYWORDS') or None
        mongo_dict['subject'] = manifestation.get('"MANIFESTATION_CASE-LAW_SUBJECT') or None
        mongo_dict['endorsements'] = manifestation.get('MANIFESTATION_CASE-LAW_ENDORSEMENTS') or None

        parties = manifestation.get('MANIFESTATION_CASE-LAW_PARTIES')
        if parties:
            mongo_dict['parties'] = parties.get('VALUE') or None

        grounds = manifestation.get('MANIFESTATION_CASE-LAW_GROUNDS')
        if grounds:
            mongo_dict['grounds'] = grounds.get('VALUE') or None

        costs = manifestation.get('MANIFESTATION_CASE-LAW_COSTS_DECISIONS')
        if costs:
            mongo_dict['decisions_on_costs'] = costs.get('VALUE') or None

        operative = manifestation.get('MANIFESTATION_CASE-LAW_OPERATIVE_PART')
        if operative:
            mongo_dict['operative_part'] = operative.get('VALUE') or None
    
    work = response.get('content').get('NOTICE').get('WORK')
    if work:
        mongo_dict['celex'] = work.get('ID_CELEX').get('VALUE') or None
        mongo_dict['ecli'] = work.get('ECLI').get('VALUE') or None
        mongo_dict['date'] = work.get('WORK_DATE_DOCUMENT').get('VALUE') or None

        author_data = work.get('WORK_CREATED_BY_AGENT') or None
        if author_data:
            mongo_dict['author'] = extract_ids(author_data, 'author_data')

        subject_matter = work.get('RESOURCE_LEGAL_IS_ABOUT_SUBJECT-MATTER') or None
        if subject_matter:
            mongo_dict['subject_matter'] = extract_ids(subject_matter)
        
        requested_by_agent = work.get('CASE-LAW_REQUESTED_BY_AGENT') or None
        if requested_by_agent:
            mongo_dict['applicant'] = requested_by_agent.get('VALUE')

        defended_by_agent = work.get('CASE-LAW_DEFENDED_BY_AGENT') or None
        if defended_by_agent:
            mongo_dict['defendant'] = defended_by_agent.get('VALUE')

        procedure_type = work.get('CASE-LAW_HAS_TYPE_PROCEDURE_CONCEPT_TYPE_PROCEDURE')
        if procedure_type:
            mongo_dict['procedure_type'] = extract_ids(procedure_type)

        memberlist = work.get('CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST')
        if memberlist:
            concept = memberlist.get('CASE-LAW_IS_ABOUT_CONCEPT')
            if concept:
                mongo_dict['case_law_directory'] = extract_ids(concept)
                print(mongo_dict['case_law_directory'])


    inverse = response.get('content').get('NOTICE').get('INVERSE')
    if inverse:
        mongo_dict['affected_by_case'] = inverse.get('RESOURCE_LEGAL_INTERPRETATION_REQUESTED_BY_CASE-LAW')

    
    return mongo_dict


def parse_response_for_mongo(response):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]
    parsed_responses = []
    for response in results_dict:
        parsed_responses.append(parse_to_json(response))
    
    print('CELEX Numbers of documents parsed:')
    for data in parsed_responses:
        print(data['celex'])

def parse_response_for_mongo_xml(response):
    root = bs(response.content, "lxml", from_encoding = 'UTF-8')
    parsed_responses = []
    for element in root.find_all('result'):
        parsed_responses.append(parse_to_mongo_format_xml(element))
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