from datetime import timedelta

from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms import RegistrationForm, LoginForm, PostForm
from models import db, User, Post

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

        # Проверка уникальности имени пользователя и электронной почты

        # выражение справа создает запрос к бд для поиска user-a,
        # у которого username или email совпадает с теми, что были введены в форму
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        # вернет объект - <User 3>
        print(existing_user)

        # <class 'models.user.User'>
        print(type(existing_user))

        # если все совпадает - если такой пользователь существует
        if existing_user:

            if existing_user.username == username or existing_user.email == email:
                form.form_errors.append('Такой пользователь уже есть.')

            return render_template('registration.html', form=form)

        # Хэширование пароля и создание нового пользователя

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
    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('personal_account.html', posts=user_posts)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост создан!', 'success')
        return redirect(url_for('personal_account'))
    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)


if __name__ == "__main__":
    app.run(debug=True)
