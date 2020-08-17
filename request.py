# Zeep is a python soap client
from zeep import Client
from zeep import xsd

from bs4 import BeautifulSoup as bs

import requests
import configparser
import io
import json
import xmltodict

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

# Traverse xml with beautifulSoup and get html tags to build a structure on our own?
# root = bs(response.content, "lxml")
# response_file = open("response.txt", "w+")
# response_file.write(str(root.prettify()))

# Or convert response to one huge dict and use this to get information?
data_dict = xmltodict.parse(response.content)
results_dict = data_dict["S:Envelope"]["S:Body"]["searchResults"]["result"]

# Simple implementation to write every result to a separate .json - however empty tags are not returned by the API so we need to modify this dic in the future
counter = 0
for result in results_dict:
    json_data = json.dumps(results_dict[counter], indent=4)
    with open("data_" + str(counter) +".json", "w") as json_file:
        json_file.write(json_data)
        json_file.close()
    counter += 1
