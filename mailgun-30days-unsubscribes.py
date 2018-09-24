from mgapi.mgapi import Api as MailgunApi
from email.utils import parsedate
from datetime import datetime, timedelta
import time
import argparse
import config
import pprint as pp
import time
import os

parser = argparse.ArgumentParser(description="Mailgun 30 days unsubscribes")
parser.add_argument("--days", help="Number of days")
parser.add_argument("--ext", help="Extension")
args = parser.parse_args()

D_RANGE_ = 31 if not args.days else int(args.days)

def convert_to_datetime(rfc2822):
    t = parsedate(rfc2822)
    return datetime.fromtimestamp(time.mktime(t))

d_range = datetime.now() - timedelta(days=D_RANGE_)

EXT = "txt" if not args.ext else args.ext.strip(".")

domain = config.MG_DOMAIN
api = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)

print("[*] Getting unsubscribes events from last %s days" % D_RANGE_)
print("Now   :", convert_to_datetime(api.nowRFC2822()) )
print("Range :", d_range)

all_unsubscribes = []
print("[*] Getting unsubscribes", end=" ")
des, ser = api.get_unsubscribes(limit=500)
all_unsubscribes += des["items"]
exhausted = False
while not exhausted:
    print(".", end="")
    exhausted, des, ser = api.follow_pagination(Next=des["paging"]["next"])
    all_unsubscribes += des["items"]
print("done. Size:", len(all_unsubscribes))


with open("rezygnacje_ostatnie_%s_dni.txt" % D_RANGE_, "wb") as dest:
    for unsub in all_unsubscribes:
        d_unsub = convert_to_datetime(unsub["created_at"])
        if d_unsub > d_range:
            tmp = "%s\r\n" % unsub["address"]
            dest.write(tmp.encode("utf8"))
    dest.close()
