//functions for CreateChart html: return to the main dashboard page, read input

function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

document.addEventListener("DOMContentLoaded", loadDatasets);

function loadDatasets() {
    const dropdown = document.getElementById("datasetName");
    const status = document.getElementById("datasetStatus");

    fetch("/datasets")
        .then(async response => {
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Could not load datasets.");
            }

            return data;
        })
        .then(data => {
            dropdown.replaceChildren(new Option("Choose a dataset", ""));

            data.datasets.forEach(dataset => {
                dropdown.add(
                    new Option(dataset.dataset_name, dataset.dataset_name)
                );
            });

            status.textContent = data.datasets.length
                ? ""
                : "No datasets have been uploaded yet.";
        })
        .catch(error => {
            dropdown.replaceChildren(new Option("Datasets unavailable", ""));
            status.textContent = error.message;
        });
}

function retrieveData() {
    // Read the VALUE of the input (not the element itself)
    const datasetName = document.getElementById('datasetName').value.trim();
    const columnDropdown = document.getElementById("columnDropdown");
    
    if (!datasetName) {
        alert("Enter the dataset name first.");
        return;
    }

    columnDropdown.disabled = true;
    columnDropdown.replaceChildren(new Option("Loading columns...", ""));


    fetch('/create-chart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        // The Flask route reads `action` from the JSON body, so it goes here
        // (it was previously placed outside the body as an undefined variable).
        body: JSON.stringify({ datasetName, action: 'get_columns' })
    })
        .then(async response => {
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Could not load columns.");
            }

            return data;
        })
        .then(data => {
            columnDropdown.replaceChildren(new Option("Choose a column", ""));

            data.columns.forEach(column => {
                columnDropdown.add(new Option(column, column));
            });

            columnDropdown.disabled = false;
        })
        .catch(error => {
            columnDropdown.replaceChildren(new Option("Columns unavailable", ""));
            alert(error.message);
        });
}
