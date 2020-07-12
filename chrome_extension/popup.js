// Wire up the button in popup.html to the appropriate function
document.addEventListener("DOMContentLoaded", function(event) {
    var getDOMButton = document.getElementById("getDOM");
    getDOMButton.onclick = function() { getDOM(); }
});

// Regex-pattern to check URLs against. 
// It matches URLs like: http[s]://[...]linkedin.com/jobs/view/[...]
var urlRegex = /^https?:\/\/(?:[^.\/?#]+\.)?linkedin\.com\/jobs\/view\//;


// Send a message (intended for the content script)
function getDOM(){
    // Need to send message with the id of the currently active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tab) {

        // Request content script to get DOM if correct webpage, else raise an alert
        if (urlRegex.test(tab[0].url)){

            // Extract the job_id from the url
            var split_url = tab[0].url.split("/", 6);
            var current_id = split_url[split_url.length - 1]

            chrome.tabs.sendMessage(tab[0].id, {instruction: 'sendMeTheDOM', job_id: current_id}, processDOM);
        
        } else {
            chrome.tabs.sendMessage(tab[0].id, {instruction: 'alertWrongPage'} ); 
        }     
    });
}

// The callback function (runs using the message received from the content script)
function processDOM(DOM) {
    console.log('I received the following:\nJob ID: ' + DOM.job_id + '\nDOM Content:\n'+  DOM.HTML);
}

