from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional


class PhoneForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired()])
    delay = IntegerField('Delay', validators=[Optional()])
    unit = SelectField('Time Unit', choices=[('s', 'seconds'),
                                             ('m', 'minutes'),
                                             ('h', 'hours'),
                                             ('d', 'days')])
    submit = SubmitField('Call')
