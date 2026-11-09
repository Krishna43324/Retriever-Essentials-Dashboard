function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function retrieveData(){
    datasetName = document.getElementById('datasetName')


    fetch('/create-chart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ datasetName }),
        action: get_columns
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
}