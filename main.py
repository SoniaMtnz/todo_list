from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
import sqlite3
from forms import RegisterForm, LoginForm, AddTask


from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = "T4Jj#0Q)EWtfz4T8"
bootstrap = Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create Database
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Create a User Table for registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


#  Creating the list's table
class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(100), nullable=False)


with app.app_context():
    db.create_all()


# Create the list where could save tasks
# tasks = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash ("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("create_list"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again!")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("create_list"))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    flash("You logged out!")
    return redirect(url_for('login'))


@app.route("/create-list", methods=["GET", "POST"])
def create_list():
    form = AddTask()
    if form.validate_on_submit():
        description_task = form.description.data
        result = db.session.execute(db.select(Task))
        task = result.scalar()
        if task:
            flash("Task added!")
            new_task = Task(
                description=form.description.data,
            )
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("create_list"))

    return render_template("create-list.html", form=form, current_user=current_user)

@app.route("/my-list", methods=["GET", "POST"])
def my_list():
    tasks = Task.query.all()
    return render_template("my-list.html", tasks=tasks, current_user=current_user)

if __name__ == "__main__":
    app.run(debug=True)


