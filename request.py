# Zeep is a python soap client
from zeep import Client
from zeep import xsd

from bs4 import BeautifulSoup as bs

import requests
import configparser
import io
import json

from plugin import prevent_escaping_characters_in_cdata

config = configparser.ConfigParser()
config.read("config.ini")

client = Client(
    wsdl="https://eur-lex.europa.eu/eurlex-ws?wsdl",
    plugins=[prevent_escaping_characters_in_cdata()],
)

# Soap headers are not correctly defined inside the wsdl - define them hear manually
header = xsd.Element(
    "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security",
    xsd.ComplexType(
        [
            xsd.Element(
                "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}UsernameToken",
                xsd.ComplexType(
                    [
                        xsd.Element(
                            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username",
                            xsd.String(),
                        ),
                        xsd.Element(
                            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Password",
                            xsd.String(),
                        ),
                    ]
                ),
            ),
        ]
    ),
)

header_value = header(
    UsernameToken={
        "Username": config.get("eur-lex", "username"),
        "Password": config.get("eur-lex", "password"),
    }
)

def print_simple_value_tags(metadata_root, tag):
    if(metadata_root.find(tag) is not None):
        print(metadata_root.find(tag).value.string)


# Excute the query - zeep automatically generates an object with the doQuery property defined by eur-lex
# We need to use a raw request here (https://stackoverflow.com/questions/57730340/how-to-fix-str-object-has-no-attribute-keys-in-python-zeep-module)
with client.settings(raw_response=True):
    response = client.service.doQuery(
        expertQuery="<![CDATA[SELECT TI, TE, IX, I1, I2, VS , MO, CO, DI, DN, AU, CT, RJ, RJ_NEW, ECLI, DD, AJ, LB, AP, DF, CD, PR WHERE DTS_SUBDOM = EU_CASE_LAW AND CASE_LAW_SUMMARY = false AND (DTT=C? AND DTS = 6) AND (FM_CODED = JUDG)]]>",
        page=1,
        pageSize=2,
        searchLanguage="en",
        _soapheaders=[header_value],
    )

# Traverse xml with beautifulSoup - prints all relevant tags for our analysis into the command line
# TODO: Insert each string into dictionary which later on gets inserted into our mongo database
root = bs(response.content, "lxml", from_encoding = 'UTF-8')
for element in root.find_all('result'):
    # ID
    print(element.reference.string.split(":")[1])
    # Fulltext
    # print(element.content.content_url.drecontent.string)
    metadata_root = element.content.notice
    # Decisions on cost
    print_simple_value_tags(metadata_root, 'manifestation_case-law_costs_decisions')
    # Law grounds
    print_simple_value_tags(metadata_root, 'manifestation_case-law_grounds')
    # Operative part
    print_simple_value_tags(metadata_root, 'manifestation_case-law_operative_part')
    # Parties
    print_simple_value_tags(metadata_root, 'manifestation_case-law_parties')
    # ID CELEX
    print_simple_value_tags(metadata_root, 'id_celex')

    # Author
    if(metadata_root.find('work_created_by_agent') is not None):
        print(metadata_root.find('work_created_by_agent').find_all('identifier'))

    # Subject matter
    if(metadata_root.find('resource_legal_is_about_subject-matter') is not None):
        print(metadata_root.find('resource_legal_is_about_subject-matter').find_all('identifier'))
        print(metadata_root.find('resource_legal_is_about_subject-matter').find_all('preflabel'))
    
     # Case law directory code
    if(metadata_root.find('case-law_is_about_concept.memberlist') is not None):
        print(metadata_root.find('case-law_is_about_concept.memberlist').find_all('identifier'))
        print(metadata_root.find('case-law_is_about_concept.memberlist').find_all('preflabel'))

    # Case affecting
    if(metadata_root.find('case-law_confirms_resource_legal') is not None):
        print(metadata_root.find('case-law_confirms_resource_legal').find_all('identifier'))
    # ECLI
    print_simple_value_tags(metadata_root, 'ecli')
    # Date
    print_simple_value_tags(metadata_root, 'work_date_document')
    
    # Case affecting
    if(metadata_root.find('case-law_confirms_resource_legal') is not None):
        print(metadata_root.find('case-law_confirms_resource_legal').find_all('identifier'))

    # Applicant
    if(metadata_root.find('case-law_requested_by_agent') is not None):
        print(metadata_root.find('case-law_requested_by_agent').find_all('identifier'))
        print(metadata_root.find('case-law_requested_by_agent').find_all('preflabel'))

    # Defendant
    if(metadata_root.find('case-law_defended_by_agent') is not None):
        print(metadata_root.find('case-law_defended_by_agent').find_all('identifier'))
        print(metadata_root.find('case-law_defended_by_agent').find_all('preflabel'))

     # Affected by case
    if(metadata_root.find_all(['resource_legal_preliminary_question-submitted_by_communication_case', 'resource_legal_preliminary_question-submitted_by_communication_case_new', 'resource_legal_interpretation_requested_by_case-law']) is not None):
        for element in metadata_root.find_all(['resource_legal_preliminary_question-submitted_by_communication_case', 'resource_legal_preliminary_question-submitted_by_communication_case_new', 'resource_legal_interpretation_requested_by_case-law']):
                if(element is not None):
                    print(element.find_all('identifier'))

    # Type of procedure
    if(metadata_root.find('case-law_has_type_procedure_concept_type_procedure') is not None):
        print(metadata_root.find('case-law_has_type_procedure_concept_type_procedure').find_all('identifier'))
        print(metadata_root.find('case-law_has_type_procedure_concept_type_procedure').find_all('preflabel'))


response_file = open("response.txt", "w+")
response_file.write(str(root.prettify()))