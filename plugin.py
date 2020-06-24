import lxml.etree
from zeep import Plugin

# Adapated to python3 from https://stackoverflow.com/questions/48655638/python-zeep-send-un-escaped-xml-as-content
class prevent_escaping_characters_in_cdata(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        xml_string = lxml.etree.tostring(envelope, encoding="unicode")
        xml_string = xml_string.replace("&lt;", "<")
        xml_string = xml_string.replace("&gt;", ">")
        parser = lxml.etree.XMLParser(strip_cdata=False)
        new_envelope = lxml.etree.XML(xml_string, parser=parser)
        return new_envelope, http_headers
