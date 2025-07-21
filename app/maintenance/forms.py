from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class MaintenanceForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    cost = FloatField('Estimated Cost', validators=[Optional()])
    technician = StringField('Technician Name', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Maintenance')

class MaintenanceUpdateForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    cost = FloatField('Actual Cost', validators=[Optional()])
    technician = StringField('Technician Name', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Maintenance')