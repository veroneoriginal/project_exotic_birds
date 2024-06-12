from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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
    tags = SelectMultipleField('Tags', choices=[('nature', 'Природа'), ('birds', 'Птицы'), ('animals', 'Животные')])
    submit = SubmitField('Создать пост')
