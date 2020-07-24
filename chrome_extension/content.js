// Listen for messages
chrome.runtime.onMessage.addListener(
    function (msg, sender, sendResponse) {
    // Raise an alert to notify the user of an incorrect page
    if (msg.instruction === 'alertWrongPage') {
        alert("Invalid webpage! Your open webpage must be a LinkedIn job posting.\n" +
              "Hint: URL should begin with 'https://www.linkedin.com/jobs/view'");
    }
    if (msg.instruction === 'startPostRequest') {
        // Send a message containing the webpage's HTML to the background script for POST to server
        // Has a callback - user alert message
        var webpageDOM = document.all[0].outerHTML
        chrome.runtime.sendMessage({instruction: 'POST', id: msg.job_id, HTML: webpageDOM}, alertComplete);
    }
    if (msg.instruction === 'startGetRequest') {
        // Send a message containing the user-entered job id to the background script for GET from server
        // Has a callback - user alert message
        chrome.runtime.sendMessage({instruction: 'GET', id: msg.job_id}, alertComplete);
    }
});


// Display alert message to user on successful/failed request to server
function alertComplete(status) {
    let alertText = ''

    if (status.status === 'SUCCESS'){
        switch(status.instruction){
            case 'POST':
                alertText += " extracted to server.";
                break;
            case 'GET':
                alertText += " retrieved from server.";
                break;
        }
        alert("Success! Job posting " + status.id + alertText);
    }

    if (status.status === 'FAILURE'){
        switch(status.instruction){
            case 'POST':
                alertText += " could not be sent to server.";
                break;
            case 'GET':
                alertText += " could not be retrieved from server.";
                break;
        }
        alert("Error! Job posting " + status.id + alertText + " Details below:\n" + status.error_msg);
    }

}