import csv
import os
import secrets
from functools import wraps
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from mysql.connector import Error, IntegrityError

curr_file = Path(__file__).resolve()
project_root = curr_file.parent.parent
frontend_dir = project_root / "frontend"

# Load local development settings when a .env file exists. Docker Compose
# provides the same variables directly through the container environment.
# This must run BEFORE importing modules that read the environment.
load_dotenv(project_root / ".env")

import database  # noqa: E402
from CSV_uploader import CSVUploader  # noqa: E402
from CSV_validator import CSV_validator  # noqa: E402
from user import User  # noqa: E402

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", project_root / "uploads"))

# static_url_path="/frontend" so the "/frontend/style.css", "/frontend/js/..."
# and "/frontend/images/..." URLs used by the HTML pages actually resolve.
app = Flask(
    __name__,
    template_folder=str(frontend_dir),
    static_folder=str(frontend_dir),
    static_url_path="/frontend",
)

app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    # Fine for local dev, but sessions are invalidated on every restart and
    # are not shared between workers. Set SECRET_KEY for anything real.
    app.secret_key = secrets.token_hex(32)
    app.logger.warning("SECRET_KEY is not set; using a temporary random key.")

# A valid bcrypt hash used to keep login timing similar for unknown usernames.
_DUMMY_HASH = bcrypt.hashpw(b"not-a-real-password", bcrypt.gensalt())


def init_database() -> None:
    """Wait for MySQL, then make sure the bootstrap admin account exists."""
    database.wait_for_database()
    try:
        database.ensure_admin_user(
            os.getenv("ADMIN_USERNAME", ""), os.getenv("ADMIN_PASSWORD", "")
        )
    except IntegrityError:
        pass  # another worker created it first


init_database()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def current_user():
    """Return a User for the logged-in session, or None."""
    if "user_id" not in session:
        return None
    return User(session["user_id"], session["username"], session["role"])


def api_login_required(permission=None):
    """Require a logged-in user; optionally require a User.can_*() permission."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return jsonify(success=False, message="Please log in first."), 401
            if permission and not getattr(user, permission)():
                return jsonify(success=False, message="You do not have permission to do that."), 403
            return view(*args, user=user, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def pushToLoginPage():
    return render_template("LoginPage.html")


@app.route("/health/db", methods=["GET"])
def database_health():
    """Small endpoint for checking that Flask can reach MySQL."""
    try:
        if database.check_database_connection():
            return jsonify({"status": "ok", "database": "connected"}), 200
        return jsonify({"status": "error", "database": "unavailable"}), 503
    except Error:
        app.logger.exception("Database health check failed")
        return jsonify({"status": "error", "database": "unavailable"}), 503


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    try:
        row = database.get_user_by_username(username)
    except Error:
        app.logger.exception("Login lookup failed")
        return render_template(
            "LoginPage.html", error="The database is unavailable. Try again shortly."
        ), 503

    stored_hash = row["password_hash"].encode("utf-8") if row else _DUMMY_HASH
    valid = bcrypt.checkpw(password.encode("utf-8"), stored_hash)

    if row and valid:
        session.clear()
        session["user_id"] = row["user_id"]
        session["username"] = row["username"]
        session["role"] = row["role"]
        session["dep_id"] = row["dep_id"]
        return redirect(url_for("dashboard"))

    return render_template("LoginPage.html", error="Invalid username or password."), 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("pushToLoginPage"))


@app.route("/dashboard")
def dashboard():
    if current_user() is None:
        return redirect(url_for("pushToLoginPage"))
    return render_template("Student Data Dashboard.html")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

def _count_csv_rows(path: str) -> int:
    """Number of data rows (header excluded)."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


@app.route("/upload-route", methods=["POST"])
@api_login_required("can_upload")
def upload_file(user):
    uploaded_file = request.files.get("dataUpload")
    original_name = getattr(uploaded_file, "filename", "") or ""
    dataset_name = (request.form.get("datasetName") or "").strip() or Path(original_name).stem
    # fieldsToOmit / columnOrRow are collected by the form but not applied yet.

    if not dataset_name:
        return jsonify(success=False, message="Enter a dataset name."), 400

    try:
        if database.get_csv_by_dataset_name(dataset_name):
            return jsonify(success=False, message=f"A dataset named '{dataset_name}' already exists."), 409

        uploader = CSVUploader(CSV_validator(), UPLOAD_DIR)
        result = uploader.upload_file(uploaded_file, user_id=user.user_id)
        if not result["success"]:
            return jsonify(result), 400

        saved_path = result["file_path"]
        try:
            database.insert_csv_file(
                dataset_name=dataset_name,
                file_name=original_name,
                file_path=saved_path,
                file_size_bytes=os.path.getsize(saved_path),
                row_count=_count_csv_rows(saved_path),
                uploader_id=user.user_id,
                dep_id=session.get("dep_id"),
            )
        except Exception:
            # Don't leave an orphaned file on disk if the DB write fails.
            Path(saved_path).unlink(missing_ok=True)
            raise
    except IntegrityError:
        return jsonify(success=False, message=f"A dataset named '{dataset_name}' already exists."), 409
    except Error:
        app.logger.exception("Upload failed: database error")
        return jsonify(success=False, message="Database error while saving the upload."), 500

    result["dataset_name"] = dataset_name
    return jsonify(result)


@app.route("/create-account", methods=["POST"])
@api_login_required("can_manage_accounts")
def createAccount(user):
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    userrole = data.get("role")
    if userrole not in User.VALID_ROLES:
        return jsonify(success=False, message="Choose a valid account role."), 400

    if not username or not password:
        return jsonify(success=False, message="Enter both a username and password."), 400
    if len(username) > 100:
        return jsonify(success=False, message="Username must be 100 characters or fewer."), 400
    if len(password) < 8:
        return jsonify(success=False, message="Password must be at least 8 characters."), 400
    if len(password.encode("utf-8")) > 72:
        return jsonify(success=False, message="Password must be 72 bytes or fewer."), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        database.create_user(username, hashed, role=userrole, dep_id=session.get("dep_id"))
    except IntegrityError:
        return jsonify(success=False, message=f"The username '{username}' is already taken."), 409
    except Error:
        app.logger.exception("Create account failed")
        return jsonify(success=False, message="Database error while creating the account."), 500

    return jsonify(success=True, message=f"Account '{username}' created.")


@app.route("/delete-data", methods=["POST"])
@api_login_required()
def deleteData(user):
    data = request.get_json(silent=True) or {}
    dataset_name = (data.get("datasetName") or "").strip()
    if not dataset_name:
        return jsonify(success=False, message="Enter the dataset name."), 400

    try:
        record = database.get_csv_by_dataset_name(dataset_name)
        if record is None:
            return jsonify(success=False, message=f"No dataset named '{dataset_name}'."), 404
        if not user.can_delete_dataset(record["uploader_id"]):
            return jsonify(success=False, message="You do not have permission to delete this dataset."), 403

        database.delete_csv_file(record["csv_id"])
    except Error:
        app.logger.exception("Delete failed")
        return jsonify(success=False, message="Database error while deleting the dataset."), 500

    Path(record["file_path"]).unlink(missing_ok=True)
    return jsonify(success=True, message=f"Dataset '{dataset_name}' deleted.")


@app.route("/create-chart", methods=["POST"])
@api_login_required()
def retrieveDataSet(user):
    data = request.get_json(silent=True) or {}
    dataset_name = (data.get("datasetName") or "").strip()

    if data.get("action") != "get_columns":
        return jsonify(success=False, message="Unknown chart action."), 400
    if not dataset_name:
        return jsonify(success=False, message="Choose a dataset."), 400

    try:
        record = database.get_csv_by_dataset_name(dataset_name)
        if record is None:
            return jsonify(success=False, message="Dataset not found."), 404

        with open(record["file_path"], newline="", encoding="utf-8-sig") as csv_file:
            columns = next(csv.reader(csv_file), [])

        return jsonify(success=True, columns=columns)

    except Error:
        app.logger.exception("Database error loading dataset columns")
        return jsonify(success=False, message="Database error loading the dataset."), 500
    except (OSError, UnicodeError, csv.Error):
        app.logger.exception("Could not read dataset columns")
        return jsonify(success=False, message="Could not read the dataset file."), 500



@app.route("/datasets", methods=["GET"])
@api_login_required()
def list_datasets(user):
    try:
        datasets = database.get_all_csv_datasets()
    except Error:
        app.logger.exception("Could not load dataset names")
        return jsonify(success=False, message="Could not load datasets."), 500

    return jsonify(success=True, datasets=datasets)


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
