//functions for CreateChart html: return to the main dashboard page, read input

function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function retrieveData() {
    // Read the VALUE of the input (not the element itself)
    const datasetName = document.getElementById('datasetName').value.trim();

    if (!datasetName) {
        alert("Enter the dataset name first.");
        return;
    }

    fetch('/create-chart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        // The Flask route reads `action` from the JSON body, so it goes here
        // (it was previously placed outside the body as an undefined variable).
        body: JSON.stringify({ datasetName, action: 'get_columns' })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Could not load the dataset. Please try again.");
    });
}
