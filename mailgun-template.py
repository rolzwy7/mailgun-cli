from mgapi.mgapi import Api as MailgunApi
from bs4 import BeautifulSoup
import argparse
from premailer import transform
import config
import os

parser = argparse.ArgumentParser(description="Mailgun Template")
parser.add_argument("template_path", help="")
args = parser.parse_args()

class TemplateParser(object):

    def __init__(self, template_path):
        self.template_path = template_path
        with open(template_path, "rb") as source:
            self.raw_html = source.read()
            self.done_html = self.raw_html
            source.close()

    def cutHead(self):
        print("\n[*] Cutting head")
        soup = BeautifulSoup(self.done_html, "html5lib")
        self.done_html = str(soup.find('body')).encode("utf8")

    def unminify(self):
        print("\n[*] Making HTML Pretty")
        soup = BeautifulSoup(self.done_html, "html5lib")
        self.done_html = soup.prettify().encode("utf8")

    def inilineCSS(self):
        print("\n[*] Inlining CSS")
        self.done_html = transform(str(self.done_html, "utf8")).encode("utf8")

    def writeTemplate(self):
        filepath = "Done_%s" % self.template_path.split(os.sep)[-1]
        with open(filepath, "wb") as dest:
            dest.write(self.done_html)
            dest.close()
        print("\n[+] Template saved")


template_parser_object = TemplateParser(args.template_path)
template_parser_object.unminify()
template_parser_object.inilineCSS()
template_parser_object.cutHead()
template_parser_object.writeTemplate()
