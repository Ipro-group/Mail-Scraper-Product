import imaplib
import email
from email.header import decode_header

# RETRIEVES LAST 10 EMAIL TITLES


# Gmail IMAP server settings
imap_server = "imap.gmail.com"
email_account = "nice@gmail.com"  # Replace with your Gmail address
# Replace with your app password if 2FA is enabled
password = "apppass"

try:
    # Connect to the Gmail IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_account, password)

    # Select the inbox
    mail.select("inbox")

    # Search for all emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    # Retrieve the last 10 emails (or fewer if inbox has less than 10 emails)
    last_10_ids = email_ids[-10:]  # Get the IDs of the last 10 emails
    print("Getting last 10 email titles from: ", email_account)

    # Reverse to display emails in chronological order
    for email_id in reversed(last_10_ids):
        # Fetch the email
        res, msg = mail.fetch(email_id, "(RFC822)")
        for response_part in msg:
            if isinstance(response_part, tuple):
                # Parse the email content
                message = email.message_from_bytes(response_part[1])

                # Decode the email subject
                subject = decode_header(message["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                # Print the email title
                print(f"- {subject}")
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" not in content_disposition:
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            print("Body:", body)
            else:
                body = msg.get_payload(decode=True).decode()
                print("Body:", body)
    # Close the connection
    mail.logout()

except Exception as e:
    print(f"An error occurred: {e}")
