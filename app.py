
from flask import Flask, request, send_file, redirect
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
from html import escape

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "backups")
DATABASE = os.path.join(BASE_DIR, "backup.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Database creation
def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            backup_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Cloud Backup and Recovery</title>
    </head>
    <body style="margin:0; font-family:Arial; background:#f2f5fa;">

        <div style="background:#102a56; color:white;
                    padding:25px; text-align:center;">
            <h1>Cloud Backup and Recovery Management System</h1>
            <p>Secure Backup and Easy Recovery</p>
        </div>

        <div style="text-align:center; padding:60px;">

            <div style="background:white; padding:30px;
                        margin:20px auto; width:300px;
                        border-radius:12px;">
                <h2>Upload Backup</h2>
                <p>Upload your files safely.</p>
                <a href="/upload-page">Upload Now</a>
            </div>

            <div style="background:white; padding:30px;
                        margin:20px auto; width:300px;
                        border-radius:12px;">
                <h2>Recover Backup</h2>
                <p>View and download your backups.</p>
                <a href="/backups">Recover Now</a>
            </div>

        </div>
    </body>
    </html>
    """


# Upload page
@app.route("/upload-page")
def upload_page():
    return """
    <html>
    <head>
        <title>Upload Backup</title>
    </head>
    <body style="font-family:Arial; text-align:center;
                 padding:50px;">

        <h1>Upload Your Backup</h1>

        <form action="/upload" method="POST"
              enctype="multipart/form-data">

            <input type="file" name="file" required>
            <br><br>

            <button type="submit">Upload Backup</button>
        </form>

        <br>
        <a href="/">Back to Home</a>

    </body>
    </html>
    """


# Upload file
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return "No file selected!"

    file = request.files["file"]

    if file.filename == "":
        return "No file selected!"

    filename = secure_filename(file.filename)

    if not filename:
        return "Invalid filename!"

    unique_name = str(uuid.uuid4()) + "_" + filename
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    file.save(file_path)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO backups (filename, backup_path) VALUES (?, ?)",
        (filename, file_path)
    )

    conn.commit()
    conn.close()

    return """
    <h2>File uploaded successfully!</h2>
    <a href="/">Back to Home</a><br><br>
    <a href="/backups">View Backups</a>
    """


# View backup history
@app.route("/backups")
def list_backups():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, filename, created_at FROM backups ORDER BY id DESC"
    )

    records = cursor.fetchall()
    conn.close()

    html = """
    <html>
    <head>
        <title>Backup History</title>
    </head>
    <body style="font-family:Arial; text-align:center;
                 padding:30px;">

        <h1>Your Backup History</h1>

        <table border="1" cellpadding="12"
               style="margin:auto; border-collapse:collapse;">

        <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Date and Time</th>
            <th>Restore</th>
        </tr>
    """

    for record in records:
        file_id, filename, created_at = record

        html += f"""
        <tr>
            <td>{file_id}</td>
            <td>{escape(filename)}</td>
            <td>{escape(str(created_at))}</td>
            <td>
                <a href="/restore/{file_id}">Download</a>
            </td>
        </tr>
        """

    html += """
        </table>

        <br><br>
        <a href="/">Back to Home</a>

    </body>
    </html>
    """

    return html


# Restore / Download file
@app.route("/restore/<int:file_id>")
def restore(file_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT filename, backup_path FROM backups WHERE id = ?",
        (file_id,)
    )

    record = cursor.fetchone()
    conn.close()

    if record is None:
        return "Backup not found!"

    filename, file_path = record

    if not os.path.isfile(file_path):
        return "Backup file is missing!"

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


# Start application
if __name__ == "__main__":
    create_database()
    print(app.url_map)
    app.run(debug=True)
