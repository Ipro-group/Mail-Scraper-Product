#*****************************************#
#Author: Kaleb Austgen
#Last Edited: 3/26/25
#Purpose: Listens for output from background.js for processing and then returns output to user
#*****************************************#

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  # Import CORS
import sys
from email_analysis import core
sys.stdout.reconfigure(encoding='utf-8')
app = Flask(__name__)
CORS(app)  # Enable CORS for all routs


@app.route('/email', methods=['POST'])
def receive_email():

    # Log request methods and headers
    print(f"\nRequest Method: {request.method}")
    print(f"Request Headers: {request.headers}")

    data = request.json
    subject = data.get('subject', 'No Subject')
    body = data.get('body', 'No Body')
    senderName = data.get('senderName', 'Unknown Sender')
    senderEmail = data.get('senderEmail', 'Unknown Email')
    links = data.get('links', 'No links')

    # Print first 500 characters
    print(
        f"\nEmail Received:\nSender: {senderName} <{senderEmail}>\nSubject: {subject}\nLinks: {links}\nBody: {body[:500]}...")

    # Dict in format for is_phishing
    dict_email = {'subject': subject,
                  'preheader_text': None,
                  'sender_info': senderEmail,
                  'recipient_info': None,
                  'date_time': None,
                  'body': body,
                  'footer': None}

    dict_tests = {'url_test': 0,
                  'sender_info': 1,
                  'attachment_test': 1,
                  'grammar_test': 0,
                  'tone_test': 0}

    processEmail, breachInfo, breachList = core.is_phishing(
        dict_email=dict_email, dict_tests=dict_tests, attachments=None)
    attachments = {
        "tests\MailScraperExtension\email_analysis\attachments\Relational Algebra Practice Questions.pdf"}
    processAttachment = core.is_attachment_unsafe(attachments)

    print(processEmail)
    print(processAttachment)

    # Add your processing logic here
    # Example: Save to file or database

    # If a vulnerability was found render an HTML template to pass on the data for a popup
    if processEmail==1 or processAttachment==1: 
        return render_template('emailPopup.html',
                         senderName=senderName,
                         senderEmail=senderEmail,
                         links=links,
                         breachInfo=breachInfo,
                         breachList=breachList,)
    
    else:
        return jsonify({"status": "success", "message": "Email processed successfully!"})


if __name__ == '__main__':
    app.run(port=5000)
