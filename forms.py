from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, BooleanField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from models import Tag


class RegistrationForm(FlaskForm):
    """Форма на странице регистрации"""
    username = StringField('Ваш логин', validators=[DataRequired()])
    email = StringField('Ваш email', validators=[DataRequired(), Email()])
    password = PasswordField('Придумайте пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                                     EqualTo('password',
                                                                             message='Пароли не совпадают!')])
    submit = SubmitField('Зарегистрироваться')
    form_errors = []


class LoginForm(FlaskForm):
    """Форма на странице авторизации"""
    email = StringField('Ваш email', validators=[DataRequired(), Email()])
    password = PasswordField('Ваш пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class PostForm(FlaskForm):
    """Форма для создания поста"""
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    content = TextAreaField('Content', validators=[DataRequired()])
    # SelectMultipleField - позволяет пользователю выбирать несколько значений из выпадающего списка
    # coerce=int: значения, выбранные пользователем, должны быть приведены к int.
    # Значения тегов будут ID тегов из базы данных, которые являются целыми числами.
    tags = SelectMultipleField('Tags', coerce=int)
    remove_all_tags = BooleanField('Удалить теги')
    submit = SubmitField('Создать пост')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Заполнение поля tags списком тегов из базы данных
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.all()]
