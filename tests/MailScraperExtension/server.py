#*****************************************#
#Author: Kaleb Austgen
#Last Edited: 3/26/25
#Purpose: Listens for output from background.js for processing and then returns output to user
#*****************************************#

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  # Import CORS
import sys
import os
from email_analysis import core
sys.stdout.reconfigure(encoding='utf-8')
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Set the folder where you want to save uploaded attachments
UPLOAD_FOLDER = 'attachments'  # You can change this to any valid directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Make sure the folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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

    processEmail = core.is_phishing(
        dict_email=dict_email, dict_tests=dict_tests, attachments=None)
    
    attachments = data.get('attachments', [])
   
    processAttachment = core.is_attachment_unsafe(attachments)

    print(processEmail)
    print(processAttachment)

    # Add your processing logic here
    # Example: Save to file or database

    # If a vulnerability was found render an HTML template to pass on the data for a popup
    if processEmail==1 or processAttachment==1: 
        return render_template('emailPopup.html',
                         subject=subject,
                         body=body,
                         senderName=senderName,
                         senderEmail=senderEmail,
                         links=links)
    
    else:
        return jsonify({"status": "success", "message": "Email processed successfully!"})


# route for handling attachments
@app.route('/attachments', methods=['POST'])
def receive_attachment():
    # Check if the request contains files
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If the user doesn't select a file, the filename will be empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validate file type (optional, you can adjust this based on what you need)
    allowed_extensions = {'pdf', 'docx', 'txt', 'jpg', 'png'}
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Generate a secure filename for the uploaded file
        filename = os.path.basename(file.filename)  # Avoid path traversal issues
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # If needed, you can process the file here (e.g., analyze the contents)

        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)

