function returnToDashboard() {
    window.location.href = '/frontend/Student Data Dashboard.html';
}

function createAccount() {
    // Read the VALUES of the inputs (not the elements themselves)
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Enter both a username and password.");
        return;
    }

    fetch('/create-account', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Could not create the account. Please try again.");
    });
}