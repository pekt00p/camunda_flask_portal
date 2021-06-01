__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector
import datetime


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


def get_variable_instance_by_proc_inst_id_and_name(pc: PortalConnector, proc_inst_id, var_name=None, session=None):
    if var_name:
        url = '/engine-rest/variable-instance?processInstanceIdIn=' \
              + str(proc_inst_id) + '&variableName=' + str(var_name)
    else:  # When var_name is not specified return all variable instances
        url = '/engine-rest/variable-instance?processInstanceIdIn=' + str(proc_inst_id)
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_variable_instance_binary_data(pc: PortalConnector, variable_instance_id, session=None):
    url = '/engine-rest/variable-instance/' + str(variable_instance_id) + '/data'
    json_response = pc.execute_request(url, session=session, binary_data=True)
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
    # make data transformation for Camunda
    process_variables = {}
    for item in data:
        if item != "csrf_token":
            process_variables[item] = {"value": data[item], "type": "String"}
    all_vars = {"variables": process_variables}
    json_response = pc.execute_request(url, request_type='POST', session=session, data=all_vars)
    return json_response


def update_task_variables_by_id(pc: PortalConnector, task_id, data=None, session=None):
    url = '/engine-rest/task/' + str(task_id) + '/variables'
    # make data transformation for Camunda
    modifications = {}
    for item in data:
        if item != "csrf_token":
            modifications[item] = {"value": data[item], "type": "String"}
    all_mods = {"modifications": modifications}
    json_response = pc.execute_request(url, request_type='POST', data=all_mods, session=session)
    return json_response
