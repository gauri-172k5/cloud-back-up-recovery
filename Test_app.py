
from app import app, DATABASE
import sqlite3
from io import BytesIO


# Test 1: Home page
def test_home_page():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200


# Test 2: Upload page
def test_upload_page():
    client = app.test_client()
    response = client.get("/upload-page")

    assert response.status_code == 200
    assert b"Upload Your Backup" in response.data


# Test 3: Backups page
def test_backups_page():
    client = app.test_client()
    response = client.get("/backups")

    assert response.status_code == 200


# Test 4: File upload
def test_file_upload():
    client = app.test_client()

    response = client.post(
        "/upload",
        data={
            "file": (
                BytesIO(b"Test backup content"),
                "test_backup.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"uploaded successfully" in response.data


# Test 5: Restore / Download
def test_restore_backup():
    client = app.test_client()

    # Upload a test file
    client.post(
        "/upload",
        data={
            "file": (
                BytesIO(b"Restore test content"),
                "restore_test.txt"
            )
        },
        content_type="multipart/form-data"
    )

    # Find the uploaded file
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM backups WHERE filename = ? ORDER BY id DESC LIMIT 1",
        ("restore_test.txt",)
    )

    record = cursor.fetchone()
    conn.close()

    assert record is not None

    # Test downloading the file
    response = client.get(f"/restore/{record[0]}")

    assert response.status_code == 200
    assert response.data == b"Restore test content"
# Test 6: Upload without selecting a file
def test_upload_without_file():
    client = app.test_client()

    response = client.post("/upload")

    assert response.status_code == 200
    assert b"No file selected!" in response.data
    # Test 7: Restore an unknown backup
def test_restore_unknown_backup():
    client = app.test_client()
    response = client.get("/restore/99999999")
    assert response.status_code == 200
    assert b"Backup not found!" in response.data
    # Test 8: Restore a missing backup file

def test_restore_missing_file():
    client = app.test_client()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO backups (filename, backup_path) VALUES (?, ?)",
        ("missing.txt", "backups/missing.txt")
    )

    file_id = cursor.lastrowid
    conn.commit()
    conn.close()

    response = client.get(f"/restore/{file_id}")

    assert response.status_code == 200
    assert b"Backup file is missing!" in response.data