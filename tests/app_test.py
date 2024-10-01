from pathlib import Path

from project.app import app, init_db, flaskr_root


def test_index():
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")

    assert response.status_code == 200
    assert response.data == b"Hello, World!"


def test_database():
    init_db()
    assert Path(flaskr_root, Path("flaskr.db")).is_file()
