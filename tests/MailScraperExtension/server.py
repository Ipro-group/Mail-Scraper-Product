from flask import Flask, request, jsonify
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

    # Print first 500 characters
    print(f"\nEmail Received:\nSender: {senderName} <{senderEmail}>\nSubject: {subject}\nBody: {body[:500]}...")

    # Dict in format for is_phishing
    dict_email = {'subject':subject, 
                  'preheader_text':None, 
                  'sender_info':None, 
                  'recipient_info':None, 
                  'date_time':None,
                  'body':body, 
                  'footer':None}
    
    dict_tests = {'url_test':0, 
                  'sender_reputation_test':0, 
                  'attachment_test':0, 
                  'grammar_test':0, 
                  'tone_test':0}

    processEmail = core.is_phishing(dict_email=dict_email, dict_tests=dict_tests, attachments=None)

    print(processEmail)

    # Add your processing logic here
    # Example: Save to file or database

    return jsonify({"status": "success", "message": "Email processed successfully!"})


if __name__ == '__main__':
    app.run(port=5000)
