__author__ = 'Oleg Ladizhensky'

import app.forms.wind_farm_manager as wind_farm_manager
import app.camunda.user_task as ut


class FormFactory:
    def get_start_form(self, process_key):
        if process_key == 'Utilities_Wind_Farm_Manager':
            return wind_farm_manager.StartProcessForm()
        else:
            raise ValueError(process_key)

    def get_ut_form(self, pc, session=None, task_vars=None, task=None, process_definition=None, with_variables=True):
        if process_definition['key'] == 'Utilities_Wind_Farm_Manager':
            form = getattr(wind_farm_manager, task['taskDefinitionKey'])()
            if with_variables:
                for task_var in task_vars:
                    if hasattr(form, task_var['name']):
                        if task_var['type'] == 'String':
                            setattr(form, task_var['name'], task_var['value'])
                        elif task_var['type'] == 'File':
                            payload = ut.get_variable_instance_binary_data(pc, session=session,
                                                                           variable_instance_id=task_var['id'])
                            setattr(form, task_var['name'], payload)
                form.task_id = task['id']
            return form
        else:
            raise ValueError('Unknown type')


factory = FormFactory()
