from flask import Flask, render_template, request, jsonify
from pathlib import Path

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

    if username == 'admin' and password == 'AdminRetriever21256#':
        return render_template('Student Data Dashboard.html')
    
    return render_template(
        'LoginPage.html',
        error='Invalid username or password.',
    ), 401

if __name__ == '__main__':
    app.run(debug=True)

