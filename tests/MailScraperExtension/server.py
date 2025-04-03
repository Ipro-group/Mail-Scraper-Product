# *****************************************#
# Author: Kaleb Austgen
# Last Edited: 4/2/25
# Purpose: Listens for output from background.js for processing and then returns output to user
# *****************************************#

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  # Import CORS
import sys
import os
import magic
from email_analysis import core
from werkzeug.utils import secure_filename
sys.stdout.reconfigure(encoding='utf-8')
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set the folder where you want to save uploaded attachments
UPLOAD_FOLDER = 'attachments'  # You can change this to any valid directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Make sure the folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# email route
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

    dict_tests = {'url_test': 1,
                  'sender_info': 1,
                  'attachment_test': 1,
                  'grammar_test': 0,
                  'tone_test': 0}

    # Check to see if is_phishing is iterable
    try:
        processEmail, breachInfo = core.is_phishing(
            dict_email=dict_email, dict_tests=dict_tests, attachments=None)
    except TypeError:
        processEmail = core.is_phishing(
            dict_email=dict_email, dict_tests=dict_tests, attachments=None)
        breachInfo = "None"
        #breachList = "None"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    attachment_path = os.path.join(
        BASE_DIR, "email_analysis", "attachments")
    attachments = {attachment_path}

    processAttachment = core.is_attachment_unsafe(attachments)

    processed_urls = {"http://119.189.200.56:53768/bin.sh"}
    processURL = core.is_url_unsafe(links)

    print(processEmail)
    print(processAttachment)
    print(processURL)

    # Add your processing logic here
    # Example: Save to file or database

    # If a vulnerability was found render an HTML template to pass on the data for a popup
    if processEmail == 1 or processAttachment[0] == 1 or processURL[0] == 1:
        showWarning = True
        '''return render_template('emailPopup.html', showWarning=showWarning,
                         senderName=senderName,
                         senderEmail=senderEmail,
                         links=links,
                         breachInfo=breachInfo,
                         breachList=breachList,)'''
        message = f'''
            <p><strong>Warning!</strong> The email you clicked on may be malicious</p>
            <p>{breachInfo}</p>
            <p>{processAttachment[1]}</p>
            <p>{processURL[1:]}</p>
        '''
    else:
        showWarning = False
        message = None
    print(showWarning)
    return jsonify({
        "status": "success",
        "showWarning": showWarning,
        "message": message
    })


# Define the allowed MIME types and their corresponding extensions
mime_to_extension = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'application/zip': 'zip',
    'text/plain': 'txt',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'text/html': 'html',
    'text/csv': 'csv'
}

# Function to check MIME type based on file's magic number (signature)


def get_mime_type(file):
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file.read())


@app.route('/attachments', methods=['POST'])
def receive_attachment():
    # Check if the request contains files
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If the user doesn't select a file, the filename will be empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Generate a secure filename for the uploaded file to avoid path traversal issues
        filename = secure_filename(file.filename)

        # Check MIME type
        file.seek(0)  # Rewind the file to start before checking MIME type
        mime_type = get_mime_type(file)

        # Check if the MIME type is allowed
        if mime_type not in mime_to_extension:
            return jsonify({'error': f'File type not allowed. Received: {mime_type}'}), 400

        # Get the appropriate file extension
        file_extension = mime_to_extension[mime_type]

        # If the filename doesn't already have the correct extension, add it
        if not filename.endswith(file_extension):
            filename = f"{os.path.splitext(filename)[0]}.{file_extension}"

        # Rewind the file after MIME type check
        file.seek(0)

        # Create the file path to save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the file to the server
        file.save(file_path)

        # call function in core.py
        processAttachment = core.is_attachment_unsafe([file_path])

        # Return a success response with the file path
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path, 'attachment_unsafe': processAttachment}), 200

    except Exception as e:
        # Return a failure response if something went wrong
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
