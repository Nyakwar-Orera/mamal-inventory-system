from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import date

class AssetForm(FlaskForm):
    name = StringField('Asset Name', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])

    asset_type = SelectField('Type', choices=[
        ('desktop', 'Desktop Computer'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('server', 'Server'),
        ('monitor', 'Monitor'),
        ('Keyboard', 'Keyboard'),
        ('Mouse', 'Mouse'),
        ('CPU', 'CPU'),
        ('TV', 'TV'),
        ('Camera', 'Camera'),
        ('Headphone', 'Headphone / Headset'),
        ('Paper cutter', 'Paper Cutter'),
        ('Stapler', 'Stapler'),
        ('Flash Drive', 'Flash Drive'),
        ('Hard Drive', 'Hard Drive'),
        ('Toner', 'Toner'),
        ('Intercom', 'Intercom'),
        ('UPS', 'UPS'),
        ('RAM', 'RAM'),
        ('Power Cable', 'Power Cable'),
        ('Display Cable', 'Display Cable'),
        ('Fan', 'Fan'),
        ('Pin Remover', 'Pin Remover'),
        ('Scissors', 'Scissors')
    ], validators=[DataRequired()])

    purchase_date = DateField('Purchase Date', default=date.today, validators=[Optional()])
    purchase_cost = FloatField('Purchase Cost', validators=[Optional()])

    location = SelectField('Location', choices=[
        ('', 'Select Location'),
        ('Mamal Boys Lab', 'Mamal Boys Lab'),
        ('Mamal Girls Lab', 'Mamal Girls Lab'),
        ('Masakin', 'Masakin'),
        ('Rabwat', 'Rabwat')
    ], validators=[DataRequired()])

    status = SelectField('Status', choices=[
        ('Available', 'Available'),
        ('In-use', 'In-use'),
        ('Maintenance', 'Maintenance'),
        ('Out of Service', 'Out of Service')
    ], validators=[DataRequired()])

    condition = StringField('Condition', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')


class AssetFilterForm(FlaskForm):
    location = SelectField('Location', choices=[
        ('', 'All Locations'),
        ('Mamal Boys Lab', 'Mamal Boys Lab'),
        ('Mamal Girls Lab', 'Mamal Girls Lab'),
        ('Masakin', 'Masakin'),
        ('Rabwat', 'Rabwat')
    ], validators=[Optional()])

    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('Available', 'Available'),
        ('In-use', 'In-use'),
        ('Maintenance', 'Maintenance'),
        ('Out of Service', 'Out of Service')
    ], validators=[Optional()])

    submit = SubmitField('Filter')
