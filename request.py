# Zeep is a python soap client
from zeep import Client
from zeep import xsd

import requests
import configparser
import io

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
response = client.service.doQuery(
    expertQuery="<![CDATA[DTS_SUBDOM = EU_CASE_LAW AND ((COMPOSE = ENG) WHEN (EMBEDDED_MANIFESTATION-TYPE = html OR xhtml)) AND CASE_LAW_SUMMARY = false AND (DTT=C? AND DTS = 6) AND (FM_CODED = JUDG)]]>",
    page=1,
    pageSize=5,
    searchLanguage="en",
    _soapheaders=[header_value],
)

#Print id from first response for demo puroposes
print(response.result[0].reference)
