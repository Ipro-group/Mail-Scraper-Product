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

                // Send email data to the background script (stateless approach)
                chrome.runtime.sendMessage({
                    type: 'emailContent',
                    subject: subject,
                    body: body,
                    senderName: senderName,
                    senderEmail: senderEmail,
                    links: links
                });
            }
        }, 500); // Delay ensures content is fully loaded
    }
});