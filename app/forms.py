from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    ValidationError,
)

from app.models import JobApplication, User


class RegistrationForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, message="Use at least 8 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )

    def validate_email(self, field):
        email = field.data.lower().strip()
        if User.query.filter_by(email=email).first():
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class ApplicationForm(FlaskForm):
    company = StringField("Company", validators=[DataRequired(), Length(max=150)])
    position = StringField("Position", validators=[DataRequired(), Length(max=150)])
    location = StringField("Location", validators=[Optional(), Length(max=150)])
    status = SelectField("Status", choices=[(s, s) for s in JobApplication.STATUSES])
    interview_date = DateField("Interview date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
