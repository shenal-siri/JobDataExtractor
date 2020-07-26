// Wire up the buttons in popup.html to the appropriate functions
// "Extract Job Posting"
document.addEventListener("DOMContentLoaded", function(event) {
    var extractPageButton = document.getElementById("extractWebpage");
    extractPageButton.onclick = function() { startExtract(); }
});

// "Retrieve Job Posting"
document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById('ok_btn').addEventListener('click', function() { 
        var inputJobID = document.getElementById('job_id_input')
        startGET(inputJobID.value);
        // console.log("input value is : " + inputJobID.value);
        // alert("The entered data is : " + inputJobID.value);
    });
});

// "Download ALL Job Postings"
document.addEventListener("DOMContentLoaded", function(event) {
    var getAllButton = document.getElementById("downloadAllJobs");
    getAllButton.onclick = function() { startGETAll(); }
});


// Regex pattern to check URLs against
// Matches URLs like: http[s]://[...]linkedin.com/jobs/view/[...]
var urlRegex = /^https?:\/\/(?:[^.\/?#]+\.)?linkedin\.com\/jobs\/view\//;


// Send a message containing the current tab's job id to the content script
// No callback - this message kickstarts the eventual POST request to the server
function startExtract(){
    // Need to send message with the id of the currently active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tab) {

        // Request content script to get DOM if correct webpage, else raise an alert
        if (urlRegex.test(tab[0].url)){

            // Extract the job_id from the url
            var split_url = tab[0].url.split("/", 6);
            var current_id = split_url[split_url.length - 1]

            chrome.tabs.sendMessage(tab[0].id, {instruction: 'startPostRequest', job_id: current_id} );
        
        } else {
            chrome.tabs.sendMessage(tab[0].id, {instruction: 'alertWrongPage'} ); 
        }     
    });
}

// Send a message containing the entered job id for retrieval by the server
// No callback - this message kickstarts the eventual GET request to the server
function startGET(current_id) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, {instruction: 'startGetRequest', job_id: current_id} );
    });
}

// Send a message containing only the instruction to extract all jobs
// No callback - this message kickstarts the eventual GET request to the server
function startGETAll() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, {instruction: 'startGetAllRequest'} );
    });
}


/*
Current implementation:

popup.html:     "extractWebpage" click  ->
popup.js:       startExtract()          ->
popup.js:       'startPOSTRequest'      -> 
content.js:     'POST'                  -> 
background.js:  fetchFromServer()       -> 
background.js:  'SUCCESS'/'FAILURE'     ->
content.js:     alertComplete()      
*/
