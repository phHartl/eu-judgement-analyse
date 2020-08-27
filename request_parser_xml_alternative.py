from bs4 import BeautifulSoup as bs

import unicodedata

DEBUG = 1


def parse_response_for_mongo_xml(response):
    root = bs(response.content, "lxml", from_encoding='UTF-8')
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
        mongo_dict['keywords'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_keywords')
        mongo_dict['subject'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_subject')
        mongo_dict['endorsements'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_endorsements')
        mongo_dict['operative part'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_operative_part')
        mongo_dict['decisions on cost'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_costs_decisions')
        mongo_dict['law grounds'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_grounds')
        mongo_dict['parties'] = find_simple_value_tag(
            metadata_root, 'manifestation_case-law_parties')
        mongo_dict['celex'] = find_simple_value_tag(metadata_root, 'id_celex')
        mongo_dict['ecli'] = find_simple_value_tag(metadata_root, 'ecli')
        mongo_dict['document date'] = find_simple_value_tag(
            metadata_root, 'work_date_document')

        mongo_dict['author'] = find_multiple_sub_elements_for_multiple_tag(
            metadata_root, 'work_created_by_agent', 'identifier')
        mongo_dict['subject matter'] = find_multiple_sub_elements_for_multiple_tag(
            metadata_root, 'resource_legal_is_about_subject-matter', 'preflabel')
        mongo_dict['case law directory'] = find_multiple_sub_elements(
            metadata_root, 'case-law_is_about_concept.memberlist', 'preflabel')
        mongo_dict['case affecting'] = find_multiple_sub_elements(
            metadata_root, 'case-law_confirms_resource_legal', 'identifier')
        mongo_dict['applicant'] = find_multiple_sub_elements(
            metadata_root, 'case-law_requested_by_agent', 'identifier')
        mongo_dict['defendant'] = find_multiple_sub_elements(
            metadata_root, 'case-law_defended_by_agent', 'identifier')
        mongo_dict['procedure type'] = find_multiple_sub_elements(
            metadata_root, 'case-law_has_type_procedure_concept_type_procedure', 'identifier')

        # Affected by case got three different tags
        affected_by_case_tags = metadata_root.find_all(["resource_legal_preliminary_question-submitted_by_communication_case",
                                                        "resource_legal_preliminary_question-submitted_by_communication_case_new", "resource_legal_interpretation_requested_by_case-law", ])

        if(affected_by_case_tags is not None):
            data = set()
            for element in affected_by_case_tags:
                if(element is not None):
                    for identifier in element.find_all('identifier'):
                        data.add(identifier.text)
            mongo_dict['affected case'] = data
    return mongo_dict
    # print(mongo_dict)
