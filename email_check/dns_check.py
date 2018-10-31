import DNS, smtplib

def validate_email(email, check_mx=False,verify=False):
    try:
        check_mx |= verify
        if check_mx:
            if not DNS: raise Exception('For check the mx records or check if the email exists you must have installed pyDNS python package')
            DNS.DiscoverNameServers()
            hostname = email[email.find('@')+1:]
            mx_hosts = DNS.mxlookup(hostname)
            for mx in mx_hosts:
                print("mx:", mx)
                try:
                    smtp = smtplib.SMTP()
                    smtp.connect(mx[1])
                    if not verify: return True
                    status, _ = smtp.helo()
                    if status != 250: continue
                    smtp.mail('')
                    status, _ = smtp.rcpt(email)
                    if status != 250: return False
                    break
                except smtplib.SMTPServerDisconnected: #Server not permits verify user
                    break
                except smtplib.SMTPConnectError:
                    continue
    except (AssertionError, ServerError):
        return False
    return True

def quick_mx_lookup(email):
    DNS.DiscoverNameServers()
    hostname = email[email.find('@')+1:]
    
    try:
        mx_hosts = DNS.mxlookup(hostname)
    except:
        return False

    if len(mx_hosts) != 0:
        return True
    else:
        return False


# for mx in mx_hosts:
#     smtp = smtplib.SMTP()
#     #.. if this doesn't raise an exception it is a valid MX host...
#     try:
#         smtp.connect(mx[1])
#     except smtplib.SMTPConnectError:
#         continue # try the next MX server in list

# def check_has_smtp(email):
#     is_valid = validate_email(email, check_mx=True)
#     return is_valid
#
# def check_email_exist(email):
#     is_valid = validate_email(email, verify=True)
#     return is_valid
