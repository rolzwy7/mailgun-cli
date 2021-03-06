from mgapi.mgapi import Api as MailgunApi
import argparse
import config
import os
import re
import string
import requests

parser = argparse.ArgumentParser(description="Mailgun Emails")
parser.add_argument("emails_directory", help="Emails directory")
args = parser.parse_args()

class EmailParser(object):

    def __init__(self, emails_directory):
        self.emails_directory     = emails_directory
        self.email_files          = []
        self.emails_all           = []

        self.mailgun_bounces      = []
        self.mailgun_unsubscribes = []
        self.mailgun_complaints   = []

        self.re_obj               = re.compile(config.RE_EMAIL)
        self.api                  = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)

    def getEmailFiles(self):
        print("[*] Getting email files")
        for r, d, f in os.walk(self.emails_directory):
            self.email_files += list(map(lambda x: os.path.join(r, x), f))
        for email_file in self.email_files:
            print("-> source:", email_file)

    def getMailgunBounces(self):
        print("[*] Getting bounces")
        print(" - Sending request...", end="")
        des, ser = self.api.get_bounces(limit=1000)
        print("got %s bounces" % len(des["items"]))
        self.mailgun_bounces += des["items"]
        exhausted = False
        while not exhausted:
            print(" - Sending request...", end="")
            exhausted, des, ser = self.api.follow_pagination(Next=des["paging"]["next"])
            print("got %s bounces" % len(des["items"]))
            self.mailgun_bounces += des["items"]

        tmp = []
        for email in self.mailgun_bounces:
            tmp.append(email["address"])
        self.mailgun_bounces = list(set(tmp))
        print("\n[*] Got %s bounces" % len(self.mailgun_bounces))
    def getMailgunUnsubscribes(self):
        print("[*] Getting unsubscribes")
        print(" - Sending request...", end="")
        des, ser = self.api.get_unsubscribes(limit=1000)
        print("got %s unsubscribes" % len(des["items"]))
        self.mailgun_unsubscribes += des["items"]
        exhausted = False
        while not exhausted:
            print(" - Sending request...", end="")
            exhausted, des, ser = self.api.follow_pagination(Next=des["paging"]["next"])
            print("got %s unsubscribes" % len(des["items"]))
            self.mailgun_unsubscribes += des["items"]
        tmp = []
        for email in self.mailgun_unsubscribes:
            tmp.append(email["address"])
        self.mailgun_unsubscribes = list(set(tmp))
        print("\n[*] Got %s unsubscribes" % len(self.mailgun_unsubscribes))
    def getMailgunComplaints(self):
        print("[*] Getting complaints")
        print(" - Sending request...", end="")
        des, ser = self.api.get_complaints(limit=1000)
        print("got %s complaints" % len(des["items"]))
        self.mailgun_complaints += des["items"]
        exhausted = False
        while not exhausted:
            print(" - Sending request...", end="")
            exhausted, des, ser = self.api.follow_pagination(Next=des["paging"]["next"])
            print("got %s complaints" % len(des["items"]))
            self.mailgun_complaints += des["items"]
        tmp = []
        for email in self.mailgun_complaints:
            tmp.append(email["address"])
        self.mailgun_complaints = list(set(tmp))
        print("\n[*] Got %s complaints" % len(self.mailgun_complaints))

    def excludeCheck(self, email):
        # Check if startswith digit
        ch_falg = False
        for ch in string.digits:
            if str(email, "utf8").startswith(ch):
                ch_falg = True
        if ch_falg:
            print("    - excluded (sd):", str(email, "utf8"))
            return True;

        # Check if email exclude
        if str(email, "utf8") in config.EXCLUDE_EMAILS:
            print("    - excluded (ex):", str(email, "utf8"))
            return True

        # Check if excluded word in email
        for exclude in config.EXCLUDE_EMAILS_CONTAIN:
            if exclude in str(email, "utf8"):
                print("    - excluded (ex):", str(email, "utf8"))
                return True

        # Check if in mailgun bounces
        if str(email, "utf8") in self.mailgun_bounces:
            print("    - excluded (mg):", str(email, "utf8"))
            return True

        # Check if in mailgun unsubscribes
        if str(email, "utf8") in self.mailgun_unsubscribes:
            print("    - excluded (un):", str(email, "utf8"))
            return True

        # Check if in mailgun complaints
        if str(email, "utf8") in self.mailgun_complaints:
            print("    - excluded (cm):", str(email, "utf8"))
            return True

    def gatherAllEmails(self):
        print("[*] Gathering from:")
        for email_file in self.email_files:
            print("\n >", email_file)
            with open(email_file, "rb") as source:
                for line in source:
                    match = self.re_obj.match(line)
                    f, t = match.span() if match is not None else (0,0)
                    email = line[f:t]

                    # Exclusions
                    if len(email) != 0:
                        if self.excludeCheck(email):
                            continue

                        self.emails_all.append(str(email, "utf8"))

        with_duplicates = self.emails_all
        without_duplicates = list(set(self.emails_all))

        len_all = len(with_duplicates)
        len_duplicates = len(with_duplicates) - len(without_duplicates)
        len_unique      = len(self.emails_all)

        self.emails_all = without_duplicates
        self.emails_all = sorted(self.emails_all, key=str.lower)

        print("All Emails : ", len_all)
        print("Unique     : ", len(without_duplicates))
        print("Duplicates : ", len_duplicates)

    def writeEmails(self):
        filepath = "Done_Emails.txt"
        with open(filepath, "wb") as dest:
            for email in self.emails_all:
                dest.write(email.encode("utf8") + b"\n")
            dest.close()
        print("\n[+] Emails saved")

email_parser_object = EmailParser(args.emails_directory)

email_parser_object.getEmailFiles()

email_parser_object.getMailgunComplaints()
email_parser_object.getMailgunUnsubscribes()
email_parser_object.getMailgunBounces()

email_parser_object.gatherAllEmails()
email_parser_object.writeEmails()


# # Check SMTP servers
# from email_check import dns_check
# _edc = config.EXCLUDE_DNS_CHECK
# email_all_temp = []
#
# for email in email_parser_object.emails_all:
#     domain_temp = email.split("@")[-1]
#
#     # Trusted domain
#     if domain_temp in _edc:
#         print("Trusted      :", email)
#         email_all_temp.append(email)
#         continue
#
#     # mx check
#     has_mx = dns_check.validate_email(email, check_mx=True, verify=True)
#     if not has_mx:
#         print("Mx not found :", email)
#     else:
#         print("Mx found     :", email)
#         _edc.append(domain_temp)
#         email_all_temp.append(email)
