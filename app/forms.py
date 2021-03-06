from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(_l("Repeat Password"), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l("Register"))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_("Please use a different username."))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_("Please use a different email address."))


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
    new_password = PasswordField("New Password")
    new_password2 = PasswordField("Repeat new password", validators=[EqualTo("new_password")])
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, *kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_("please use a different name!!!"))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(_l("New Password"), validators=[DataRequired()])
    new_password2 = PasswordField(_l("Repeat new password"), validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField(_l("Submit"))

class PostForm(FlaskForm):
    post = TextAreaField(_l("Write something"), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Post it!'))



########### ############ ############
class FootballForm(FlaskForm):
    player_name = StringField("Фамилия игрока", validators=[DataRequired()])
    player_number = IntegerField("Номер", validators=[DataRequired()])
    position = SelectMultipleField("Position",
                                   choices=[("вратарь", 'Вратарь'), ("защитник", 'Защитник'),
                                            ("полузащитник", 'Полузащитник'), ("нападающий", "Нападающий")],
                                   default=["защитник"])
    age = IntegerField("Возраст")
    submit = SubmitField("Добавить игрока")


class RecieptForm(FlaskForm):
    ingredient_1 = StringField("Ингридиент 1", validators=[DataRequired()])
    quantity_1 = IntegerField("Количество (грамм)", validators=[DataRequired()])
    ingredient_2 = StringField("Ингридиент 2", validators=[DataRequired()])
    quantity_2 = IntegerField("Количество (грамм)",validators=[DataRequired()])
    salt = SelectMultipleField("Посолить?", choices=[('1', 'да'), ('2', "нет")])
    submit = SubmitField("Добавить рецепт")


class PetForm(FlaskForm):
    pet_1 = StringField("Animal 1", validators=[DataRequired()])
    pet_1_name = StringField("Name", validators=[DataRequired()])
    sex_1 = SelectMultipleField("Sex of first animal:", choices=[("1", "male"), ("2", "female")])
    pet_2 = StringField("Animal 2", validators=[DataRequired()])
    pet_2_name = StringField("Name", validators=[DataRequired()])
    sex_2 = SelectMultipleField("Sex of second animal:", choices=[("1", "male"), ("2", "female")])
    submit = SubmitField("Add animals!")



