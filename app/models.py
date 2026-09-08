from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    applications = db.relationship(
        "JobApplication",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company = db.Column(
        db.String(150),
        nullable=False
    )

    position = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150)
    )

    status = db.Column(
        db.String(50),
        default="Applied"
    )

    application_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    interview_date = db.Column(
        db.DateTime,
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )