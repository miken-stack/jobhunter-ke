from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import db, login_manager
from app.models import User, JobApplication

main = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("main.register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(
            url_for("main.dashboard")
        )

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        email = request.form["email"].lower().strip()
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(
                url_for("main.dashboard")
            )

        flash("Invalid email or password.")

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("main.index"))


@main.route("/dashboard")
@login_required
def dashboard():

    applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).order_by(
        JobApplication.application_date.desc()
    ).all()

    total = len(applications)

    interviews = len([
        app for app in applications
        if app.status == "Interview"
    ])

    offers = len([
        app for app in applications
        if app.status == "Offer"
    ])

    rejected = len([
        app for app in applications
        if app.status == "Rejected"
    ])

    return render_template(
        "dashboard.html",
        applications=applications,
        total=total,
        interviews=interviews,
        offers=offers,
        rejected=rejected
    )


@main.route("/applications/add", methods=["POST"])
@login_required
def add_application():

    application = JobApplication(
        company=request.form["company"],
        position=request.form["position"],
        location=request.form.get("location"),
        status=request.form.get(
            "status",
            "Applied"
        ),
        notes=request.form.get("notes"),
        user_id=current_user.id
    )

    db.session.add(application)
    db.session.commit()

    flash("Application added successfully.")

    return redirect(
        url_for("main.dashboard")
    )


@main.route("/applications/<int:id>/delete")
@login_required
def delete_application(id):

    application = JobApplication.query.get_or_404(id)

    if application.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(application)
    db.session.commit()

    return redirect(
        url_for("main.dashboard")
    )