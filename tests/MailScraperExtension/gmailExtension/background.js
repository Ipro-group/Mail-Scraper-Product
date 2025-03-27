//*****************************************#
//Author: Kaleb Austgen
//Last Edited: 3/26/25
//Purpose: Recieves email info from content.js, prepares it and then sends to server.py
//*****************************************#

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'emailContent') {
        //Debug
        console.log('Recieved email content in background.js');
        console.log('Email clicked:', request.subject);
        console.log('Sender Name:', request.senderName);
        console.log('Sender Email:', request.senderEmail);

        // Send email content to Python server
        fetch('http://localhost:5000/email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: request.subject,
                body: request.body,
                senderName: request.senderName,
                senderEmail: request.senderEmail,
                links: request.links
            })
        }).then(response => response.text())
          .then(html => {
              console.log('Python server response:', html);

              // Create popup
              chrome.windows.create({
                url: 'data:text/html;charset=utf-8,' + encodeURIComponent(html),
                type: 'popup',
                width: 1000,
                height: 600
              })
          }).catch(err => {
              console.error('Error:', err);
          });
    }
});

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "showOverlay",
        title: "Show Overlay",
        contexts: ["all"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "showOverlay") {
        // Getting current window's dimensions
        chrome.windows.getCurrent((currentWindow) => {
            const width = 1000;
            const height = 260;
            const top = Math.round((currentWindow.height - height) / 2);
            const left = Math.round((currentWindow.width - width) / 2);

            // Open the custom popup window
            chrome.windows.create({
                url: chrome.runtime.getURL("detection.html"),
                type: "popup",
                width: width,
                height: height,
                top: top,
                left: left
            });
        });
    }
});
