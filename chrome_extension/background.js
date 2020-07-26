// Server name (minus endpoints)
hostUrl = "http://localhost:5000/jobdataextractor/api/v1.0/"

// Listen for messages
chrome.runtime.onMessage.addListener(
    function (msg, sender, sendResponse) {
        // Compile data and request for fetch, based on request type
        if (msg.instruction === 'POST') {

            // Compile data and endpoint for POST request
            let data = JSON.stringify({id: msg.id, HTML: msg.HTML})
            let endpoint = hostUrl + "/jobs"

            // Create our request constructor with all the parameters we need
            var request = new Request(endpoint, {
                method: 'POST', 
                body: data, 
                headers: {'Content-Type': 'application/json'}
            });

            // Initiate POST request through fetch function
            fetchFromServer(request, msg, sendResponse);
        }

        if (msg.instruction === 'GET') {

            // Compile endpoint for GET request
            let endpoint = hostUrl + "/jobs/" + msg.id.toString()

            // Create our request constructor with all the parameters we need
            var request = new Request(endpoint, {
                method: 'GET'
            });

            // Initiate GET request through fetch function
            fetchFromServer(request, msg, sendResponse);
        }

        if (msg.instruction === 'GETALL') {

            // Compile endpoint for GET (all jobs) request
            let endpoint = hostUrl + "/jobs/"

            // Create our request constructor with all the parameters we need
            var request = new Request(endpoint, {
                method: 'GET'
            });

            // Initiate GET request through fetch function
            fetchFromServer(request, msg, sendResponse);
        }

        return true; // Needed to ensure message is async
    }
)


// Wrapper function for fetch from server
function fetchFromServer(request, message, sendResponse) {
    fetch(request)

        // CHECK - Throw error if fetch fails or error code is not in 200 range
        .then(function(response) {
        if (!response.ok) {
            let errorString = response.status + " - " + response.statusText;
            throw Error(errorString);
        }
        // Read in the response as JSON
        return response.json();
        })
        // OK - Output response and trigger callback to content.js
        .then(function(responseAsJson) {
        console.log(responseAsJson);
        // Format response and actions based on expected response type
        if (message.instruction == 'POST' || message.instruction == 'GET'){
            sendResponse({ 
                instruction: message.instruction, 
                status: 'SUCCESS', 
                id: responseAsJson.job.id 
            });
        }
        if (message.instruction == 'GETALL'){
            sendResponse({ 
                instruction: message.instruction, 
                status: 'SUCCESS'
            })
            downloadJobList(responseAsJson);
        }
        })
        // BAD - Output error and trigger callback to content.js
        .catch(function(error) {
        console.log('Looks like there was a problem: \n', error);
        sendResponse({
            instruction: message.instruction, 
            status: 'FAILURE', 
            id: message.id, 
            error_msg: error.toString() 
        });
        });
}


// Function to download list of jobs from database as JSON. Implemented from this SO post: 
// https://stackoverflow.com/questions/38833178/using-google-chrome-extensions-to-import-export-json-files
function downloadJobList(jobArray){
    var _jobArray = JSON.stringify(jobArray, null, 4); //indentation in json format, human readable
    var vLink = document.createElement('a'),
    vBlob = new Blob([_jobArray], {type: "octet/stream"}),
    vName = 'JobDataExtractor_AllPostings.json',
    vUrl = window.URL.createObjectURL(vBlob);
    vLink.setAttribute('href', vUrl);
    vLink.setAttribute('download', vName);
    vLink.click();
}