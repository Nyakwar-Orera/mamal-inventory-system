from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class AssetForm(FlaskForm):
    name = StringField('Asset Name', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])

    asset_type = SelectField('Type', choices=[
        ('Monitor', 'Monitor'),
        ('Keyboard', 'Keyboard'),
        ('Mouse', 'Mouse'),
        ('CPU', 'CPU'),
        ('TV', 'TV'),
        ('Laptop', 'Laptop'),
        ('Printer', 'Printer'),
        ('Server', 'Server'),
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

    search = StringField('Search', validators=[Optional()])
    submit = SubmitField('Filter')


class TransferAssetForm(FlaskForm):
    asset_id = SelectField('Asset', coerce=int, validators=[DataRequired()])
    to_location = SelectField('Transfer To', choices=[
        ('Mamal Boys Lab', 'Mamal Boys Lab'),
        ('Mamal Girls Lab', 'Mamal Girls Lab'),
        ('Masakin', 'Masakin'),
        ('Rabwat', 'Rabwat')
    ], validators=[DataRequired()])
    submit = SubmitField('Transfer')
