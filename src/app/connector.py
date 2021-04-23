from configparser import ConfigParser
import requests
import json
from app.portal_constants import Statuses


class PortalConnector:
    parser = ConfigParser()
    parser.read('app/portal_config.ini')
    camunda_url = parser.get('camunda_server', 'url')
    camunda_port = parser.get('camunda_server', 'port')
    camunda_user_name = ''
    camunda_password = ''


    def authenticate_user(self, flask_form):
        self.camunda_user_name = flask_form['uname']
        self.camunda_password = flask_form['pswd']
        try:
            url = (str(self.camunda_url) + ':' + str(self.camunda_port) +
                   '/engine-rest/task/count?assigned=true')
            assigned_tasks_count_response = requests.get(url,
                                                         auth=(self.camunda_user_name,
                                                               self.camunda_password))
            status_code = assigned_tasks_count_response.status_code
            if status_code != 200:
                return {'status': Statuses.Failed, 'code': status_code}
            else:
                return {'status': Statuses.Success,
                        'response': json.loads(assigned_tasks_count_response.text)}

        except Exception as ex:
            print('Engine is down ' + str(ex))
            return {'status': Statuses.Exception, 'code': '',
                    'message': 'Mainetnace, please try again later'}
                    
    def execute_get_request(self, request_url):
        url = (str(self.camunda_url) + ':' + str(self.camunda_port) + request_url)
        try:           
            get_response = requests.get(url, auth=(self.camunda_user_name, self.camunda_password))
            status_code = get_response.status_code
            if str(status_code).startswith('2'): # success codes starts with 2, e.g. 200, 201
                json_response = json.loads(get_response.text)
                return {'status': Statuses.Success, 'response': json_response}
            else:
                return {'status': Statuses.Failed, 'code': status_code}
        except Exception as ex:
            return {'status': Statuses.Exception, 'code': '', 'message': ex}
