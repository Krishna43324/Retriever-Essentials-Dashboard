function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function handleUpload() {
    const formData = new FormData();
    formData.append('datasetName', document.getElementById('datasetName').value);
    formData.append('fieldsToOmit', document.getElementById('fieldsToOmit').value);
    formData.append('columnOrRow', document.getElementById('omissionType').value);
    formData.append('dataUpload', document.getElementById('dataUpload').files[0]); // Grabs the CSV file

    // Send it to your Flask backend route
    fetch('/upload-route', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}