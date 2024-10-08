import json
from pathlib import Path

import pytest

from project.app import app, db

TEST_DB = "test.db"


@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)


def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200


def test_database(client):
    """initial test. ensure that the database exists"""
    tester = Path("test.db").is_file()
    assert tester


def test_empty_db(client):
    """Ensure database is blank"""
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data


def test_login_logout(client):
    """Test login and logout using helper functions"""
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Invalid username" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Invalid password" in rv.data


def test_messages(client):
    """Ensure that user can post messages"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"No entries here so far" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


def test_delete_message(client):
    """Ensure the messages are being deleted"""
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1


def test_search(client):
    # Ensure the database is empty initially
    test_empty_db(client)

    # Log in first to add some posts
    login(client, app.config["USERNAME"], app.config["PASSWORD"])

    # Add a few test entries
    client.post(
        "/add",
        data=dict(title="First Post", text="This is the first test post."),
        follow_redirects=True,
    )
    client.post(
        "/add",
        data=dict(title="Second Post", text="Another test post for search."),
        follow_redirects=True,
    )

    # Test searching for an existing post title
    rv = client.get("/search/", query_string={'query': 'First'})
    assert b"First Post" in rv.data
    assert b"This is the first test post." in rv.data

    # Test searching for text within a post
    rv = client.get("/search/", query_string={'query': 'Another'})
    assert b"Second Post" in rv.data
    assert b"Another test post for search." in rv.data

    # Test searching for a post that does not exist
    rv = client.get("/search/", query_string={'query': 'Nonexistent'})
    assert b"" in rv.data

    # Test empty search query (should just return the search page without any filtering)
    rv = client.get("/search/")
    assert b"Search" in rv.data


def test_delete_without_login(client):
    """Ensure that posts cannot be deleted without login."""
    # Try to delete post without logging in
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    assert data["message"] == "Please log in."
    assert rv.status_code == 401  # Unauthorized access


def test_delete_with_login(client):
    """Ensure that logged-in users can delete posts."""
    # Log in and add a post first
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post(
        "/add",
        data=dict(title="Post to Delete", text="This post will be deleted"),
        follow_redirects=True,
    )

    # Attempt to delete the post
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1
    assert data["message"] == "Post Deleted"
    assert rv.status_code == 200  # Success
