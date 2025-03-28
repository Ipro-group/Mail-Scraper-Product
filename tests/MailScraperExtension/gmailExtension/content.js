//*****************************************#
//Author: Kaleb Austgen
//Last Edited: 3/26/25
//Purpose: Reads clicked on email and sends information to background.js
//*****************************************#

console.log('Content script loaded');

// Listen for clicks on emails
document.addEventListener('click', (event) => {
    const emailElement = event.target.closest('tr.zA, .adn'); // Email list item or conversation view

    if (emailElement) {
        console.log('Email clicked:', emailElement);

        setTimeout(() => {
            const emailView = document.querySelector('div[role="dialog"], .nH.bkK'); // Opened email view

            if (emailView) {
                console.log('Email view detected:', emailView);

                const linkElements = emailView.querySelector('a'); //Link Selector
                const subjectElement = emailView.querySelector('.hP'); // Subject selector
                const bodyElement = emailView.querySelector('.ii.gt'); // Body selector
                const senderNameElement = emailView.querySelector('.gD'); // Sender name
                const senderEmailElement = senderNameElement ? senderNameElement.getAttribute('email') : null; // Sender email
                
                const links = linkElements ? linkElements.getAttribute("href") : "No links found";
                //const links = Array.from(linkElements).map(link => link.getAttribute("href"));
                const subject = subjectElement ? subjectElement.innerText : "No subject found";
                const body = bodyElement ? bodyElement.innerText : "No body found";
                const senderName = senderNameElement ? senderNameElement.innerText : "No sender name found";
                const senderEmail = senderEmailElement ? senderEmailElement : "No sender email found";

                console.log('Sending email to server:', subject);

                // Extract attachment data
                const attachments = [];

                // Handle attachments from anchor tags <a> with the classes `aQy aZr e`
                const attachmentElements = emailView.querySelectorAll('a.aQy.aZr.e');
                attachmentElements.forEach((attachment) => {
                    const attachmentUrl = attachment.getAttribute('href'); // Get URL of attachment
                    let attachmentName = attachment.getAttribute('download'); // Get name of attachment
                
                    // If download name is not available, fall back to URL or generate a unique name
                    if (!attachmentName) {
                        attachmentName = 'attachment_' + new Date().getTime(); // Default name
                    }

                    // Try to extract file extension based on URL or content type
                    const fileExtension = getFileExtensionFromUrl(attachmentUrl);
                    if (fileExtension) {
                        attachmentName += '.' + fileExtension; // Add the file extension to the name
                    }

                    attachments.push({
                        url: attachmentUrl,
                        name: attachmentName
                    });
                });


                // Handle attachments from span tags with `download_url` attribute
                const spanElements = emailView.querySelectorAll('span[download_url]');
                spanElements.forEach((span) => {
                    const attachmentUrl = span.getAttribute('download_url'); // Get URL of attachment from the download_url attribute
                    let attachmentName = span.innerText; // You could extract the filename from innerText or other methods

                    // If the name from innerText is not good, fall back to generating one
                    if (!attachmentName) {
                        attachmentName = 'attachment_' + new Date().getTime(); // Default name or based on URL
                    }

                    // Try to extract file extension based on URL or content type
                    const fileExtension = getFileExtensionFromUrl(attachmentUrl);
                    if (fileExtension) {
                        attachmentName += '.' + fileExtension; // Add the file extension to the name
                    }

                    attachments.push({
                        url: attachmentUrl,
                        name: attachmentName
                    });
                });


                // Send email data to the background script (stateless approach)
                chrome.runtime.sendMessage({
                    type: 'emailContent',
                    subject: subject,
                    body: body,
                    senderName: senderName,
                    senderEmail: senderEmail,
                    links: links,
                    attachments: attachments // Send attachments data to server
                });
            
                // Send attachments to the server
                attachments.forEach((attachment) => {
                    console.log('Downloading attachment:', attachment.name, 'from', attachment.url);

                    // Fetch the attachment from the URL
                    fetch(attachment.url)
                        .then(response => {
                            if (response.ok) {
                                return response.blob(); // Get blob data of the attachment
                            } else {
                                throw new Error('Failed to download attachment');
                            }
                    })
                    .then(blob => {
                        // Create FormData to send the attachment to your Python server
                        const formData = new FormData();
                        formData.append('file', blob, attachment.name); // Append the file with its name

                        // Send the attachment to the server
                        fetch('http://localhost:5000/attachments', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Attachment sent successfully:', data);
                        })
                        .catch(error => {
                            console.error('Error sending attachment:', error);
                        });
                    })
                    .catch(error => {
                        console.error('Error downloading attachment:', error);
                    });
            });


            }
        }, 500); // Delay ensures content is fully loaded
    }
});

// Function to get file extension from URL (based on the URL or content type)
function getFileExtensionFromUrl(url) {
    const urlParts = url.split('/');
    const fileName = urlParts[urlParts.length - 1];
    const fileExtension = fileName.split('.').pop();
    
    // Check if it's a valid file extension (this is basic, you can improve based on your needs)
    if (fileExtension && fileExtension.length > 1) {
        return fileExtension;
    }
    return ''; // Return empty if no valid extension
}