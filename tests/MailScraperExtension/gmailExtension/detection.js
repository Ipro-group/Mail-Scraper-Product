document.getElementById('acknowledgeButton').addEventListener('click', function() {
    chrome.tabs.getCurrent(function(tab) {
        chrome.tabs.remove(tab.id);
    });
});