__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector
import datetime


def get_processes_started_by_user(pc: PortalConnector, session=None):
    url = '/engine-rest/history/process-instance?startedBy=' + str(session['username'])
    json_response = pc.execute_request(url, session=session)
    for record in json_response['response']:
        if record['startTime']:
            record['startTime'] = datetime.datetime.strptime(record['startTime'][:-9], '%Y-%m-%dT%H:%M:%S')
        if record['endTime']:
            record['endTime'] = datetime.datetime.strptime(record['endTime'][:-9], '%Y-%m-%dT%H:%M:%S')
    return json_response


def get_process_history_by_id(pc: PortalConnector, session=None, execution_id=None):
    url = '/engine-rest/history/activity-instance?executionId=' + str(execution_id) \
          + '&activityType=intermediateNoneThrowEvent'
    json_response = pc.execute_request(url, session=session)
    for record in json_response['response']:
        if record['endTime']:
            record['endTime'] = datetime.datetime.strptime(record['endTime'][:-9], '%Y-%m-%dT%H:%M:%S')
    return json_response
