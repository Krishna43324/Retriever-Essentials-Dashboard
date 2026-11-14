function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function deleteData() {
    // Read the VALUE of the input (not the element itself)
    const datasetName = document.getElementById('datasetName').value.trim();

    // This previously checked an undefined variable (`username`), which threw an error
    if (!datasetName) {
        alert("Enter the dataset name that you want to delete.");
        return;
    }

    fetch('/delete-data', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ datasetName })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Could not delete the dataset. Please try again.");
    });
}
