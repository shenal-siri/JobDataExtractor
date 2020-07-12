// Listen for messages
chrome.runtime.onMessage.addListener(
    function (msg, sender, sendResponse) {
    // If the received message has the expected format...
    if (msg.instruction === 'alertWrongPage') {
        // Raise an alert to notify the user of an incorrect page
        alert("Invalid webpage! Your open webpage must be a LinkedIn job posting.\n" +
              "Hint: URL should begin with 'https://www.linkedin.com/jobs/view'");
    }
    if (msg.instruction === 'sendMeTheDOM') {
        // Send response to the popup.js callback, passing the web-page's DOM content as argument
        sendResponse({ HTML: document.all[0].outerHTML, job_id: msg.job_id });
        alert("Job posting data successfully extracted!");
    }
});