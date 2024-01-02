from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, FileField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email, InputRequired, EqualTo
from wtforms.fields.simple import PasswordField, SubmitField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Add more fields as needed

    submit = SubmitField('Update User')

class ChangeUserRoleForm(FlaskForm):
    # Define the choices for the role field
    ROLES = [
        ('normal', 'Normal'),
        ('admin', 'Admin'),
        ('superuser', 'Superuser')
    ]

    role = SelectField('Role', choices=ROLES, validators=[DataRequired()])
    submit = SubmitField('Change Role')
    
class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    
    
class CustomerProfileForm(FlaskForm):
    customer_name = StringField('Name', validators=[DataRequired()])
    customer_email = StringField('Email', validators=[DataRequired(), Email()])
    customer_location = StringField('Location')

class EditProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    details = TextAreaField('Details', validators=[DataRequired()])
    image = FileField('Product Image')

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    details = TextAreaField('Details', validators=[DataRequired()])
    image = FileField('Image')


