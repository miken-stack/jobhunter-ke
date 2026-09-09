from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    applications = db.relationship(
        "JobApplication",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="JobApplication.application_date.desc()",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class JobApplication(db.Model):
    STATUSES = ("Applied", "Interview", "Offer", "Rejected")

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Applied", nullable=False)
    application_date = db.Column(db.DateTime, default=utcnow, nullable=False)
    interview_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    def __repr__(self):
        return f"<JobApplication {self.position} @ {self.company}>"
