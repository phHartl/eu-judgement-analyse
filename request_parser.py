from collections import OrderedDict

import xmltodict
import json

parse_counter = 0
DEBUG = 1

def extract_ids(data):
    list_id = []
    
    def recursive_crawl(data):
        if isinstance(data, OrderedDict):
            for key, value in data.items():
                if isinstance(value, OrderedDict):  # skip non-complex dict entries

                    # individual people IDs are inside ['URI'] OrderedDicts.
                    # cellar numbers can be a possible result and are filtered
                    # any remaining None's get filtered
                    if True:
                        if value.get('URI'):
                            list_id.append(value.get('URI').get('IDENTIFIER'))
                        elif value.get('TYPE') != 'cellar':
                            if value.get('IDENTIFIER'):
                                list_id.append(value.get('IDENTIFIER'))

                                        
        elif isinstance(data, list):
            for item in data:
                if(isinstance(item, OrderedDict)):  # skip non-complex entries, which hold unneeded info. prevents calling data.values() on a list item
                    recursive_crawl(item)
        else:
            if(DEBUG):
                print("Recursive crawl: Object is neither type 'list' nor 'OrderedDict'")


    recursive_crawl(data)
    
    # remove duplicates
    filtered_list_id = list(set(list_id))
    print(filtered_list_id)
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
            "case affecting": None, 
            "applicant": None,        
            "defendant": None,
            "affected_by_case": None,
            "procedure_type": None,
    }


    # assign values to variables if present, otherwise assign 'None'
    mongo_dict["reference"] = response.get("reference").split(':')[1]
    
    # there is no text for non-english documents
    content_url = response.get('content').get('CONTENT_URL')
    if content_url:
        mongo_dict["text"] = response.get("content").get("CONTENT_URL").get("DRECONTENT")

    # check every tag that could be empty in a judgment file; avoids get() on NoneTypes
    manifestation = response.get('content').get('NOTICE').get('MANIFESTATION')   
    if manifestation:
        mongo_dict["keywords"] = manifestation.get('MANIFESTATION_CASE-LAW_KEYWORDS')
        mongo_dict['subject'] = manifestation.get('"MANIFESTATION_CASE-LAW_SUBJECT')
        mongo_dict['endorsements'] = manifestation.get('MANIFESTATION_CASE-LAW_ENDORSEMENTS')

        parties = manifestation.get('MANIFESTATION_CASE-LAW_PARTIES')
        if parties:
            mongo_dict['parties'] = parties.get('VALUE')

        grounds = manifestation.get('MANIFESTATION_CASE-LAW_GROUNDS')
        if grounds:
            mongo_dict['grounds'] = grounds.get('VALUE')

        costs = manifestation.get('MANIFESTATION_CASE-LAW_COSTS_DECISIONS')
        if costs:
            mongo_dict['decisions_on_costs'] = costs.get('VALUE')

        operative = manifestation.get('MANIFESTATION_CASE-LAW_OPERATIVE_PART')
        if operative:
            mongo_dict['operative_part'] = operative.get('VALUE')
    
    work = response.get('content').get('NOTICE').get('WORK')
    if work:
        mongo_dict['celex'] = work.get('ID_CELEX').get('VALUE')
        mongo_dict['ecli'] = work.get('ECLI').get('VALUE')
        mongo_dict['date'] = work.get('WORK_DATE_DOCUMENT').get('VALUE')

        author_data = work.get('WORK_CREATED_BY_AGENT')
        if author_data:
            mongo_dict['author'] = extract_ids(author_data)

        subject_matter = work.get('RESOURCE_LEGAL_IS_ABOUT_SUBJECT-MATTER')
        if subject_matter:
            mongo_dict['subject_matter'] = extract_ids(subject_matter)
        
        requested_by_agent = work.get('CASE-LAW_REQUESTED_BY_AGENT')
        if requested_by_agent:
            mongo_dict['applicant'] = extract_ids(requested_by_agent)

        defended_by_agent = work.get('CASE-LAW_DEFENDED_BY_AGENT')
        if defended_by_agent:
            mongo_dict['defendant'] = extract_ids(defended_by_agent)

        procedure_type = work.get('CASE-LAW_HAS_TYPE_PROCEDURE_CONCEPT_TYPE_PROCEDURE')
        if procedure_type:
            mongo_dict['procedure_type'] = extract_ids(procedure_type)

        memberlist = work.get('CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST')
        if memberlist:
            concept = memberlist.get('CASE-LAW_IS_ABOUT_CONCEPT')
            if concept:
                mongo_dict['case_law_directory'] = extract_ids(concept)


    inverse = response.get('content').get('NOTICE').get('INVERSE')
    if inverse:
        mongo_dict['affected_by_case'] = inverse.get('RESOURCE_LEGAL_INTERPRETATION_REQUESTED_BY_CASE-LAW')

    parse_counter += 1
    return mongo_dict


def parse_response_for_mongo(response):
    data_dict = xmltodict.parse(response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]
    parsed_responses = []
    for response in results_dict:
        parsed_responses.append(parse_to_json(response))
    
    # print('CELEX Numbers of documents parsed:')
    # for data in parsed_responses:
    #     print(data['celex'])

