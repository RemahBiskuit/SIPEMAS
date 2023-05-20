from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Email, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    nama = StringField('Nama', validators=[DataRequired()])
    alamat = StringField('Alamat', validators=[DataRequired()])
    notelp = StringField('No. Telp', validators=[DataRequired(), Length(min=12, max=13)])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    submit = SubmitField(label='Login')

class TambahUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    nama = StringField('Nama', validators=[DataRequired()])
    alamat = StringField('Alamat', validators=[DataRequired()])
    notelp = StringField('No. Telp', validators=[DataRequired(), Length(min=12, max=13)])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField(label='Tambah User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    nama = StringField('Nama', validators=[DataRequired()])
    alamat = StringField('Alamat', validators=[DataRequired()])
    notelp = StringField('No. Telp', validators=[DataRequired(), Length(min=12, max=13)])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField(label='Ubah User')

class TambahRoleForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    submit = SubmitField(label='Tambah Role')

class EditRoleForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    submit = SubmitField(label='Ubah Role')

class UbahProfilForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nama = StringField('Nama', validators=[DataRequired()])
    alamat = StringField('Alamat', validators=[DataRequired()])
    notelp = StringField('No. Telp', validators=[DataRequired(), Length(min=12, max=13)])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField(label='Ubah Profil')

class PhotoMaskForm(FlaskForm):
    image = FileField('Choose image:',
                      validators=[
                          FileAllowed(['jpg', 'jpeg', 'png'], 'The allowed extensions are: .jpg, .jpeg and .png')])

    submit = SubmitField('Detect mask')