# model.py
from wtforms import SubmitField, BooleanField, IntegerField, StringField, PasswordField, validators, TextAreaField
from flask_wtf import FlaskForm

class AuditRegForm(FlaskForm):
    account_number = IntegerField('Account Number (0-9)', [
        validators.DataRequired(message='Account number is required'),
        validators.NumberRange(min=0, max=9, message='Account number must be between 0 and 9')
    ], render_kw={"placeholder": "Enter a number between 0-9"})
    name_first = StringField('First Name', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your first name"})
    name_last = StringField('Last Name', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your last name"})
    email = StringField('Email Address', [validators.DataRequired(), 
        validators.Email(), validators.Length(min=6, max=35)],
        render_kw={"placeholder": "example@email.com"})
    employee_id = StringField('Unique Employee ID', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your employee ID"})
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=6, message='Password must be at least 6 characters'),
        validators.EqualTo('confirm', 
        message='Passwords must match')],
        render_kw={"placeholder": "Enter a password (min 6 characters)"})
    confirm = PasswordField('Repeat Password',
        render_kw={"placeholder": "Confirm your password"})
    submit = SubmitField('Submit')

class PatientRegForm(FlaskForm):
    account_number = IntegerField('Account Number (0-9)', [
        validators.DataRequired(message='Account number is required'),
        validators.NumberRange(min=0, max=9, message='Account number must be between 0 and 9')
    ], render_kw={"placeholder": "Enter a number between 0-9"})
    name_first = StringField('First Name', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your first name"})
    name_last = StringField('Last Name', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your last name"})
    email = StringField('Email Address', [validators.DataRequired(), 
        validators.Email(), validators.Length(min=6, max=35)],
        render_kw={"placeholder": "example@email.com"})
    phone = StringField('Phone Number', [validators.DataRequired(),
        validators.Length(min=10, message='Phone number must be at least 10 digits')],
        render_kw={"placeholder": "Enter your phone number (10+ digits)"})
    city = StringField('City', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your city"})
    zip_code = StringField('Zipcode', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your zip code"})
    insurance = StringField('Insurance #', [validators.DataRequired()],
        render_kw={"placeholder": "Enter your insurance number"})
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=6, message='Password must be at least 6 characters'),
        validators.EqualTo('confirm', 
        message='Passwords must match')],
        render_kw={"placeholder": "Enter a password (min 6 characters)"})
    confirm = PasswordField('Repeat Password',
        render_kw={"placeholder": "Confirm your password"})
    submit = SubmitField('Submit')
class LogForm(FlaskForm):
    user_name = StringField('Account Address', [validators.DataRequired()])
    contract_address = StringField('Contract Address (If Audit put 0)', [validators.DataRequired()])
    password = PasswordField('Your Password', [validators.DataRequired()])
    submit = SubmitField('Submit')
class PatientActions(FlaskForm):
    start_visit = StringField('Get an Appointment (Starts a new Medical Record)', [validators.DataRequired()])
    add_doctors = StringField('Add doctor audits', [validators.DataRequired()])
    remove_doctors = StringField('Remove doctor audits', [validators.DataRequired()])
    add_audits = StringField('Add other audits', [validators.DataRequired()])
    remove_audits = StringField('Remove other audits', [validators.DataRequired()])
    print_record = StringField('Print Medical Records', [validators.DataRequired()])
    delete_record = StringField('Delete Medical Records', [validators.DataRequired()])
class AuditActions(FlaskForm):
    contract_address =  StringField('Patient Contract Address (QR code in registration)', [validators.DataRequired()])
    print_record = StringField('Print Medical Records', [validators.DataRequired()])
    update_record_id = StringField('Update Medical Records', [validators.DataRequired()])
    update_record_rec = TextAreaField('New Record', [validators.DataRequired()],render_kw={"rows": 10, "cols": 11})
    query = StringField('Query Medical Records')
    copy_record = StringField('Copy Medical Records', [validators.DataRequired()])
    delete_record = StringField('Delete Medical Records', [validators.DataRequired()])



