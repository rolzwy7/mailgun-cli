from mgapi.mgapi import Api as MailgunApi
import argparse
import config
import pprint as pp
import time
import os

parser = argparse.ArgumentParser(description="Mailgun Supressions")
parser.add_argument("dir", help="Destination (dirpath)")
parser.add_argument("--ext", help="Extension")
args = parser.parse_args()

EXT = "txt" if not args.ext else args.ext.strip(".")

domain = config.MG_DOMAIN
api = MailgunApi(domain=config.MG_DOMAIN, private_key=config.MG_PRIVATE_KEY)

all_complaints   = []
all_unsubscribes = []
all_bounces      = []

print("[*] Getting unsubscribes", end=" ")
des, ser = api.get_unsubscribes(limit=500)
all_unsubscribes += des["items"]
exhausted = False
while not exhausted:
    print(".", end="")
    exhausted, des, ser = api.follow_pagination(Next=des["paging"]["next"])
    all_unsubscribes += des["items"]
print("done. Size:", len(all_unsubscribes))

print("[*] Getting complaints", end=" ")
des, ser = api.get_complaints(limit=500)
all_complaints += des["items"]
exhausted = False
while not exhausted:
    print(".", end="")
    exhausted, des, ser = api.follow_pagination(Next=des["paging"]["next"])
    all_complaints += des["items"]
print("done. Size:", len(all_complaints))

print("[*] Getting bounces", end=" ")
des, ser = api.get_bounces(limit=500)
all_bounces += des["items"]
exhausted = False
while not exhausted:
    print(".", end="")
    exhausted, des, ser = api.follow_pagination(Next=des["paging"]["next"])
    all_bounces += des["items"]
print("done. Size:", len(all_bounces))

domain_under = "__".join([domain.replace(".", "_"), time.strftime("%d_%m_%Y"), ".%s" % EXT])
print(domain_under)
path_complaints   = os.path.join(args.dir, "skargi_%s" % domain_under)
path_unsubscribes = os.path.join(args.dir, "odsubskrybowalo_%s" % domain_under)
path_bounces      = os.path.join(args.dir, "odbicia_twarde_%s" % domain_under)

print("Complaints   :", path_complaints)
print("Unsubscribes :", path_unsubscribes)
print("Bounces      :", path_bounces)

with open(path_unsubscribes, "wb") as dest:
    for e in all_unsubscribes:
        dest.write(e["address"].encode("utf8"))
        dest.write(b"\r\n")
    dest.close()
print("[*] Saved unsubscribes")

with open(path_complaints, "wb") as dest:
    for e in all_complaints:
        dest.write(e["address"].encode("utf8"))
        dest.write(b"\r\n")
    dest.close()
print("[*] Saved complaints")

with open(path_bounces, "wb") as dest:
    for e in all_bounces:
        dest.write(e["address"].encode("utf8"))
        dest.write(b"\r\n")
    dest.close()
print("[*] Saved bounces")
