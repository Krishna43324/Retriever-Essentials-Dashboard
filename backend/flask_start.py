from flask import Flask, redirect, render_template, request, url_for, jsonify
from pathlib import Path
import bcrypt
from CSV_uploader import CSVUploader
from CSV_validator import CSV_validator

curr_file = Path(__file__).resolve()
project_root = curr_file.parent.parent
frontend_dir = project_root / 'frontend'


app = Flask(
    __name__,
    template_folder=str(frontend_dir),
    static_folder=str(frontend_dir)
    )

@app.route('/')
def pushToLoginPage():
    return render_template('LoginPage.html')

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

    # validator = CSV_validator()
    # uploadObject = CSVUploader(validator)
    # uploadObject.upload_file(uploadObject, fileIO, 1)

@app.route('/create-account', methods=['POST'])
def createAccount():
    username = request.get_json().get('username')
    password = request.get_json().get('password')

@app.route('/delete-data', methods=['POST'])
def deleteData():
    datasetName = request.get_json().get('datasetName')


if __name__ == '__main__':
    app.run(debug=True)
