from email.utils import parseaddr
import socket
import requests
from dotenv import load_dotenv
import os
import unicodedata
load_dotenv()
# Main phishing check function
# Args:
#       dict_email: type dict, expected format {'subject': '__', 'preheader_text':'__',
#       'sender_info':'__', 'recipient_info': '__', 'date_time': '__', 'body': '__', 'footer': '__'}
#       make value = None if information not available
#       dict_tests: type dict, expected format {'test_1': 1, 'test_2': 0}
#       used to trigger different tests into the function. 1 means test it, 0 means do not test it. Example, tests= {'url_test': 1, 'sender_reputation_test': 0}
#       Accepted inputs for dict_tests: url_test, sender_reputation_test, attachment_test, grammar_test, tone_test
#       attachments: a list with the relative address of the attachments downloaded from the email. attachments = ['location/file1.x', 'location/file2.x']


def is_phishing(dict_email, dict_tests, attachments=None):
    # Variable representing how many tests have tested positive for phishing (0-5 range)
    # if a test comes back positive, the function will add +1 to is_phishing
    # if is_phishing >= 2, return true to phishing
    is_phishing = 0

    # email extraction
    subject = dict_email['subject']
    preheader_text = dict_email['preheader_text']
    sender_info = dict_email['sender_info'].strip()
    date_time = dict_email['date_time']
    body = dict_email['body']
    footer = dict_email['footer']

    # Functions Calls
    # -- is_reputable(): checks if sender email has reputable domain from database. Checks both a scammer email list and a reputable domain table
    if sender_info != None and dict_tests['sender_info'] == 1:
        try:
            is_phishing += is_reputable(sender_info)
        except TypeError as e:
            print("Did not receive an int as response at is_reputable")

    return is_phishing


def clean_email(email):
    email = email.strip()
    email = "".join(ch for ch in email if unicodedata.category(ch)[0] != "C")
    return email


def is_reputable(sender_info):
    # This function uses SPAMHAUS API. It sends the sender email address to their DBL and uses certain IP addresses to specify what they were blacklisted as
    # Function returns 0 if domain was not found in DBL and 1 if it was.

    # cumulative sum from SPAMHAUS test, and HIBP tests. If one of the tests comes back positive (phishing), the function will return 1.
    # each positive test is worth 0.5
    test_results = 0

    SPAMHAUS_CODES = {
        "127.0.1.2": "Spam domain",
        "127.0.1.4": "Phishing domain",
        "127.0.1.5": "Malware domain",
        "127.0.1.6": "Botnet C&C domain",
        "127.0.1.102": "Abused legit domain (compromised)",
        "127.0.1.103": "Abused legit domain (malware)",
        "127.0.1.104": "Abused legit domain (phishing)"
    }
    domain = sender_info.strip().split(
        '@')[-1] if '@' in sender_info else None  # retrieves domain from email

    print("extracted domain: ", domain)
    try:
        lookup = f"{domain}.dbl.spamhaus.org"  # generates lookup host link
        # the result will be one of the ip addresses from SPAMHAUS_CODES or an error will be raised if domain not in DBL
        result = socket.gethostbyname(lookup)

        if result in SPAMHAUS_CODES:
            print(f"Domain {domain} is blacklisted: {SPAMHAUS_CODES[result]}")
            test_results = test_results + 0.5
        else:
            print(
                f"Domain {domain} is blacklisted but unknown category ({result})")
    except socket.gaierror as e:
        print(f"Domain {domain} lookup failed: {e}")

    HIBP_API_KEY = os.getenv('HIBP_API_KEY')
    HIBP_HEADER = {
        "hibp-api-key": HIBP_API_KEY,
        "User-Agent": "MailScraper"
    }
    cleaned_email = clean_email(sender_info)
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{cleaned_email}"

    response = requests.get(url, headers=HIBP_HEADER)

    if response.status_code == 200:
        breaches = response.json()
        print(
            f"WARNING: {cleaned_email} has been found in {len(breaches)} breaches.")
        for breach in breaches:
            print(f"- {breach.get('Name', 'Unknown')} ({breach.get('BreachDate', 'No Date')}) - {breach.get('Description', 'No Description')}")
            test_results = test_results + 0.5
    elif response.status_code == 404:
        print(f"{cleaned_email} is safe (no known breaches).")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    if test_results >= 0.5:
        return 1
    else:
        return 0


def is_attachment_unsafe(attachments):
    return 1


def is_url_unsafe(body):
    return 1


def is_grammar_bad(subject, body, footer):
    return 1


def is_urgent(subject, body, footer):
    return 1


test_dict_email = {'subject': None, 'preheader_text': None, 'sender_info': 'hunterleaguecanal@gmail.com',
                   'recipient_info': None, 'date_time': None, 'body': None, 'footer': None}
test_dict_tests = {'sender_info': 1}

print(is_phishing(test_dict_email, test_dict_tests))
