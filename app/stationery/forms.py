from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class StationeryForm(FlaskForm):
    item_type = SelectField('Item Type', choices=[
        ('A4', 'A4 Paper'),
        ('A3', 'A3 Paper'),
        ('A5', 'A5 Paper'),
        ('Sticker Paper 2', 'Sticker Paper - Type 2'),
        ('Sticker Paper 16', 'Sticker Paper - Type 16'),
        ('Sticker Paper 24', 'Sticker Paper - Type 24'),
        ('Certificate Paper', 'Certificate Paper'),
        ('Staplers', 'Staplers'),
        ('Pins', 'Pins'),
        ('Photo Paper', 'Photo Paper'),
        ('Paper Punch', 'Paper Punch')  # Added Paper Punch as an item type
    ], validators=[DataRequired()])
    
    quantity = IntegerField('Initial Quantity', validators=[DataRequired(), NumberRange(min=0)])
    
    unit = SelectField('Unit', choices=[
        ('boxes', 'Boxes'),
        ('pieces', 'Pieces')  # Allowing "pieces" for countable items like Staplers, Pins, Paper Punches
    ], validators=[DataRequired()])
    
    threshold = IntegerField('Low Stock Threshold', validators=[DataRequired(), NumberRange(min=0)])
    
    location = SelectField('Location', choices=[
        ('Main Office', 'Main Office')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Add Item')


class StationeryUpdateForm(FlaskForm):
    quantity_change = IntegerField('Quantity Change', validators=[DataRequired(), NumberRange(min=1)], default=1)
    
    action = SelectField('Action', choices=[
        ('add', 'Add Stock'),
        ('subtract', 'Use Stock')
    ], validators=[DataRequired()])
    
    threshold = IntegerField('Update Threshold', validators=[Optional(), NumberRange(min=0)])
    
    location = SelectField('Update Location', choices=[
        ('Main Office', 'Main Office')
    ], validators=[Optional()])
    
    submit = SubmitField('Update Item')
