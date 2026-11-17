
# Retriever-Essentials-Dashboard
Retriever Essentials is UMBC's basic needs hub. This project will help Retriever Essentials build a centralized dashboard to understand the impact of their collective work by replacing manual spreadsheet collection with a database and a dashboard.
This github page can be used as a central page to view frontend and backend code. We can also write notes here. 
 
 
## Quick start (Docker)
 
Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + the Compose plugin). Nothing else needs to be installed: no Python, venv, or MySQL.
 
**Before running any `docker` command, open Docker Desktop and wait until it says "Engine running"** (green icon, bottom-left). If you see `error during connect ... dockerDesktopLinuxEngine: The system cannot find the file specified`, Docker Desktop is not running yet. On Windows it also needs WSL 2 enabled (Docker Desktop prompts you to install it on first launch; a restart may be required).
 
From the project root, in PowerShell:
 
```powershell
Copy-Item .env.example .env
# edit .env: set DB_PASSWORD, DB_ROOT_PASSWORD, SECRET_KEY, ADMIN_PASSWORD
docker compose up --build
```
 
(macOS/Linux: `cp .env.example .env`.)
 
Then open <http://localhost:5000> and log in with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from your `.env`. Check the Flask-to-MySQL connection at <http://localhost:5000/health/db> (expect `{"database":"connected","status":"ok"}`).
 
With Docker you do **not** install MySQL yourself: Compose starts its own MySQL container, creates the database user from `DB_USER`/`DB_PASSWORD`, and runs `database/init.sql` for you. Compose also overrides `DB_HOST` to `db`, so leave `DB_HOST=127.0.0.1` in `.env`.
 
| Service | What it is | Notes |
|---|---|---|
| `db` | MySQL 8.4 | Data lives in the `mysql_data` volume. `database/init.sql` runs automatically **only the first time** the volume is created. |
| `app` | Flask served by gunicorn | Waits for MySQL to be healthy, creates the admin account on first start. Uploaded CSVs live in the `uploads` volume. |
 
Useful commands:
 
```powershell
docker compose up -d --build     # run in the background
docker compose logs -f app       # follow the Flask logs
docker compose down              # stop (data is kept)
docker compose down -v           # stop AND wipe the database and uploads
```
 
**Changed `database/init.sql`?** It only runs on a fresh database, so run `docker compose down -v` and start again (this deletes data).
 
**Connecting with MySQL Workbench to the Docker database:** host `127.0.0.1`, port `3307` (`DB_HOST_PORT`), user/password from your `.env`.
 
## Running without Docker (local MySQL)
 
Use this if you installed MySQL yourself. Do **not** run it at the same time as the Docker setup on the same ports.
 
**1. Install and start MySQL 8.x** (MySQL Installer on Windows; Homebrew/apt elsewhere). During setup you choose a password for the `root` user; write it down. Make sure the MySQL service is running (Windows: `services.msc` -> MySQL80 -> Start).
 
**2. Create the database and tables.** Easiest on Windows is MySQL Workbench:
1. Open Workbench and connect to your local server (the saved connection uses `root` and your root password).
2. `File > Open SQL Script...` and choose `database/init.sql`.
3. Click the lightning-bolt button (Execute). In the left panel, refresh Schemas: `retriever_dashboard` should show 5 tables (`csv_files`, `departments`, `figure_datasets`, `figures`, `users`).
(PowerShell does not support `mysql -u root -p < database/init.sql`. Use Workbench, or run `mysql -u root -p` and then `source database/init.sql;` from the MySQL prompt.)
 
**3. Choose the account Flask will use.** Pick ONE:
- *Quickest:* use root. Set `DB_USER=root` and `DB_PASSWORD=<your root password>` in `.env`.
- *Recommended:* create a dedicated user. In a Workbench query tab run (change the password):
```sql
CREATE USER IF NOT EXISTS 'retriever'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON retriever_dashboard.* TO 'retriever'@'localhost';
FLUSH PRIVILEGES;
```
*Current Universal Standard Credentials*
username: retriever
password: database4website$
 
then set `DB_USER=retriever` and `DB_PASSWORD=choose-a-password` in `.env`. If the user already exists with a different password, use `ALTER USER 'retriever'@'localhost' IDENTIFIED BY 'new-password';` instead.
 
The error `1045 (28000): Access denied for user '...'@'localhost'` means the user in `.env` does not exist in your MySQL, or the password does not match. It is a credentials problem, not a Flask problem. You can test a login directly in Workbench with the same username/password.
 
**4. Configure `.env`.** `Copy-Item .env.example .env`, then make sure these are set (older `.env` files are missing the last three):
 
```
DB_HOST=127.0.0.1
DB_USER=...
DB_PASSWORD=...
SECRET_KEY=any-long-random-string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=pick-a-password
```
 
`ADMIN_USERNAME`/`ADMIN_PASSWORD` become the first login (created on first start if no admin exists). Skip `DB_ROOT_PASSWORD`, `DB_HOST_PORT`, and `APP_PORT`; they are Docker-only.
 
**5. Run Flask.**
 
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend/flask_start.py
```
 
Open <http://localhost:5000>. You should see `Connected to MySQL database successfully.` in the terminal.
 
## Environment variables
 
| Variable | Purpose | Default |
|---|---|---|
| `DB_HOST` | MySQL hostname (Compose sets this to `db`) | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` / `DB_PASSWORD` | App's MySQL credentials (Compose creates this user) | `root` / empty |
| `DB_NAME` | Database name | `retriever_dashboard` |
| `DB_ROOT_PASSWORD` | MySQL root password (Docker only) | required in Docker |
| `DB_HOST_PORT` | Host port for Workbench access (Docker only) | `3307` |
| `DB_CONNECTION_TIMEOUT` | Connection timeout in seconds | `10` |
| `DB_STARTUP_ATTEMPTS` / `DB_STARTUP_DELAY` | Startup retry count / seconds between retries | `20` / `2` |
| `SECRET_KEY` | Signs login sessions; required in Docker | random per start |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | First admin account, created if no admin exists | none |
| `FLASK_HOST` / `PORT` / `FLASK_DEBUG` | Flask bind address, port, debug (non-Docker) | `0.0.0.0` / `5000` / `false` |
| `MAX_UPLOAD_BYTES` | Maximum upload size | `10485760` |
| `UPLOAD_DIR` | Where CSVs are stored | `<project>/uploads` |
 
## Current implementation notes
 
- `backend/database.py` holds the MySQL connection config, startup retry, and the query helpers (users, csv_files).
- Login checks bcrypt hashes in the `users` table and stores the user in a session. Roles (`admin`/`staff`/`viewer`) are enforced on the API routes via `backend/user.py`.
- Upload validates the CSV, then records it in `csv_files`. Delete removes the row and the file. Create Account (admin only) adds a `staff` user.
- Not implemented yet: chart persistence (`/create-chart`, `figures` tables), `fieldsToOmit` handling on upload, and password change.
 
