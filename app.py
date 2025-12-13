from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegisterForm, LoginForm, StudyForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from models import db, User, StudyLog, Subject
from sqlalchemy import func
import os
from functools import wraps

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'trackdemic.db')
app.config['SECRET_KEY'] = 'trackdemic_secret_somuch'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db.init_app(app)

with app.app_context():
    db.create_all()

AVATARS = ["avatar1.jpg", "avatar2.jpg", "avatar3.jpg", "avatar4.jpg"]

def calculate_stats(user_id):
    logs = StudyLog.query.filter_by(user_id=user_id).all()
    total_minutes = sum((log.minutes or 0) for log in logs)
    xp = total_minutes // 10
    level = xp // 100
    progress = xp % 100
    return total_minutes, xp, level, progress

def get_badges(xp):
    badges = []
    if xp >= 500:
        badges.append("Study Warrior")
    if xp >= 1000:
        badges.append("Study Elite")
    if xp >= 1500:
        badges.append("Study Master")
    if xp >= 2000:
        badges.append("Study GrandMaster")
    if xp >= 3000:
        badges.append("Study Legend")
    return badges

def _to_date(obj):
    if obj is None:
        return None
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return obj
    if isinstance(obj, datetime):
        return obj.date()
    if isinstance(obj, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(obj, fmt).date()
            except ValueError:
                continue
    return None

def get_streak(user_id):
    logs = StudyLog.query.filter_by(user_id=user_id).all()
    if not logs:
        return 0

    log_dates = []
    for log in logs:
        d = _to_date(log.date)
        if d and (not log_dates or d != log_dates[-1]):
            log_dates.append(d)

    if not log_dates:
        return 0

    log_dates = sorted(set(log_dates), reverse=True)
    streak = 0
    today = date.today()
    most_recent = log_dates[0]

    if most_recent < (today - timedelta(days=1)) and most_recent != today:
        return 0

    expected = most_recent
    for d in log_dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d < expected:
            break

    return streak

def superuser():
    uid = session.get('user_id')
    if not uid:
        return False
    user = User.query.get(uid)
    if not user:
        return False
    return user.username == 'my_username'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def make_session_permanent():
    session.permanent = True

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    user_id = current_user.id
    user = User.query.get(user_id)

    if user is None:
        session.clear()
        flash("User not found, please log in again.", "warning")
        return redirect(url_for('login'))

    if not user.avatar:
        user.avatar = "avatar1.jpg"
        db.session.commit()

    username = user.username if user else "Guest"

    total_minutes, xp, level, progress = calculate_stats(user_id)
    badges = get_badges(xp)
    streak = get_streak(user_id)

    return render_template('index.html',
                            username=username,
                            total_minutes=total_minutes,
                            xp=xp,
                            level=level,
                            progress=progress,
                            badges=badges,
                            streak=streak,
                            current_user=user
                            )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()

    if form.validate_on_submit():
        existing = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing:
            flash("Username or Email already used.", "danger")
            return render_template('register.html', form=form)

        hashed_pw = generate_password_hash(form.password.data)

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            role="user",
            avatar="avatar1.jpg"
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            if not user.avatar:
                user.avatar = "avatar1.jpg"
                db.session.commit()
            flash("Login successful!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)



@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/addlog", methods=["GET", "POST"])
@login_required
def add_log():
    form = StudyForm()
    user_id = current_user.id
    subjects = Subject.query.filter_by(user_id=user_id).all()
    form.subject.choices = [(s.id, s.name) for s in subjects]
    if not subjects:
        flash("Add a subject first before logging study time.", "warning")
        return redirect(url_for("subjects"))
    if form.validate_on_submit():
        subject = Subject.query.get(form.subject.data)
        if not subject or subject.user_id != user_id:
            flash("Invalid subject selected.", "danger")
            return redirect(url_for("add_log"))
        new_log = StudyLog(
            user_id=user_id,
            subject_id=subject.id,
            subject=subject.name,
            minutes=form.minutes.data
        )
        db.session.add(new_log)
        db.session.commit()
        flash("Study log added successfully!", "success")
        return redirect(url_for("home"))
    return render_template("addlog.html", form=form)


@app.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    user_id = current_user.id
    logs = StudyLog.query.filter_by(user_id=user_id).order_by(StudyLog.date.desc(), StudyLog.id.desc()).all()
    if request.method == 'POST':
        action = request.form.get('action')
        log_id = int(request.form.get('log_id'))
        log = StudyLog.query.get_or_404(log_id)
        if action == 'edit':
            new_subject = request.form.get('subject').strip().lower()
            new_minutes = int(request.form.get('minutes'))
            existing_subjects = [l.subject.lower() for l in logs if l.id != log.id]
            if new_subject in existing_subjects:
                flash(f"You already have a log for '{new_subject}'. Choose a different subject.", 'danger')
            else:
                subj = Subject.query.filter_by(user_id=user_id, name=new_subject).first()
                if not subj:
                    flash("Subject not found. Add it first from Subjects page.", "danger")
                else:
                    log.subject = subj.name
                    log.subject_id = subj.id
                    log.minutes = new_minutes
                    db.session.commit()
                    flash("Log updated successfully.", "success")
        elif action == 'delete':
            db.session.delete(log)
            db.session.commit()
            flash(f"Deleted '{log.subject}' and its XP!", "success")
        return redirect(url_for('logs'))
    return render_template('logs.html', logs=logs)

@app.route("/leaderboard")
@login_required
def leaderboard():
    users = db.session.query(
        User.id,
        User.username,
        User.avatar,
        func.coalesce(func.sum(StudyLog.minutes), 0).label('xp')
    ).outerjoin(StudyLog, StudyLog.user_id == User.id) \
    .group_by(User.id) \
    .order_by(func.coalesce(func.sum(StudyLog.minutes), 0).desc()) \
    .all()
    return render_template("leaderboard.html", users=users, enumerate=enumerate)

@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_log(log_id):
    if not superuser():
        flash("you cant edit this", "danger")
        return redirect(url_for('leaderboard'))
    log = StudyLog.query.get_or_404(log_id)
    form = StudyForm(obj=log)
    if form.validate_on_submit():
        log.subject = form.subject.data
        log.minutes = form.minutes.data
        if getattr(form, 'date', None) and form.date.data:
            parsed = _to_date(form.date.data)
            if parsed:
                log.date = parsed
        db.session.commit()
        flash("Done! Log updated :)", "success")
        return redirect(url_for('leaderboard'))
    return render_template('editlog.html', form=form, log=log)

@app.route('/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    if not superuser():
        flash("No, its not allowed", "danger")
        return redirect(url_for('leaderboard'))
    log = StudyLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    flash("Deleted!", "success")
    return redirect(url_for('leaderboard'))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user
    if not user.avatar:
        user.avatar = "avatar1.jpg"
        db.session.commit()
    if request.method == "POST":
        new_username = request.form.get("username")
        if new_username and new_username != user.username:
            existing = User.query.filter_by(username=new_username).first()
            if existing:
                flash("Username already taken.", "danger")
                return redirect(url_for("profile"))
            user.username = new_username
        chosen = request.form.get("avatar")
        if chosen in AVATARS:
            user.avatar = chosen
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile"))
    total_minutes, xp, level, progress = calculate_stats(user.id)
    streak = get_streak(user.id)
    return render_template(
        "profile.html",
        user=user,
        current_user=user,
        avatars=AVATARS,
        xp=xp,
        level=level,
        streak=streak,
        progress=progress,
        total_minutes=total_minutes
    )




@app.route("/subjects")
@login_required
def subjects():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    subject_data = []
    for s in subjects:
        studied = (
            db.session.query(func.coalesce(func.sum(StudyLog.minutes), 0))
            .filter(
                StudyLog.subject_id == s.id,
                StudyLog.user_id == current_user.id
            )
            .scalar()
        )
        progress = (
            min(int((studied / s.goal_minutes) * 100), 100)
            if s.goal_minutes else 0
        )
        subject_data.append({
            "id": s.id,
            "name": s.name,
            "goal_minutes": s.goal_minutes,
            "goal_type": s.goal_type,
            "studied": studied,
            "progress": progress
        })
    return render_template("subjects.html", subjects=subject_data)


@app.route('/subjects/add', methods=['POST'])
@login_required
def add_subject():
    user_id = current_user.id
    count = Subject.query.filter_by(user_id=user_id).count()
    if count >= 8:
        flash("Subject limit reached (8 max).", "danger")
        return redirect(url_for('subjects'))
    name = request.form['name'].strip()
    goal_type = request.form['goal_type']
    goal_minutes = int(request.form.get('goal_minutes', 0))
    exists = Subject.query.filter_by(user_id=user_id, name=name).first()
    if exists:
        flash("You already have a subject with that name.", "danger")
        return redirect(url_for('subjects'))
    new_sub = Subject(
        user_id=user_id,
        name=name,
        goal_type=goal_type,
        goal_minutes=goal_minutes
    )
    db.session.add(new_sub)
    db.session.commit()
    return redirect(url_for('subjects'))

@app.route('/subjects/edit/<int:subject_id>', methods=['POST'])
@login_required
def edit_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    sub.goal_type = request.form['goal_type']
    sub.goal_minutes = int(request.form.get('goal_minutes', 0))
    db.session.commit()
    flash("Subject updated!", "success")
    return redirect(url_for('subjects'))

@app.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    db.session.delete(sub)
    db.session.commit()
    flash("Subject deleted.", "warning")
    return redirect(url_for('subjects'))

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    total_users = User.query.count()
    total_logs = StudyLog.query.count()
    return render_template(
        "admin/dashboard.html",
        users=users,
        total_users=total_users,
        total_logs=total_logs
    )

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    if current_user.role != "admin":
        abort(403)
    users = User.query.order_by(User.id).all()
    return render_template("admin/users.html", users=users)



@app.route("/admin/logs")
@login_required
@admin_required
def admin_logs():
    logs = StudyLog.query.order_by(StudyLog.date.desc()).all()
    return render_template("admin/logs.html", logs=logs)

@app.route("/admin/analytics")
@login_required
@admin_required
def admin_analytics():
    total_users = User.query.count()
    total_logs = StudyLog.query.count()
    total_minutes = db.session.query(
        func.coalesce(func.sum(StudyLog.minutes), 0)
    ).scalar()
    return render_template(
        "admin/analytics.html",
        users=total_users,
        logs=total_logs,
        minutes=total_minutes
    )


@app.route("/admin/settings")
@login_required
@admin_required
def admin_settings():
    return render_template("admin/settings.html")

@app.route("/admin/database")
@login_required
@admin_required
def admin_database():
    return render_template("admin/database.html")

@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    if current_user.role != "admin":
        abort(403)

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Cannot delete admin.", "danger")
        return redirect(url_for("admin_users"))

    StudyLog.query.filter_by(user_id=user.id).delete()
    Subject.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_users"))

if __name__ == '__main__':
    app.run(debug=True)
