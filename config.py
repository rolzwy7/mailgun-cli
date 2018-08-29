import json
import pprint as pp

json_config_path = "E:\\mailgun.json"

###JSON fields
# domain <str>
# company_name <str>
# private_key <str>
# exclude_emails <list>
# exclude_emails_contain <list>
# exclude_dns_check <list>
# company_logo_url <str>

json_config = None

try:
    with open(json_config_path, "r") as source:
        json_config = json.loads(source.read())
        print("[ JSON Config File ]")
        pp.pprint(json_config)
except Exception as e:
    print("Error:", e)
    exit(0)

if json_config is None:
    print("[-] Failed to read cofign from JSON file")
    exit(0)

MG_DOMAIN       = "{domain}".format(
    domain=json_config["domain"]
)
MG_PRIVATE_KEY  = "{private_key}".format(
    private_key=json_config["private_key"]
)
MG_FROM         = "{company_name} <mailing@{domain}>".format(
    company_name=json_config["company_name"],
    domain=MG_DOMAIN
)

MG_LOGO = json_config["company_logo_url"]

RE_EMAIL = b"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

# Exclude email from mailing if whole email match
EXCLUDE_EMAILS         = json_config["exclude_emails"]

# Exclude email from mailing if part of email match
EXCLUDE_EMAILS_CONTAIN = json_config["exclude_emails_contain"]

# Exlude email from DNS check if part of email match or whole email match
EXCLUDE_DNS_CHECK      = json_config["exclude_dns_check"]

print("\n[ BASIC ]")
print("Domain     :", MG_DOMAIN)
print("Private Key:", MG_PRIVATE_KEY)
print("From       :", MG_FROM)

print("\n\n")
