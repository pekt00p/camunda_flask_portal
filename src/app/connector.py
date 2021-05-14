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

    def authenticate_user(self, flask_form):
        camunda_user_name = flask_form['uname']
        camunda_password = flask_form['pswd']

        try:
            url = (str(self.camunda_url) + ':' + str(self.camunda_port) +
                   '/engine-rest/user/' + camunda_user_name + '/profile')
            user_profile = requests.get(url, auth=(camunda_user_name,
                                                   camunda_password))
            status_code = user_profile.status_code
            if status_code != 200:
                return {'status': Statuses.Failed.value, 'code': status_code}
            else:
                return {'status': Statuses.Success.value,
                        'response': json.loads(user_profile.text)}

        except Exception as ex:
            print('Engine is down ' + str(ex))
            return {'status': Statuses.Exception.value, 'code': '',
                    'message': 'Mainetnace, please try again later'}

    def execute_request(self, request_url, request_type='GET', data=None, session=None):
        url = (str(self.camunda_url) + ':' + str(self.camunda_port) + request_url)
        try:
            if request_type == 'GET':
                requests_response = requests.get(url, auth=(session['username'], session['password']))
            elif request_type == 'POST':
                data = json.dumps(data)
                headers = {'Content-type': 'application/json'}
                requests_response = requests.post(url, auth=(session['username'], session['password']), headers=headers,
                                                  data=data)
            status_code = requests_response.status_code
            if str(status_code).startswith('2'):  # success codes starts with 2, e.g. 200, 201
                json_response = {}
                if requests_response.text:
                    json_response = json.loads(requests_response.text)
                return {'status': Statuses.Success.value, 'response': json_response}
            else:
                return {'status': Statuses.Failed.value, 'code': status_code}
        except Exception as ex:
            return {'status': Statuses.Exception.value, 'code': '', 'message': ex}
