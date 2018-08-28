from mgapi.mgapi import Api as MailgunApi
import pprint as pp
import config

# GET /{domain}/tags/{tag}	get_tags

class Report(object):

    def __init__(self, tag):
        self.api = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)
        self.tag = tag
        self.data = {}

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

        pp.pprint(self.data)


report = Report("DevTest")
report.gather()
