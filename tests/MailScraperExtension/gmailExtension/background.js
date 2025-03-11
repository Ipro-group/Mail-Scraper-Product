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
                senderEmail: request.senderEmail
            })
        }).then(response => response.json())
          .then(data => {
              console.log('Python server response:', data);
          }).catch(err => {
              console.error('Error:', err);
          });
    }
});