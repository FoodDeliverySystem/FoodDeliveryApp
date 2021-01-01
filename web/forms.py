from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import *
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
#import phonenumbers
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from web.models import User, OrderStatus
from wtforms.fields.html5 import *
from datetime import datetime, date

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phone_no(self, phone):
        user = User.query.filter_by(phone_no=phone.data).first()
        if user:
            raise ValidationError('That phone number is taken. Please use a different one.')

class AgentTipForm(FlaskForm):
    #datetime.now(tz='US/Pacific').replace(tzinfo='UTC')
    start_date = DateField('From', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.utcnow)
    end_date = DateField('To', format='%Y-%m-%d',validators=[DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Calculate Tip')

class AdminTipForm(FlaskForm):
    #datetime.now(tz='US/Pacific').replace(tzinfo='UTC')
    agent_id = SelectField('Agent Name', validators=[DataRequired()], choices=[])
    start_date = DateField('From', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.utcnow)
    end_date = DateField('To  ', format='%Y-%m-%d',validators=[DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Calculate Tip')

class OrderItemsForm(FlaskForm):
    status = SelectField('Status of Order', choices=OrderStatus.choices())
    cust_name = StringField('Customer Name', validators=[DataRequired(), Length(min=3, max=30)])
    phone = StringField('Phone', validators=[DataRequired(), Length(10)])
    cust_addr1 = TextAreaField('Address Line 1', validators=[DataRequired(), Length(min=5, max=65)], render_kw={'class': 'form-control', 'rows': 5, 'cols':5})
    cust_addr2 = TextAreaField('Address Line 2', validators=[Length(min=0, max=65)],  render_kw={'class': 'form-control', 'rows': 5, 'cols':5})
    cust_pincode = StringField('Pin Code', validators=[DataRequired(), Length(min=5, max=12)])
    user_tip = FloatField('Tip', default=0)
    delivery_instructions = TextAreaField('Delivery Instructions',  render_kw={'class': 'form-control', 'rows': 5, 'cols':5}, validators=[Length(min=0, max=300)])
    drinks = remember_me = BooleanField('Drinks')
    submit = SubmitField('Add Order')
    
    # def validate_phone(self, field):
    #     if len(field.data) > 16:
    #         raise ValidationError('length should be less than 16')
    #     try:
    #         input_number = phonenumbers.parse(field.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')
    #     except:
    #         input_number = phonenumbers.parse("+1"+field.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('failed validating with +1')
