__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector


def get_all_user_tasks(pc:PortalConnector):
    url = '/engine-rest/task?assignee=' + str(pc.camunda_user_name)
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