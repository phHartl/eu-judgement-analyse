# Zeep is a python soap client
from zeep import Client
from zeep import xsd

from bs4 import BeautifulSoup as bs

import requests
import configparser
import io
import json

from plugin import prevent_escaping_characters_in_cdata
from request_parser import parse_to_mongo_format

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
parse_to_mongo_format(response)

root = bs(response.content, "lxml", from_encoding = 'UTF-8')
response_file = open("response.txt", "w+", encoding='UTF8')
response_file.write(str(root.prettify()))