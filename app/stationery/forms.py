from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError

# Constants for reuse
ITEM_TYPES = [
    ('A4', 'A4 Paper'),
    ('A3', 'A3 Paper'),
    ('A5', 'A5 Paper'),
    ('Sticker Paper 2', 'Sticker Paper - Type 2'),
    ('Sticker Paper 16', 'Sticker Paper - Type 16'),
    ('Sticker Paper 24', 'Sticker Paper - Type 24'),
    ('Card Paper', 'Card Paper'),
    ('Certificate Paper', 'Certificate Paper'),
    ('Staplers', 'Staplers'),
    ('Pins', 'Pins'),
    ('Photo Paper', 'Photo Paper'),
    ('Paper Punch', 'Paper Punch')
]

UNITS = [
    ('boxes', 'Boxes'),
    ('pieces', 'Pieces')
]

LOCATIONS = [
    ('Main Office', 'Main Office')
]

class StationeryForm(FlaskForm):
    item_type = SelectField('Item Type', choices=ITEM_TYPES, validators=[DataRequired()])
    quantity = IntegerField('Initial Quantity', validators=[DataRequired(), NumberRange(min=0)],
                            render_kw={"placeholder": "Enter initial quantity"})
    unit = SelectField('Unit', choices=UNITS, validators=[DataRequired()])
    threshold = IntegerField('Low Stock Threshold', validators=[DataRequired(), NumberRange(min=0)],
                             render_kw={"placeholder": "Alert threshold for low stock"})
    location = SelectField('Location', choices=LOCATIONS, validators=[DataRequired()])
    submit = SubmitField('Add Item')


class StationeryUpdateForm(FlaskForm):
    quantity_change = IntegerField('Quantity Change', validators=[DataRequired(), NumberRange(min=1)],
                                  render_kw={"placeholder": "Enter quantity to add or subtract"})
    action = SelectField('Action', choices=[('add', 'Add Stock'), ('subtract', 'Use Stock')], validators=[DataRequired()])
    threshold = IntegerField('Update Threshold', validators=[Optional(), NumberRange(min=0)],
                             render_kw={"placeholder": "Leave blank to keep unchanged"})
    location = SelectField('Update Location', choices=LOCATIONS, validators=[Optional()])
    submit = SubmitField('Update Item')

    def __init__(self, current_quantity=None, *args, **kwargs):
        """
        Accept current_quantity to validate subtraction does not cause negative stock.
        """
        super().__init__(*args, **kwargs)
        self.current_quantity = current_quantity

    def validate_quantity_change(self, field):
        if self.action.data == 'subtract':
            if self.current_quantity is None:
                raise ValidationError('Current quantity unavailable for validation.')
            if field.data > self.current_quantity:
                raise ValidationError(f'Cannot subtract more than current quantity ({self.current_quantity}).')
