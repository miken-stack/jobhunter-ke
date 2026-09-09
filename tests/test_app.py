import pytest

from app import create_app, db
from app.models import JobApplication, User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, email="jane@example.com", password="password123", name="Jane Doe"):
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="jane@example.com", password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


# ---------- Public pages ----------

def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"JobHunter" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"log in" in response.data.lower()


# ---------- Registration ----------

def test_register_creates_user(app, client):
    response = register(client)
    assert response.status_code == 200

    with app.app_context():
        assert User.query.filter_by(email="jane@example.com").first() is not None


def test_register_rejects_duplicate_email(client):
    register(client)
    client.post("/logout")
    response = register(client)
    assert b"already exists" in response.data


def test_register_rejects_mismatched_passwords(client):
    response = client.post(
        "/register",
        data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "password123",
            "confirm_password": "somethingelse",
        },
    )
    assert b"must match" in response.data


def test_register_rejects_short_password(client):
    response = client.post(
        "/register",
        data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "short",
            "confirm_password": "short",
        },
    )
    assert b"at least 8" in response.data.lower()


# ---------- Login ----------

def test_login_with_valid_credentials(client):
    register(client)
    client.post("/logout")
    response = login(client)
    assert response.status_code == 200

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200


def test_login_with_wrong_password_fails(client):
    register(client)
    client.post("/logout")
    response = login(client, password="wrongpassword")
    assert b"Invalid email or password" in response.data


# ---------- Applications ----------

def test_add_application_requires_login(client):
    response = client.post(
        "/applications/add",
        data={"company": "Safaricom", "position": "Analyst", "status": "Applied"},
        follow_redirects=True,
    )
    assert b"log in" in response.data.lower()


def test_add_application(app, client):
    register(client)
    response = client.post(
        "/applications/add",
        data={
            "company": "Safaricom",
            "position": "Product Analyst",
            "location": "Nairobi",
            "status": "Applied",
            "notes": "Referred by a friend",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Product Analyst" in response.data

    with app.app_context():
        assert JobApplication.query.count() == 1


def test_edit_application(app, client):
    register(client)
    client.post(
        "/applications/add",
        data={"company": "Safaricom", "position": "Analyst", "status": "Applied"},
    )

    with app.app_context():
        application_id = JobApplication.query.first().id

    client.post(
        f"/applications/{application_id}/edit",
        data={"company": "Safaricom", "position": "Senior Analyst", "status": "Interview"},
        follow_redirects=True,
    )

    with app.app_context():
        updated = db.session.get(JobApplication, application_id)
        assert updated.position == "Senior Analyst"
        assert updated.status == "Interview"


def test_delete_application(app, client):
    register(client)
    client.post(
        "/applications/add",
        data={"company": "Safaricom", "position": "Analyst", "status": "Applied"},
    )

    with app.app_context():
        application_id = JobApplication.query.first().id

    client.post(f"/applications/{application_id}/delete", follow_redirects=True)

    with app.app_context():
        assert db.session.get(JobApplication, application_id) is None


def test_cannot_delete_another_users_application(app, client):
    register(client, email="owner@example.com")
    client.post(
        "/applications/add",
        data={"company": "Safaricom", "position": "Analyst", "status": "Applied"},
    )

    with app.app_context():
        application_id = JobApplication.query.first().id

    client.post("/logout")
    register(client, email="intruder@example.com")

    response = client.post(f"/applications/{application_id}/delete")
    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(JobApplication, application_id) is not None


def test_dashboard_search_filters_results(app, client):
    register(client)
    # follow_redirects so the one-time "Added ..." flash message is consumed
    # on the redirect target rather than lingering into our assertion below.
    client.post(
        "/applications/add",
        data={"company": "Safaricom", "position": "Analyst", "status": "Applied"},
        follow_redirects=True,
    )
    client.post(
        "/applications/add",
        data={"company": "Equity Bank", "position": "Engineer", "status": "Interview"},
        follow_redirects=True,
    )

    response = client.get("/dashboard?q=Equity")
    assert b"Equity Bank" in response.data
    assert b"Safaricom" not in response.data
