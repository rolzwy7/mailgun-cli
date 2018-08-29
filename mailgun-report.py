from mgapi.mgapi import Api as MailgunApi
import pprint as pp
import config
import argparse
import json
import os
import pycountry
from textblob import TextBlob

class Report(object):

    def __init__(self, tag):
        self.api = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)
        self.tag = tag
        self.data = {}
        print("[*] Creating report for:", self.tag)
        self.gather()

    def write_report(self):
        print("[*] Saving report")
        with open(os.path.join("resources", "report_template.html"),"rb") as template:
            template_content = template.read()
            template.close()

        with open("report_%s.html" % self.tag, "wb") as dest:
            report_data = json.dumps(self.data, indent=4, sort_keys=True).encode("utf8")
            report_content = template_content.replace(b"[DATA]", report_data)
            dest.write(report_content)
            dest.close()
        print(" - success")

    def aggregates_countries(self):
        print("- Getting aggregates countries")
        des, ser = self.api.get_tag_aggregates(tag=self.tag, aggregate="countries")
        return des

    def aggregates_providers(self):
        print("- Getting aggregates providers")
        des, ser = self.api.get_tag_aggregates(tag=self.tag, aggregate="providers")
        return des

    def aggregates_devices(self):
        print("- Getting aggregates devices")
        des, ser = self.api.get_tag_aggregates(tag=self.tag, aggregate="devices")
        return des

    def tag_stats(self, event):
        print("- Getting tag stats (event=%s)" % event)
        des, ser = self.api.get_tag_stats(tag=self.tag, event=event)
        return des

    def tag_info(self):
        print("- Getting tag basic info")
        des, ser = self.api.get_tags(tag=self.tag)
        return des

    def gather(self):
        tag_info = self.tag_info()
        if tag_info["justify"]["success"]:
            self.data["tag_info"] = tag_info
        else:
            print(tag_info["justify"]["reason"])

        for event in self.api._EVENTS:
            stats = self.tag_stats(event=event)
            if stats["justify"]["success"]:
                self.data["%s_stats" % event] = stats["stats"]
            else:
                print(stats["justify"]["reason"])

        countries = self.aggregates_countries()
        if countries["justify"]["success"]:
            self.data["countries"] = countries
        else:
            print(countries["justify"]["reason"])

        providers = self.aggregates_providers()
        if providers["justify"]["success"]:
            self.data["providers"] = providers
        else:
            print(providers["justify"]["reason"])

        devices = self.aggregates_devices()
        if devices["justify"]["success"]:
            self.data["devices"] = devices
        else:
            print(devices["justify"]["reason"])

parser = argparse.ArgumentParser(description="Mailgun Report")
parser.add_argument("tag", help="Mailing tag")
args = parser.parse_args()

# Create report
report = Report(args.tag)


data = {
    "tag": report.data["tag_info"],
    "company_logo_url": config.MG_LOGO,

    "accepted": 0,
    "delivered": 0,
    "opened": 0,
    "opened_unique": 0,
    "clicked": 0,
    "clicked_unique": 0,
    "complained": 0,
    "unsubscribed": 0,
    "failed_permanent": 0,
    "failed_temporary": 0,

    "devices": {},
    "providers": {},
    "countries": {},
}


for k, v in report.data["devices"]["device"].items():
    if k == "desktop": device_name = "Urządzenia stacjonarne";
    if k == "mobile": device_name = "Urządzenia mobilne";
    if k == "tablet": device_name = "Tablety";
    if k == "unknown": device_name = "nieznany";

    data["devices"][str(device_name)] = v

for k, v in report.data["countries"]["country"].items():

    save_record = False
    for elem in v.values():
        if elem != 0:
            save_record = True
            break

    if save_record:

        try:
            country_name = pycountry.countries.lookup(k).name
        except Exception as e:
            country_name = "unknown"
            print("[-] Exception:", e)

        blob = TextBlob(country_name)
        country_name = blob.translate(to="pl")

        data["countries"][str(country_name)] = v

for k, v in report.data["providers"]["provider"].items():

    save_record = False
    for elem in v.values():
        if elem != 0:
            save_record = True
            break

    if save_record:
        data["providers"][k] = v

for e in report.data["accepted_stats"]:
    data["accepted"] += e["accepted"]["outgoing"]

for e in report.data["delivered_stats"]:
    data["delivered"] += e["delivered"]["total"]

for e in report.data["opened_stats"]:
    data["opened"] += e["opened"]["total"]
    if "unique" in e["opened"].keys():
        data["opened_unique"] += e["opened"]["unique"]

for e in report.data["clicked_stats"]:
    data["clicked"] += e["clicked"]["total"]
    if "unique" in e["clicked"].keys():
        data["clicked_unique"] += e["clicked"]["unique"]

for e in report.data["complained_stats"]:
    data["complained"] += e["complained"]["total"]

for e in report.data["unsubscribed_stats"]:
    data["unsubscribed"] += e["unsubscribed"]["total"]

for e in report.data["failed_stats"]:
    data["failed_permanent"] += e["failed"]["permanent"]["total"]
    data["failed_temporary"] += e["failed"]["temporary"]["total"]

report.data = data

pp.pprint(data)

report.write_report()
