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

        return true; // Needed to ensure message is async
    }
)


// Wrapper function for fetch from server
function fetchFromServer(request, message, sendResponse) {
    fetch(request)

        // CHECK - Throw error if fetch fails or error code is not in 200 range
        .then(function(response) {
        if (!response.ok) {
            throw Error(response.status);
        }
        // Read in the response as JSON
        return response.json();
        })

        // OK - Output response and trigger callback to content.js
        .then(function(responseAsJson) {
        console.log(responseAsJson);
        sendResponse({ 
            instruction: message.instruction, 
            status: 'SUCCESS', 
            id: responseAsJson.job.id 
        });
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