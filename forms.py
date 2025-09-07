from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional, NumberRange
from models import User

class LoginForm(FlaskForm):
    username = StringField('მომხმარებელის სახელი', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('პაროლი', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('მომხმარებელის სახელი', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('ელექტრონული ფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField('პაროლი', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('დაადასტურე პაროლი', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('მომხმარებელის სახელი უკვე არსებობს. გთხოვთ აირჩიოთ სხვა.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('ელექტრონული ფოსტა უკვე რეგისტრირებულია. გთხოვთ აირჩიოთ სხვა.')

class ProfileUpdateForm(FlaskForm):
    username = StringField('მომხმარებელის სახელი', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('ელექტრონული ფოსტა', validators=[DataRequired(), Email()])
    profile_image = FileField('პროფილის სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('მიმდინარე პაროლი', validators=[DataRequired()])
    new_password = PasswordField('ახალი პაროლი', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('დაადასტურე ახალი პაროლი', validators=[DataRequired(), EqualTo('new_password')])

class GameForm(FlaskForm):
    title = StringField('თამაშის სათაური', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('აღწერა', validators=[DataRequired(), Length(min=10)])
    genre = SelectField('ჟანარი', choices=[
        ('action', 'მოქმედება'),
        ('adventure', 'ავანტიურა'),
        ('rpg', 'რპგ'),
        ('strategy', 'სტრატეგიული'),
        ('simulation', 'სიმულაცია'),
        ('sports', 'სპორტული'),
        ('racing', 'რეისინგი'),
        ('puzzle', 'თავსაცეცხლი'),
        ('horror', 'საშინელება'),
        ('shooter', 'სტრელბა'),
        ('platformer', 'პლატფორმერი'),
        ('indie', 'ინდი'),
        ('mmo', 'მმო'),
        ('casual', 'კაზუალური'),
        ('other', 'სხვა')
    ], validators=[DataRequired()])
    download_link = StringField('გადმოწერის ბმული', validators=[DataRequired(), URL()])
    image_url = StringField('თამაშის სურათის URL', validators=[Optional(), URL()])

class CommentForm(FlaskForm):
    content = TextAreaField('კომენტარი', validators=[DataRequired(), Length(min=3, max=500)])

class BanForm(FlaskForm):
    reason = StringField('ბანის მიზეზი', validators=[DataRequired(), Length(max=255)])
    duration_days = IntegerField('ხანგრძლივობა (დღეები)', validators=[NumberRange(min=1, max=365)], default=1)
    permanent = BooleanField('მუდმივი ბანი')

class AssignRoleForm(FlaskForm):
    role = SelectField('როლი', choices=[
        ('user', 'მომხმარებელი'),
        ('moderator', 'მოდერატორი'),
        ('admin', 'ადმინისტრატორი')
    ], validators=[DataRequired()])
