from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms import *
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from web.models import User
import phonenumbers

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
    order_items = TextAreaField('Order Items', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 10, 'cols':8})
    order_status = FieldList(SelectField(u'Order status', 
                                    choices=[(1, 'Order placed'), (2, 'Cooking in Progress'), (3, 'Assigned to Agent'),
                                             (4, '30min Notification'), (5, '10 min notification'), (6, 'Delivered')]), min_entries=1)
    cust_name = StringField('Customer Name', validators=[DataRequired()])
    cust_phone_no = StringField('Customer Phone Number', validators=[DataRequired()])
    cust_addr1 = TextAreaField('Address 1', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 3, 'cols':5})
    cust_addr2 = TextAreaField('Address 2', render_kw={'class': 'form-control', 'rows': 3, 'cols':5})
    cust_pincode = StringField('Pincode', validators=[DataRequired()])
    submit = SubmitField('Add Order')

    def validate_phone(self, cust_phone_no):
        try:
            p = phonenumbers.parse(cust_phone_no.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
    
                            


