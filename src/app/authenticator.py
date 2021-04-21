from configparser import ConfigParser
import requests
import json
from app.portal_constants import Statuses

parser = ConfigParser()
parser.read('app/camunda_config.ini')
camunda_url = parser.get('camunda_server', 'url')
camunda_port = parser.get('camunda_server', 'port')


def authenticate_user(flask_form):
    camunda_user_name = flask_form['uname']
    camunda_password = flask_form['pswd']
    try:
        url = (str(camunda_url) + ':' + str(camunda_port) +
               '/engine-rest/task/count?assigned=true')
        assigned_tasks_count_response = requests.get(url,
                                                     auth=(camunda_user_name,
                                                           camunda_password))
        status_code = assigned_tasks_count_response.status_code
        if status_code != 200:
            return {'status': Statuses.Failed, 'code': status_code}
        else:
            return {'status': Statuses.Success,
                    'response': json.loads(assigned_tasks_count_response.text)}

    except Exception as ex:
        print('Engine is down')
        print(ex)
        return {'status': Statuses.Exception, 'code': '',
                'message': 'Mainetnace, please try again later'}
