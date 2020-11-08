from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import *
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import phonenumbers
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from web.models import User, OrderStatus

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
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

class OrderItemsForm(FlaskForm):
    #company = SelectField("Company", choices=Company.choices(), coerce=Company.coerce)
    order_items = TextAreaField('Order Items', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 10, 'cols':8})
    #status = StringField('Status of Order', validators=[DataRequired()], default=OrderStatus.accepted.value)
    status = SelectField('Status of Order', choices=OrderStatus.choices())
    cust_name = StringField('Customer Name', validators=[DataRequired(), Length(min=3, max=30)])
    cust_phone_no = StringField('Customer Phone', validators=[DataRequired(), Length(min=5, max=15)])
    cust_addr1 = StringField('Address Line 1', validators=[DataRequired(), Length(min=5, max=65)])
    cust_addr2 = StringField('Address Line 2', validators=[DataRequired(), Length(min=0, max=65)])
    cust_pincode = StringField('Pin Code', validators=[DataRequired(), Length(min=5, max=12)])
    submit = SubmitField('Add Order')
