__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector
import datetime


def get_all_user_tasks(pc:PortalConnector):
    url = '/engine-rest/task?assignee=' + str(pc.camunda_user_name)
    json_response = pc.execute_request(url)
    for record in json_response['response']:
        if record['created']:
            record['created'] = datetime.datetime.strptime(record['created'][:-9], '%Y-%m-%dT%H:%M:%S')
        if record['due']:
            record['due'] = datetime.datetime.strptime(record['due'][:-9], '%Y-%m-%dT%H:%M:%S')
    return json_response
    

def get_user_profile(pc:PortalConnector):
    url = '/engine-rest/user/' + str(pc.camunda_user_name) + '/profile'
    json_response = pc.execute_request(url)
    return json_response

def count_all_user_tasks(pc:PortalConnector):
    url = '/engine-rest/task/count?assigned=true'
    json_response = pc.execute_request(url)
    return json_response
    
def count_all_group_tasks(pc:PortalConnector):
    url = '/engine-rest/task/count?withCandidateGroups=true'
    json_response = pc.execute_request(url)
    return json_response
    
def get_all_user_group_tasks(pc:PortalConnector):
    url = '/engine-rest/task?withCandidateGroups=true'
    json_response = pc.execute_request(url)
    return json_response

def get_user_task_by_id(pc:PortalConnector, task_id):
    url = '/engine-rest/task/' + str(task_id)
    json_response = pc.execute_request(url)
    return json_response

def get_task_vars_by_id(pc:PortalConnector, task_id):
    url = '/engine-rest/task/' + str(task_id) + '/variables'
    json_response = pc.execute_request(url)
    return json_response
    
def complete_task_by_id(pc:PortalConnector, task_id, data=None):
    url = '/engine-rest/task/' + str(task_id) + '/complete'
    json_response = pc.execute_request(url, type='POST', data=data)
    print(json_response)
    return json_response


def update_task_variables_by_id(pc:PortalConnector, task_id, data=None):
    url = '/engine-rest/task/' + str(task_id) + '/variables'
    json_response = pc.execute_request(url, type='POST', data=data)
    print(json_response)
    return json_response