from dotenv import dotenv_values
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

from forms import RegistrationForm
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

db.init_app(app)
migrate = Migrate(app, db)


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

        # сообщение flash отображается только один раз после следующего запроса
        flash('Вы успешно зарегистрировались! Теперь можете войти в личный кабинет')
        return redirect(url_for('login'))

    # form используется для рендеринга полей формы
    return render_template('registration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
