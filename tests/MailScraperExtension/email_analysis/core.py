from email.utils import parseaddr
import socket
import requests
from dotenv import load_dotenv
import os
import unicodedata
import base64
import time
load_dotenv()
VIRUS_TOTAL_KEY = os.getenv("VIRUS_TOTAL_KEY")
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
            result = is_reputable(sender_info)
            if result[0] == 0:
                return result[0]
            else:
                is_phishing += result[0]
                breachInfo = result[1]
                breachList = result[2]
                return is_phishing, breachInfo, breachList

        except TypeError as e:
            print("Did not receive an int as response at is_reputable")


def clean_email(email):
    email = email.strip()
    email = "".join(ch for ch in email if unicodedata.category(ch)[0] != "C")
    return email


def is_reputable(sender_info):
    # This function uses SPAMHAUS API and HIBP API.
    # It returns a tuple: (result, breachInfo, breachList)
    #   result: 0 if safe, 1 if suspicious/breached
    #   breachInfo: string with breach details (or None)
    #   breachList: list of individual breach entries (or empty list)
    test_results = 0
    breachInfo = None
    breachList = []

    SPAMHAUS_CODES = {
        "127.0.1.2": "Spam domain",
        "127.0.1.4": "Phishing domain",
        "127.0.1.5": "Malware domain",
        "127.0.1.6": "Botnet C&C domain",
        "127.0.1.102": "Abused legit domain (compromised)",
        "127.0.1.103": "Abused legit domain (malware)",
        "127.0.1.104": "Abused legit domain (phishing)"
    }
    domain = sender_info.strip().split('@')[-1] if '@' in sender_info else None
    print("extracted domain: ", domain)
    try:
        lookup = f"{domain}.dbl.spamhaus.org"
        result_ip = socket.gethostbyname(lookup)
        if result_ip in SPAMHAUS_CODES:
            print(
                f"Domain {domain} is blacklisted: {SPAMHAUS_CODES[result_ip]}")
            test_results += 0.5
        else:
            print(
                f"Domain {domain} is blacklisted but unknown category ({result_ip})")
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
        breachInfo = f"WARNING: {cleaned_email} has been found in {len(breaches)} breaches."
        print(breachInfo)
        for breach in breaches:
            breachString = f"- {breach.get('Name', 'Unknown')} ({breach.get('BreachDate', 'No Date')}) - {breach.get('Description', 'No Description')}"
            breachList.append(breachString)
            print(breachString)
            test_results += 0.5
    elif response.status_code == 404:
        breachInfo = f"{cleaned_email} is safe (no known breaches)."
        print(breachInfo)
    else:
        breachInfo = f"Error: {response.status_code}, {response.text}"
        print(breachInfo)

    if test_results >= 0.5:
        return (1, breachInfo, breachList)
    else:
        return (0, breachInfo, breachList)


def is_attachment_unsafe(attachments):
    virus_total = VIRUS_TOTAL_KEY
    if not virus_total:
        print("VIRUS_TOTAL_API not found in environment.")
        return 0

    headers = {"x-apikey": virus_total}
    upload_url = "https://www.virustotal.com/api/v3/files"
    analysis_url_base = "https://www.virustotal.com/api/v3/analyses/"

    for file_path in attachments:
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                print(f"Uploading file: {file_path}")
                upload_response = requests.post(
                    upload_url, headers=headers, files=files)
            if upload_response.status_code != 200:
                print(
                    f"Error uploading file {file_path}: {upload_response.text}")
                continue

            analysis_id = upload_response.json().get("data", {}).get("id")
            if not analysis_id:
                print(f"No analysis id returned for file {file_path}")
                continue

            # Poll for analysis completion (up to 10 attempts)
            analysis_url = analysis_url_base + analysis_id
            for attempt in range(10):
                analysis_response = requests.get(analysis_url, headers=headers)
                if analysis_response.status_code != 200:
                    print(
                        f"Error retrieving analysis for {file_path}: {analysis_response.text}")
                    break

                analysis_data = analysis_response.json()
                status = analysis_data.get("data", {}).get(
                    "attributes", {}).get("status")
                if status == "completed":
                    stats = analysis_data.get("data", {}).get(
                        "attributes", {}).get("stats", {})
                    malicious = stats.get("malicious", 0)
                    if malicious > 0:
                        print(
                            f"File {file_path} is unsafe: {malicious} malicious detections.")
                        return 1
                    else:
                        print(f"File {file_path} appears safe.")
                    break
                time.sleep(2)  # wait before polling again
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    return 0


def is_url_unsafe(links):
    virus_total = VIRUS_TOTAL_KEY
    if not virus_total:
        print("VIRUS_TOTAL_API not found in environment.")
        return 0

    headers = {"x-apikey": virus_total}
    url_api_base = "https://www.virustotal.com/api/v3/urls/"

    for link in links:
        try:
            # Encode the URL in base64 (urlsafe) and remove any trailing '='
            encoded_url = base64.urlsafe_b64encode(
                link.encode()).decode().strip("=")
            lookup_url = url_api_base + encoded_url
            print(f"Checking URL: {link} (encoded: {encoded_url})")

            response = requests.get(lookup_url, headers=headers)
            if response.status_code != 200:
                print(
                    f"Error retrieving analysis for URL {link}: {response.text}")
                continue

            analysis_data = response.json()
            # The URL analysis data is under 'last_analysis_stats'
            stats = analysis_data.get("data", {}).get(
                "attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            if malicious > 0:
                print(
                    f"URL {link} is marked unsafe with {malicious} malicious detections.")
                return 1
            else:
                print(f"URL {link} appears safe.")
        except Exception as e:
            print(f"Error processing URL {link}: {e}")
            continue

    return 0


def is_grammar_bad(subject, body, footer):
    return 1


def is_urgent(subject, body, footer):
    return 1


# test_dict_email = {'subject': None, 'preheader_text': None, 'sender_info': 'hunterleaguecanal@gmail.com',
#                   'recipient_info': None, 'date_time': None, 'body': None, 'footer': None}
# test_dict_tests = {'sender_info': 1}

# print(is_phishing(test_dict_email, test_dict_tests))
