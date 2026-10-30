function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function deleteData(){
    datasetName = document.getElementById('datasetName')

    if (!username) {
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
}