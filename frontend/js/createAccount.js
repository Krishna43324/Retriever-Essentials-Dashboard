function returnToDashboard() {
    window.location.href = 'Student Data Dashboard.html';
}

function createAccount(){
    username = document.getElementById("username")
    password = document.getElementById("password")

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

}