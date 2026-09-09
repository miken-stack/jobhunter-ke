from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from app import db, login_manager
from app.forms import ApplicationForm, LoginForm, RegistrationForm
from app.models import JobApplication, User

main = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.lower().strip())
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Welcome to JobHunter KE! Your account has been created.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name.split(' ')[0]}.", "success")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html", form=form)


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.index"))


@main.route("/dashboard")
@login_required
def dashboard():
    query = JobApplication.query.filter_by(user_id=current_user.id)

    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(JobApplication.company.ilike(like), JobApplication.position.ilike(like))
        )

    status_filter = request.args.get("status", "").strip()
    if status_filter in JobApplication.STATUSES:
        query = query.filter_by(status=status_filter)

    sort = request.args.get("sort", "newest")
    sort_options = {
        "newest": JobApplication.application_date.desc(),
        "oldest": JobApplication.application_date.asc(),
        "company": JobApplication.company.asc(),
    }
    query = query.order_by(sort_options.get(sort, sort_options["newest"]))

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("APPLICATIONS_PER_PAGE", 10)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    all_applications = JobApplication.query.filter_by(user_id=current_user.id)
    total = all_applications.count()
    interviews = all_applications.filter_by(status="Interview").count()
    offers = all_applications.filter_by(status="Offer").count()
    rejected = all_applications.filter_by(status="Rejected").count()

    return render_template(
        "dashboard.html",
        pagination=pagination,
        applications=pagination.items,
        total=total,
        interviews=interviews,
        offers=offers,
        rejected=rejected,
        search=search,
        status_filter=status_filter,
        sort=sort,
        statuses=JobApplication.STATUSES,
    )


@main.route("/applications/add", methods=["GET", "POST"])
@login_required
def add_application():
    form = ApplicationForm()

    if form.validate_on_submit():
        application = JobApplication(
            company=form.company.data.strip(),
            position=form.position.data.strip(),
            location=(form.location.data or "").strip() or None,
            status=form.status.data,
            interview_date=form.interview_date.data,
            notes=(form.notes.data or "").strip() or None,
            user_id=current_user.id,
        )
        db.session.add(application)
        db.session.commit()

        flash(f"Added {form.position.data} at {form.company.data}.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("application_form.html", form=form, mode="add")


@main.route("/applications/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_application(id):
    application = db.session.get(JobApplication, id) or abort(404)

    if application.user_id != current_user.id:
        abort(403)

    form = ApplicationForm(obj=application)

    if form.validate_on_submit():
        form.populate_obj(application)
        application.location = (application.location or "").strip() or None
        application.notes = (application.notes or "").strip() or None
        db.session.commit()

        flash("Application updated.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("application_form.html", form=form, mode="edit", application=application)


@main.route("/applications/<int:id>/delete", methods=["POST"])
@login_required
def delete_application(id):
    application = db.session.get(JobApplication, id) or abort(404)

    if application.user_id != current_user.id:
        abort(403)

    db.session.delete(application)
    db.session.commit()

    flash("Application deleted.", "info")
    return redirect(url_for("main.dashboard"))
