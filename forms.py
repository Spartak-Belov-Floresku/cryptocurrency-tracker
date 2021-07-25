from flask_wtf import FlaskForm
from wtforms import StringField
from flask_wtf.file import  FileField, FileAllowed
from wtforms_alchemy import model_form_factory
from wtforms.validators import InputRequired
from wtforms.widgets import PasswordInput

from models import db, User


BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session



class RegisterUserForm(FlaskForm):
    """Register user form"""

    full_name = StringField('Full name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()], render_kw={"class": "form-control chek_username"})
    password = StringField('Password', validators=[InputRequired()], widget=PasswordInput(hide_value=False))



class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField('Username', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired()], widget=PasswordInput(hide_value=False))



class RecoverPassword(FlaskForm):
    """recover password for username"""

    username = StringField('Username', validators=[InputRequired()])
    code = StringField('Code', render_kw={"disabled": True})



class SettingsForm(FlaskForm):
    """change settings form"""
    
    full_name = StringField('Full name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()], render_kw={"class": "form-control chek_username"})
    image = FileField('Image only 4MB', validators = [FileAllowed(['jpg','jpeg', 'png'], 'Images only!')])
    new_password = StringField('New password', widget=PasswordInput(hide_value=False))
    old_password = StringField('Old password', validators=[InputRequired()], widget=PasswordInput(hide_value=False))
