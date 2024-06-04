from dotenv import dotenv_values
from flask import Flask, render_template
from models import db

# берем переменные окружения из файла
env = dotenv_values(dotenv_path='.env')


DB_URI = f'postgresql+psycopg2://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@{env["DB_HOST"]}:{env["DB_PORT"]}/{env["DB_NAME"]}'
# DB_URI = f'postgresql+psycopg2://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@pg:5432/shop'

# Инициализация приложения
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# app.config['SECRET_KEY'] = env['FLASK_SECRET_KEY']
# app.config['WTF_CSRF_ENABLED'] = True

db.init_app(app)


@app.cli.command("create-db")
def create_db():
    db.create_all()
    print("Database created successfully.")

# Декоратор, указывающий, что функция hello() является callback для корневого URL.
@app.route("/")
def index():
    return render_template('main_page.html')


if __name__ == "__main__":
    app.run(debug=True)