__author__ = 'Oleg Ladizhensky'

import app.forms.wind_farm_manager as wind_farm_manager


class FormFactory:
    def get_start_form(self, process_key):
        if process_key == 'Utilities_Wind_Farm_Manager':
            return wind_farm_manager.StartProcessForm()
        else:
            raise ValueError(process_key)


factory = FormFactory()
