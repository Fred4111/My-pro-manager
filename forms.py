
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    # 'progress' placed between start and end date
    progress = TextAreaField('Progress (summary/log)', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()], format='%Y-%m-%d')
    status = StringField('Status', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save')

class ProgressEntryForm(FlaskForm):
    content = TextAreaField('Add a progress update', validators=[DataRequired()])
    submit = SubmitField('Add Entry')
