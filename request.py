import configparser
import math
import sys

from zeep import Client
from zeep import xsd
from bs4 import BeautifulSoup as bs

from mongo import insert_doc
from plugin import prevent_escaping_characters_in_cdata
from request_parser import parse_response_for_mongo

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

# all document languages available in eur-lex
# for a descriptive list, see 13. in https://eur-lex.europa.eu/content/help/faq/intro.html
AVAILABLE_LANGUAGES = ['bg', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'de', 'el', 'hu',
                       'ga', 'it', 'lv', 'lt', 'mt', 'pl', 'pt', 'ro', 'sk', 'sl', 'es', 'sv']


def request_data(page_size=1, page=1, language='en'):
    # Excute the query - zeep automatically generates an object with the doQuery property defined by eur-lex
    # We need to use a raw request here (https://stackoverflow.com/questions/57730340/how-to-fix-str-object-has-no-attribute-keys-in-python-zeep-module)
    with client.settings(raw_response=True):
        response = client.service.doQuery(
            expertQuery="<![CDATA[SELECT TI_DISPLAY, TE, IX, I1, I2, VS , MO, CO, DI, DN, AU, CT, RJ, RJ_NEW,  ECLI, DD,  AJ,  LB, AP, DF, CD, PR WHERE DTS_SUBDOM = EU_CASE_LAW AND (EMBEDDED_MANIFESTATION-TYPE = html OR xhtml or pdf) AND CASE_LAW_SUMMARY = false AND (DTT=C? AND DTS = 6) AND (FM_CODED = JUDG) ORDER BY DN ASC]]>",
            page=page,
            pageSize=page_size,
            searchLanguage=language,
            _soapheaders=[header_value],
        )
        return response


def request_all_data_for_language(lang):
    # Find out how much data we need to crawl for our query. Doesn't really make sense to convert to a dict here.
    response = request_data(1, 1, lang)
    root = bs(response.content, "lxml", from_encoding="UTF-8")
    total_documents = root.find("totalhits").text

    for i in range(1, math.ceil(int(total_documents) / 100) + 1):
        response = request_data(page_size=100, page=i, language=lang)
        docs = parse_response_for_mongo(response, dump_mode="response", iteration_num=i)
        for doc in docs:
            insert_doc(doc, lang)


# This function can be called to crawl judgments at once automatically. Use with caution!
# accepts a single language or an array of languages to request all docs for. default: only english
def request_all_data(languages=['en']):
    if isinstance(languages, list):
        for current_lang in languages:
            if current_lang not in AVAILABLE_LANGUAGES:
                print("REQUEST: '", current_lang, "' is not a valid language.")
            else:
                request_all_data_for_language(current_lang)
    elif type(languages, str):
        request_all_data_for_language(languages)
    else:
        print("REQUEST: request_all_data(): the specified argument is not of type 'list' or 'str'")


def main():
    _page = 1
    _page_size = 10
    _dump_mode = None
    _debug_mode = False
    _language = 'en'

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

    response = request_data( _page_size, _page, _language)
    docs = parse_response_for_mongo(
        response, debug_mode=_debug_mode, dump_mode=_dump_mode
    )
    for doc in docs:
        insert_doc(doc, _language)


if WRITE_TO_FILE_DEBUG:
    from bs4 import BeautifulSoup as bs

    root = bs(response.content, "lxml", from_encoding="UTF-8")
    response_file = open("response.txt", "w+", encoding="UTF8")
    response_file.write(str(root.prettify()))

## Benchmark section:
# t1 = timeit.Timer(functools.partial(parse_response_for_mongo, response))
# print(t1.timeit(100))
# t2 = timeit.Timer(functools.partial(parse_response_for_mongo_xml, response))
# print(t2.timeit(100))

if __name__ == "__main__":
    main()
