from datetime import timedelta

from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required

from forms import RegistrationForm, LoginForm
from models import db, User

# берем переменные окружения из файла
env = dotenv_values(dotenv_path='.env')

DB_URI = f'postgresql+psycopg2://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@{env["POSTGRES_HOST"]}:{env["POSTGRES_PORT"]}/{env["POSTGRES_DB"]}'
# DB_URI = f'postgresql+psycopg2://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@pg:5432/shop'

# Инициализация приложения
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = env['FLASK_SECRET_KEY']
app.config['WTF_CSRF_ENABLED'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Сессия будет истекать через 1 день

db.init_app(app)
migrate = Migrate(app, db)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# регистрирует функцию load_user как функцию, кот.будет исп-ся для загрузки user из бд по его id
@login_manager.user_loader
def load_user(user_id):
    """ Функция, которая принимает id user-a и возвращает объект пользователя из базы данных"""
    return User.query.get(int(user_id))


@app.cli.command("create-db")
def create_db():
    db.create_all()
    print("Database created successfully.")


# Декоратор, указывающий, что функция hello() является callback для корневого URL.
@app.route("/")
def index():
    return render_template('main_page.html')


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Автоматически аутентифицируем пользователя
        login_user(new_user)

        return redirect(url_for('personal_account'))

    # form используется для рендеринга полей формы
    return render_template('registration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session.permanent = True  # Делает сессию постоянной
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('personal_account'))
        else:
            form.password.errors.append('Неправильный email или пароль')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('Вы успешно вышли из системы!', 'success')
    return redirect(url_for('index'))


@app.route('/personal_account')
@login_required
def personal_account():
    return render_template('personal_account.html')


if __name__ == "__main__":
    app.run(debug=True)
