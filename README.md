# Retriever-Essentials-Dashboard
Retriever Essentials is UMBC's basic needs hub. This project will help Retriever Essentials build a centralized dashboard to understand the impact of their collective work by replacing manual spreadsheet collection with a database and a dashboard.
This github page can be used as a central page to view frontend and backend code. We can also write notes here. 


## Docker Instructions

Retriever Essentials is UMBC's basic needs hub. This project provides a centralized dashboard for understanding the impact of its work by replacing manual spreadsheet collection with a database-backed dashboard.

Current stack

- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: Python, Flask
- Database: MySQL 8.x
- Database driver: `mysql-connector-python`

1. Set up MySQL

Install and start MySQL 8.x, or use the MySQL service from the Docker Compose setup when that is added. The application expects a database named `retriever_dashboard`.

The corrected schema is in `storage.sql`. Run it in MySQL Workbench (or the MySQL command-line client) to create the five tables and seed the Retriever Essentials department. The schema is also kept in `database/init.sql` for automated initialization in a future Docker Compose build.

2. Configure the Flask backend

From the project root, create a virtual environment and activate it in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the credentials for your local MySQL server:

```powershell
Copy-Item .env.example .env
```

At minimum, update `DB_USER` and `DB_PASSWORD`. For local development, `DB_HOST=127.0.0.1` is typical. When running inside Docker Compose, `DB_HOST` should be the database service name (for example, `db`). Do not commit `.env` to Git.

3. Start Flask

From the project root:

```powershell
python backend/flask_start.py
```

Flask waits for MySQL to become available before starting. By default, it listens on `0.0.0.0:5000` so it can be reached from outside its container later.

Open `http://localhost:5000` in a browser. To check the Flask-to-MySQL connection, visit:

```text
http://localhost:5000/health/db
```

A successful response looks like:

```json
{"status": "ok", "database": "connected"}
```

4. Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DB_HOST` | MySQL hostname or Docker service name | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | empty |
| `DB_NAME` | Database name | `retriever_dashboard` |
| `DB_CONNECTION_TIMEOUT` | Connection timeout in seconds | `10` |
| `DB_STARTUP_ATTEMPTS` | Number of MySQL startup retries | `20` |
| `DB_STARTUP_DELAY` | Seconds between retries | `2` |
| `FLASK_HOST` | Flask bind address | `0.0.0.0` |
| `PORT` | Flask port | `5000` |
| `FLASK_DEBUG` | Enable Flask debug mode | `false` |
| `MAX_UPLOAD_BYTES` | Maximum request size | `10485760` |

Current implementation notes

- `backend/database.py` centralizes MySQL connection configuration and provides connection checks/startup retries.
- `GET /health/db` verifies that Flask can connect to MySQL.
- The login route is still temporary demo authentication; database-backed user authentication and role enforcement are subsequent integration work.
- CSV validation and file storage exist, but writing upload metadata to `csv_files` is a subsequent integration step.
- Account creation, dataset deletion, and chart persistence are not implemented yet.


Setting up the Database:

1. Download the MySQL version that works with your OS
2. Follow the setup instructions from the MySQL configurator and name your MySQL server 'retriever_dashboard'. Write down your username and password for the server, we'll need that to access it using MySQL workbench.
3. Download the MySQL Workbench version that works with your OS
4. Open the Workbench. Using your username and password from the server steup, enter the correct details/credentials to register/save the server in Workbench. 
5. Make sure your MySQL server is running. If the workbench shows it is inactive, start it using the following method according to your OS. 

    a. For Windows: use "windows_key + r" and type "services.msc". In this window, navigate to the section with a service named MySQL with some numbers following it, such as "MySQL2610". Right click it and and select "start" to run the server. You can also set the server to startup automatically when you start the computer.

    b. For Linux: use the command "sudo systemctl start mysql", or "mysqld" to start it directly.

    c. For MacOS: use the command "mysql.server start" or "brew services start mysql" if you installed it via Homebrew.
6. Now that your server is running in Workbench, double click on your server and you should see a "connected" status at the top of your screen. If you do NOT see that, double check that your server is running by going through step 5 again, followed by troubleshooting if that fails as well.
7. You should now see an empty SQL file. To check your connection, write the following statements in the file: "CREATE DATABASE retriever_dashboard;", "USE retriever_dashboard;", go to the next line and write "SHOW TABLES;". If this displays 5 tables, you have setup the database!
8. Follow the Flask instructions to setup your Python environment to connect the program with the database.


To execute Flask, you need to go into backend/ folder. 

Create a venv: python3 -m venv venv
Turn on the venv: .\venv\Scripts\Activate.ps1  (on Windows)
Install pip if you haven't using online instructions (py -m ensurepip --upgrade or python -m ensurepip --upgrade on Windows) and do 'pip install Flask', 'pip install bcrypt;, and 'pip install mysql-connector-python'. Then run ./flask_start. It should be capable of bringing up the login page and allowing authentication for administrators and a lot of other functionalities. Flask will enable us to communicate between frontend and backend. Right now, the setup steps seem complex, so maybe we should also use Docker for all of this so that we can just run 'docker run build' or something like that and it'll create the venv and everything we want. We'll see.


