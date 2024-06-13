from faker import Faker
from werkzeug.security import generate_password_hash
from models import db, User, Post, Tag


def initialize_database(num_users=5, max_posts_per_user=6):
    """Функция, с помощью которой проверяем состояние базы данных и при необходимости заполняем бд"""
    # with app.app_context():
    user_count = User.query.count()
    post_count = Post.query.count()
    # проверяем наличие записей в базе данных
    # если бд пустая, генерим данные
    if user_count == 0 and post_count == 0:
        Faker.seed(42)
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

        # Наполнение базы данных тегами
        # Выполняется внутри контекста, чтобы Flask знал, какое приложение будет использоваться
        tags = [fake.unique.word() for _ in range(7)]
        tag_objects = [Tag(name=tag_name) for tag_name in tags]

        # Назначение тегов постам
        posts = Post.query.all()
        for post in posts:
            num_tags = fake.random_int(min=1, max=3)
            random_tags = fake.random_elements(elements=tag_objects, length=num_tags, unique=True)
            for tag in random_tags:
                post.tags.append(tag)

        db.session.commit()
