__author__ = 'Oleg Ladizhensky'

import app.forms.wind_farm_manager as wind_farm_manager


class FormFactory:
    def get_start_form(self, process_key):
        if process_key == 'Utilities_Wind_Farm_Manager':
            return wind_farm_manager.StartProcessForm()
        else:
            raise ValueError(process_key)

    def get_ut_form(self, task_vars, task, process_definition, with_variables=True):
        if process_definition['key'] == 'Utilities_Wind_Farm_Manager':
            form = getattr(wind_farm_manager, task['taskDefinitionKey'])()
            if with_variables:
                for task_var in task_vars:
                    if hasattr(form, task_var):
                        setattr(form, task_var, task_vars[task_var]['value'])
                form.task_id = task['id']
            return form
        else:
            raise ValueError('Unknown type')



factory = FormFactory()
