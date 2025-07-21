from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional
from datetime import date, timedelta

class CheckoutForm(FlaskForm):
    asset_id = IntegerField('Asset ID', validators=[DataRequired()])
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    expected_return = DateField('Expected Return Date', 
                              default=date.today() + timedelta(days=7),
                              validators=[DataRequired()])
    condition_out = StringField('Condition at Checkout', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Check Out')

class CheckinForm(FlaskForm):
    condition_in = StringField('Condition at Check-in', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Check In')