from mgapi.mgapi import Api as MailgunApi
import argparse
import config

parser = argparse.ArgumentParser(description="Mailgun Send")

arguments = {
    "to": "--to",
    "subject": "--subject",
    "tag": "--tag",
    "html": "--html",
    "text": "--text",
}

parser.add_argument(arguments["to"]      , help="To mail filed")
parser.add_argument(arguments["subject"] , help="Subject mail field")
parser.add_argument(arguments["tag"]     , help="Tracking tag")
parser.add_argument(arguments["html"]    , help="Path to HTML file with mail template")
parser.add_argument(arguments["text"]    , help="Path to TEXT file with mail template")
args = parser.parse_args()

class Send(object):

    def __init__(self, to, subject, tag, html, text):
        self.api     = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)
        self.From    = config.MG_FROM
        self.to      = to
        self.subject = subject
        self.tag = tag

        with open(html, "rb") as source:
            self.html = source.read()
            source.close()
            print("[+] HTML version read successfully")

        with open(text, "rb") as source:
            self.text = source.read()
            source.close()
            print("[+] TEXT version read successfully")

    def printConfig(self):
        print("From    :", self.From)
        print("To      :", self.to)
        print("Subject :", self.subject)
        print("Tag     :", self.tag)
        print("HTML    :", len(self.html), "bytes")
        print("TEXT    :", len(self.text), "bytes")

    def send(self):
        sending_options = self.api.ret_additional_sending_options(tracking=True)

        delivery_time_hours   = int(input("Delivery time (hours): "))
        delivery_time_minutes = int(input("Delivery time (minutes): "))

        sending_options["o:deliverytime"] = self.api.nowRFC2822(
            hours=delivery_time_hours,
            minutes=delivery_time_minutes
        )
        sending_options["o:tag"] = self.tag.split(";")

        print("RFC2822 delivery time:", sending_options["o:deliverytime"])
        print("Mailing Tags         :", sending_options["o:tag"])

        choice = input("Proceed ? ( yes / no )\n> ")
        if choice.lower() != "yes":
            exit(0)

        des, ser = self.api.send_single_message(
            From=self.From,
            to=self.to,
            subject=self.subject,
            html=self.html,
            text=self.text,
            additional_sending_options=sending_options
        )
        print(ser)

argparse_success = True
if (not args.to):      argparse_success = False;
if (not args.subject): argparse_success = False;
if (not args.tag):     argparse_success = False;
if (not args.html):    argparse_success = False;
if (not args.text):    argparse_success = False;

if not argparse_success:
    print("[-] Mandatory arguments:")
    args_print = list(map(lambda x: "%s=\"\"" % x, arguments.values()))
    print(" ".join(args_print))
    exit(0)

send_object = Send(
    args.to,
    args.subject,
    args.tag,
    args.html,
    args.text
)

send_object.printConfig()
send_object.send()
