# Retriever-Essentials-Dashboard
Retriever Essentials is UMBC's basic needs hub. This project will help Retriever Essentials build a centralized dashboard to understand the impact of their collective work by replacing manual spreadsheet collection with a database and a dashboard.
This github page can be used as a central page to view frontend and backend code. We can also write notes here. 

To execute Flask, you need to go into backend/ folder. 

Create a venv: python3 -m venv venv
Turn on the venv: .\venv\Scripts\Activate.ps1  (on Windows)
Install pip if you haven't using online instructions and do 'pip install Flask'. Then run ./flask_start. It should be capable of bringing up the login page so far. Flask will enable us to communicate between frontend and backend. Right now, the setup steps seem complex, so maybe we should also use Docker for all of this so that we can just run 'docker run build' or something like that and it'll create the venv and everything we want. We'll see.
