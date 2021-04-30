from configparser import ConfigParser
import requests
import json
from app.portal_constants import Statuses


class PortalConnector:
    parser = ConfigParser()
    parser.read('app/portal_config.ini')
    camunda_url = parser.get('camunda_server', 'url')
    camunda_port = parser.get('camunda_server', 'port')
    portal_name = parser.get('portal_representation', 'name')
    portal_date_format = parser.get('portal_representation', 'date_format')
    camunda_user_name = ''
    camunda_password = ''


    def authenticate_user(self, flask_form):
        self.camunda_user_name = flask_form['uname']
        self.camunda_password = flask_form['pswd']
        
        try:
            url = (str(self.camunda_url) + ':' + str(self.camunda_port) +
                   '/engine-rest/user/' + self.camunda_user_name + '/profile')
            user_profile = requests.get(url, auth=(self.camunda_user_name,
                                                   self.camunda_password))
            status_code = user_profile.status_code
            if status_code != 200:
                return {'status': Statuses.Failed, 'code': status_code}
            else:
                return {'status': Statuses.Success,
                        'response': json.loads(user_profile.text)}

        except Exception as ex:
            print('Engine is down ' + str(ex))
            return {'status': Statuses.Exception, 'code': '',
                    'message': 'Mainetnace, please try again later'}
                    
    def execute_request(self, request_url, type='GET', data=None):
        url = (str(self.camunda_url) + ':' + str(self.camunda_port) + request_url)
        try:
            if type == 'GET':        
                requests_response = requests.get(url, auth=(self.camunda_user_name, self.camunda_password))
            elif type == 'POST':
 
                data = json.loads(data)
                requests_response = requests.post(url, auth=(self.camunda_user_name, self.camunda_password), json=data)
                
            status_code = requests_response.status_code
            if str(status_code).startswith('2'): # success codes starts with 2, e.g. 200, 201
                json_response = json.loads(requests_response.text)
                return {'status': Statuses.Success, 'response': json_response}
            else:
                return {'status': Statuses.Failed, 'code': status_code}
        except Exception as ex:
            return {'status': Statuses.Exception, 'code': '', 'message': ex}
