from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from appfleshi.models import User

ALLOWED_EMAIL_DOMAINS = [
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "yahoo.com",
    "live.com"
]


class PhotoForm(FlaskForm):
    photo = FileField('Foto', validators=[DataRequired()])
    submit = SubmitField('Postar')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Usuário não encontrado. Crie uma conta!")
        return None

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail já cadastrado. Use outro e-mail ou faça login.")

        from email.utils import parseaddr
        _, address = parseaddr(email.data)

        if "@" not in address:
            raise ValidationError("E-mail inválido.")

        domain = address.split("@")[1].lower()

        if domain not in ALLOWED_EMAIL_DOMAINS:
            allowed = ", ".join(ALLOWED_EMAIL_DOMAINS)
            raise ValidationError(f"Domínio de e-mail não permitido. Utilize: {allowed}")

        return None

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Nome de usuário já cadastrado, use outro nome ou faça login.")
        return None

class PhotoForm(FlaskForm):
    photo = FileField('Foto', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Imagens apenas!')])
    submit = SubmitField('Postar')


