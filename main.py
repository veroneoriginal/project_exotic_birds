from datetime import timedelta
from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, session, abort, request
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, PostForm
from models import db, User, Post, Tag
from faker import Faker

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
    # return User.query.get(int(user_id))
    return User.query.filter_by(id=user_id).first()


@app.cli.command("create-db")
def create_db():
    db.create_all()
    print("Database created successfully.")


def initialize_database(num_users=5, max_posts_per_user=6):
    """Функция, с помощью которой проверяем состояние базы данных и при необходимости заполняем бд"""
    with app.app_context():
        user_count = User.query.count()
        post_count = Post.query.count()
        # проверяем наличие записей в базе данных
        # если бд пустая, генерим данные
        if user_count == 0 and post_count == 0:
            fake = Faker('ru_RU')
            for _ in range(num_users):
                user = User(
                    email=fake.email(),
                    username=fake.user_name(),
                    # password=generate_password_hash(fake.password())
                    password=generate_password_hash('111')
                )
                # Сохраняем пользователя, чтобы получить user.id
                db.session.add(user)
                db.session.commit()

                num_posts = fake.random_int(min=1, max=max_posts_per_user)
                for _ in range(num_posts):
                    post = Post(
                        title=fake.sentence(),
                        content=fake.text(),
                        is_published=fake.boolean(chance_of_getting_true=70),
                        user_id=user.id
                    )
                    db.session.add(post)
            db.session.commit()


# Декоратор указывает, что функция index() будет вызываться,
# когда пользователь обращается к корневому URL ("/") веб-приложения
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
        existing_user = User.query.filter_by(email=email).first()

        # если все совпадает - если такой пользователь существует
        if existing_user:
            if existing_user.email == email:
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
    if current_user.is_authenticated:
        return redirect(url_for('personal_account'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Такого пользователя не существует! Пожалуйста, зарегистрируйтесь!", 'danger')
            return redirect(url_for('registration'))
        elif user and check_password_hash(user.password, form.password.data):
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
    # logout_user завершает текущую сессию пользователя, удаляя его аутентификационные данные из сеанса
    logout_user()
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('index'))


@app.route('/personal_account')
# Декоратор @login_required разрешает доступ только аутентифицированным пользователям.
# Если пользователь не аутентифицирован, он будет перенаправлен на страницу входа.
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
        selected_tags = form.tags.data
        for tag_name in selected_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост создан!', 'success')
        return redirect(url_for('personal_account'))
    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    # post_id создается в момент сохранения нового поста в базе данных
    post = Post.query.get_or_404(post_id)

    # Проверка, опубликован ли пост и имеет ли пользователь доступ к нему
    if not post.is_published:
        if not current_user.is_authenticated:
            flash('Этого поста не существует.', 'warning')
            return redirect(url_for('blog'))
        elif post.user_id != current_user.id:
            flash('Этого поста не существует.', 'warning')
            return redirect(url_for('personal_account'))

    # Определение, является ли текущий пользователь автором поста
    is_author = current_user.is_authenticated and post.user_id == current_user.id

    # Возвращает отрендеренный HTML-шаблон view_post.html, передавая объект post в контексте
    return render_template('view_post.html', post=post, is_author=is_author)


@app.route("/post/<int:post_id>/publish", methods=['POST'])
@login_required
def publish_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user != current_user:
        abort(403)
    post.is_published = True
    db.session.commit()
    flash('Ваш пост опубликован!', 'success')
    return redirect(url_for('blog'))


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash('Вы не имеете прав на удаление этого поста.', 'danger')
        return redirect(url_for('personal_account'))

    db.session.delete(post)
    db.session.commit()
    flash('Пост был успешно удален.', 'success')
    return redirect(url_for('personal_account'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash('Вы не имеете прав на редактирование этого поста.', 'danger')
        return redirect(url_for('view_post', post_id=post.id))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Пост был успешно обновлен.', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    return render_template('edit_post.html', post=post)


@app.route('/blog')
def blog():
    posts = Post.query.filter_by(is_published=True).all()
    return render_template('blog.html', posts=posts)


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
