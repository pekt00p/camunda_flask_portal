__author__ = 'Oleg Ladizhensky'

from wtforms import StringField, validators
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm


class CamundaTask(FlaskForm):
    process_key = ''
    process_name = ''
    process_description = ''
    task_id = ''



class StartProcessForm(CamundaTask):
    input_variable_wtg_fault_description_init = StringField('input_variable_wtg_fault_description_init',
                                                            [validators.Regexp(regex=r'^\w{5,20}$')], default='')

    input_variable_user_comment_init = StringField('input_variable_user_comment_init',
                                                   [validators.Regexp(regex=r'^\w{5,20}$')], default='')

    proof_file = FileField('Profile', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'xml', 'txt'], 'Images only!')])

class CheckWindTurbineUT(CamundaTask):
    input_variable_wtg_fault_description_init = StringField('input_variable_wtg_fault_description_init',
                                                            [validators.Regexp(regex=r'^\w{5,20}$')], default='')
    input_variable_user_comment_init = StringField('input_variable_user_comment_init',
                                                   [validators.Regexp(regex=r'^\w{5,20}$')], default='')