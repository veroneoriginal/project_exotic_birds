from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Ваш логин', validators=[DataRequired()])
    email = StringField('Ваш email', validators=[DataRequired(), Email()])
    password = PasswordField('Придумайте пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(),
                                    EqualTo('password', message='Пароли не совпадают!')])
    submit = SubmitField('Зарегистрироваться')