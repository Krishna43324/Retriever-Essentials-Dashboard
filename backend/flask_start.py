from flask import Flask, redirect, render_template, request, url_for, jsonify
from pathlib import Path
import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from CSV_uploader import CSVUploader
from CSV_validator import CSV_validator
import mysql.connector
from mysql.connector import Error
import os
from database import check_database_connection, wait_for_database


curr_file = Path(__file__).resolve()
project_root = curr_file.parent.parent
frontend_dir = project_root / 'frontend'

# Load local development settings when a .env file exists. Docker Compose can
# provide the same variables directly through the container environment.
load_dotenv(project_root / ".env")


app = Flask(
    __name__,
    template_folder=str(frontend_dir),
    static_folder=str(frontend_dir)
    )

@app.route('/')
def pushToLoginPage():
    return render_template('LoginPage.html')

#connect to the DB
@app.route("/health/db", methods=["GET"])
def database_health():
    """Small endpoint for checking that Flask can reach MySQL."""
    try:
        if check_database_connection():
            return jsonify({"status": "ok", "database": "connected"}), 200
        return jsonify({"status": "error", "database": "unavailable"}), 503
    except Error:
        app.logger.exception("Database health check failed")
        return jsonify({"status": "error", "database": "unavailable"}), 503

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    hashed_password = "$2b$12$j2LlR1m1JSyLQhdvekmM3u7dsulyQHC3zpPTXDUWY.wtrybv8AuE6"

    valid_password = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode("utf-8"))

    if username == 'admin' and valid_password:
        return redirect(url_for('dashboard'))
    
    return render_template(
        'LoginPage.html',
        error='Invalid username or password.',
    ), 401

@app.route('/dashboard')
def dashboard():
    return render_template('Student Data Dashboard.html')

@app.route('/upload-route', methods=['POST'])
def upload_file():
    dataset_name = request.form.get('datasetName')
    fields_to_omit = request.form.get('fieldsToOmit')
    omission_type = request.form.get('columnOrRow')
    uploaded_file = request.files.get('dataUpload')

    validator = CSV_validator()
    uploadObject = CSVUploader(validator)
    result = uploadObject.upload_file(uploaded_file, user_id=1)

    if result["success"]:
        print("Upload successful:", result["message"])
    else:
        print("Upload failed:", result["message"])

    return jsonify(result)

@app.route('/create-account', methods=['POST'])
def createAccount():
    username = request.get_json().get('username')
    password = request.get_json().get('password')

@app.route('/delete-data', methods=['POST'])
def deleteData():
    datasetName = request.get_json().get('datasetName')

@app.route('/create-chart', methods=['POST'])
def retrieveDataSet():
    data = request.get_json()
    action = data.get('action')

    

    if action == 'get_columns':
        print(5)

if __name__ == '__main__':
    app.run(debug=True)
