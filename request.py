import configparser
import functools
import sys
import timeit
import math

from zeep import Client
from zeep import xsd
from bs4 import BeautifulSoup as bs

# from mongo import insert_doc
from plugin import prevent_escaping_characters_in_cdata
from request_parser import parse_response_for_mongo
from request_parser_xml_alternative import parse_response_for_mongo_xml


WRITE_TO_FILE_DEBUG = 0

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


def request_data(_page=1, _page_size=1):
    # Excute the query - zeep automatically generates an object with the doQuery property defined by eur-lex
    # We need to use a raw request here (https://stackoverflow.com/questions/57730340/how-to-fix-str-object-has-no-attribute-keys-in-python-zeep-module)
    with client.settings(raw_response=True):
        response = client.service.doQuery(
            expertQuery="<![CDATA[SELECT TI_DISPLAY, TE, IX, I1, I2, VS , MO, CO, DI, DN, AU, CT, RJ, RJ_NEW,  ECLI, DD,  AJ,  LB, AP, DF, CD, PR WHERE DTS_SUBDOM = EU_CASE_LAW AND (EMBEDDED_MANIFESTATION-TYPE = html OR xhtml or pdf) AND CASE_LAW_SUMMARY = false AND (DTT=C? AND DTS = 6) AND (FM_CODED = JUDG) ORDER BY DN ASC]]>",
            page=_page,
            pageSize=_page_size,
            searchLanguage="en",
            _soapheaders=[header_value],
        )
        return response


# This function can be called to crawl judgments at once automatically. Use with caution!
def full_crawl():
    # Find out how much data we need to crawl for our query. Doesn't really make sense to convert to a dict here.
    response = request_data(1, 1)
    root = bs(response.content, "lxml", from_encoding="UTF-8")
    total_documents = root.find("totalhits").text

    for i in range(1, math.ceil(int(total_documents) / 100) + 1):
        response = request_data(100, i)
        docs = parse_response_for_mongo(response)
        for doc in docs:
            insert_doc(doc)


def main():
    _page = 1
    _page_size = 10
    _dump_mode = None
    _debug_mode = False

    for arg in sys.argv[1:]:
        if arg == "debug":
            _debug_mode = True
        elif arg.startswith("page="):
            val = arg.split("page=", 1)[1]
            _page = val
        elif arg.startswith("pagesize="):
            val = arg.split("pagesize=", 1)[1]
            _page_size = val
        elif arg.startswith("dump="):
            val = arg.split("dump=", 1)[1]
            if val == "all" or val == "parse" or val == "response":
                _dump_mode = val

    response = request_data(_page, _page_size)
    docs = parse_response_for_mongo(
        response, debug_mode=_debug_mode, dump_mode=_dump_mode
    )
    # for doc in docs:
    #     insert_doc(doc)

    if WRITE_TO_FILE_DEBUG:
        from bs4 import BeautifulSoup as bs

        root = bs(response.content, "lxml", from_encoding="UTF-8")
        response_file = open("response.txt", "w+", encoding="UTF8")
        response_file.write(str(root.prettify()))


if __name__ == "__main__":
    main()

# Benchmark section:
# t1 = timeit.Timer(functools.partial(parse_response_for_mongo, response))
# print(t1.timeit(100))

# t2 = timeit.Timer(functools.partial(parse_response_for_mongo_xml, response))
# print(t2.timeit(100))
