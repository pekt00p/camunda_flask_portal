__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector
import datetime
import json


def get_all_user_tasks(pc: PortalConnector, session=None):
    url = '/engine-rest/task?assignee=' + str(session['username'])
    json_response = pc.execute_request(url, session=session)
    for record in json_response['response']:
        if record['created']:
            record['created'] = datetime.datetime.strptime(record['created'][:-9], '%Y-%m-%dT%H:%M:%S')
        if record['due']:
            record['due'] = datetime.datetime.strptime(record['due'][:-9], '%Y-%m-%dT%H:%M:%S')
    return json_response


def get_user_profile(pc: PortalConnector, session=None):
    url = '/engine-rest/user/' + str(session['username']) + '/profile'
    json_response = pc.execute_request(url, session=session)
    return json_response


def count_all_user_tasks(pc: PortalConnector, session=None):
    url = '/engine-rest/task/count?assignee=' + str(session['username'])
    json_response = pc.execute_request(url, session=session)
    return json_response


def count_all_group_tasks(pc: PortalConnector, session=None):
    url = '/engine-rest/task/count?withCandidateGroups=true'
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_group_tasks(pc: PortalConnector, session=None):
    url = '/engine-rest/task?withCandidateGroups=true'
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_user_task_by_id(pc: PortalConnector, task_id, session=None):
    url = '/engine-rest/task/' + str(task_id)
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_task_vars_by_id(pc: PortalConnector, task_id, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/variables'
    json_response = pc.execute_request(url, session=session)
    return json_response


def unclaim(pc: PortalConnector, task_id, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/unclaim'
    json_response = pc.execute_request(url, request_type='POST', data={}, session=session)
    return json_response


def claim(pc: PortalConnector, task_id, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/claim'
    data = {"userId": str(session['username'])}
    json_response = pc.execute_request(url, request_type='POST', data=data, session=session)
    return json_response


def complete_task_by_id(pc: PortalConnector, task_id, data=None, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/complete'
    data = json.loads(data.decode("utf-8"))
    json_response = pc.execute_request(url, request_type='POST', data=data, session=session)
    print("COMPLETE:" + str(json_response))
    return json_response


def update_task_variables_by_id(pc: PortalConnector, task_id, data=None, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/variables'
    # make data transformation for Camunda
    data = json.loads(data.decode("utf-8"))
    modifications = {}
    for modification in data['modifications']:
        modifications[modification["variable_id"]] = {"value": modification['value'], "type": modification['type']}
    all_mods = {"modifications": modifications}
    json_response = pc.execute_request(url, request_type='POST', data=all_mods, session=session)
    return json_response
