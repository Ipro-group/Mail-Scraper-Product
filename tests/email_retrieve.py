import win32com.client

# CONNECTS TO OUTLOOK DESKTOP APP. OLD LOOK ONLY. DOES NOT WORK WITH THE NEW LOOK/VERSION OF OUTLOOK
try:
    # Connect to Outlook application
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    # Select your email account
    account_name = "noise@hawk.iit.edu"  # Replace with your account name
    account = namespace.Folders[account_name]

    # Access the Inbox folder
    inbox = account.Folders["Inbox"]

    # Get the last email
    messages = inbox.Items
    # Sort by ReceivedTime in descending order
    messages.Sort("[ReceivedTime]", True)
    last_email = messages.GetFirst()  # Get the most recent email

    # Display the email details
    print(f"Subject: {last_email.Subject}")
    print(f"From: {last_email.SenderEmailAddress}")
    print(f"Received: {last_email.ReceivedTime}")
    print(f"Body:\n{last_email.Body}")

except Exception as e:
    print(f"An error occurred: {e}")
