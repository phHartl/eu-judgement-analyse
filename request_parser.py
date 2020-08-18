from collections import OrderedDict
import xmltodict

def extract_ids(data):
    list_id = []
    for key, value in data.items():
        if isinstance(value, OrderedDict):
            print(value.get('IDENTIFIER'))
            list_id.append(value.get('IDENTIFIER'))
    
    # remove duplicates
    filtered_list_id = list(set(list_id))
    return filtered_list_id

def parse_to_mongo_format(_response):
    data_dict = xmltodict.parse(_response.content)
    results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]
    response = results_dict[1]

    # Simple implementation to write every result to a separate .json - however empty tags are not returned by the API so we need to modify this dic in the future
    # counter = 0
    # for result in results_dict:
    #     json_data = json.dumps(results_dict[counter], indent=4)
    #     with open("data_" + str(counter) +".json", "w") as json_file:
    #         json_file.write(json_data)
    #         json_file.close()
    #     counter += 1

    if not response:
        print("request dict is empty")

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

    # assign values to variables if present, otherwise assign 'None'
    mongo_dict["reference"] = response.get("reference").split(':')[1] or None
    # mongo_dict["text"] = response.get("content").get("CONTENT_URL").get("DRECONTENT") or None

    manifestation = response.get('content').get('NOTICE').get('MANIFESTATION') or None
    # check every tag that could be empty in a judgment file; avoids get() on NoneTypes
    if manifestation:
        mongo_dict["keywords"] = manifestation.get('MANIFESTATION_CASE-LAW_KEYWORDS') or None
        mongo_dict['subject'] = manifestation.get('"MANIFESTATION_CASE-LAW_SUBJECT') or None
        mongo_dict['endorsements'] = manifestation.get('MANIFESTATION_CASE-LAW_ENDORSEMENTS') or None

        parties = manifestation.get('MANIFESTATION_CASE-LAW_PARTIES')
        if parties:
            mongo_dict['party names'] = parties.get('VALUE') or None

        grounds = manifestation.get('MANIFESTATION_CASE-LAW_GROUNDS')
        if grounds:
            mongo_dict['grounds'] = grounds.get('VALUE') or None

        costs = manifestation.get('MANIFESTATION_CASE-LAW_DECISIONS')
        if costs:
            mongo_dict['decisions on costs'] = costs.get('VALUE') or None

        operative = manifestation.get('MANIFESTATION_CASE-LAW_OPERATIVE_PART')
        if operative:
            mongo_dict['operative part'] = operative.get('VALUE') or None
    
    work = response.get('content').get('NOTICE').get('WORK')
    if work:
        mongo_dict['celex'] = work.get('ID_CELEX').get('VALUE') or None

        author_data = work.get('WORK_CREATED_BY_AGENT') or None
        if author_data:
            list_id = []
            for data in author_data:
                for key, value in data.items():
                    if(key == 'SAMEAS'):    # individual people data are inside a SAMEAS tag it seems
                        list_id.append(value.get('URI').get('IDENTIFIER'))
                    elif(key == 'IDENTIFIER'):
                        list_id.append(value)
            
            _filtered_list_id = list(set(list_id))
            mongo_dict['author'] = _filtered_list_id
        
        subject_matter = work.get('RESOURCE_LEGAL_IS_ABOUT_SUBJECT-MATTER') or None
        if subject_matter:
            list_id = []
            for data in subject_matter:
                for item in data.values():
                    list_id.append(item.get('IDENTIFIER'))
                
            # remove duplicates
            _filtered_list_id = list(set(list_id))
            mongo_dict['subject'] = _filtered_list_id
        
        # memberlist = work.get('CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST') or None
        # if memberlist:
        #     concept = memberlist.get('CASE-LAW_IS_ABOUT_CONCEPT') or None # this can be either a list or dict
        #     if concept:
        #         print(concept)


    print(mongo_dict)



    # mongo_json = {
    #         "reference":            reference,
    #         # "text" :                response["content"]["CONTENT_URL"]["DRECONTENT"],
    #         # "keywords":             response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_KEYWORDS"],
    #         # "party names":          response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_PARTIES"],
    #         # "subject":              response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_SUBJECT"],
    #         # "endorsements":         response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_ENDORSEMENTS"],
    #         # "grounds":              response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_GROUNDS"]["VALUE"],
    #         # "decisions on costs":   response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_DECISIONS"]["VALUE"],
    #         # "operative part":       response["content"]["NOTICE"]["MANIFESTATION"]["MANIFESTATION_CASE-LAW_OPERATIVE_PART"]["VALUE"],
    #         # "celex":                response["content"]["NOTICE"]["WORK"]["ID_CELEX"]["VALUE"],
    #         # "author":               response["content"]["NOTICE"]["WORK"]["WORK_CREATED_BY_AGENT"],
    #         # "subject matter":       response["content"]["NOTICE"]["WORK"]["RESOURCE_LEGAL_IS_ABOUT_SUBJECT-MATTER"],
    #         # "case law directory":   response["content"]["NOTICE"]["WORK"]["CASE-LAW_IS_ABOUT_CONCEPT.MEMBERLIST"]["CASE-LAW_IS_ABOUT_CONCEPT"],
    #         # "ecli":                 response["content"]["NOTICE"]["WORK"]["ECLI"]["VALUE"],
    #         # "document date":        response["content"]["NOTICE"]["WORK"]["WORK_DATE_DOCUMENT"]["VALUE"],
    #         # "case affecting":       
    #         # "applicant":            
    #         # "defendant":
    #         # "affected case":
    #         # "procedure type":
    #     }
