__author__ = 'Oleg Ladizhensky'

import base64

from app.connector import PortalConnector
import json


def get_user_allowed_processes(pc: PortalConnector, session=None):
    url = '/engine-rest/process-definition?latestVersion=true&startableBy=' + str(session['username'])
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_user_allowed_process_by_key(pc: PortalConnector, session=None, process_key=None):
    url = '/engine-rest/process-definition?latestVersion=true&startableBy=' + str(session['username']) + '&key=' + str(
        process_key)
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_process_start_form(pc: PortalConnector, session=None, process_key=None):
    url = '/engine-rest/process-definition/key/' + str(process_key) + '/startForm'
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_process_definition(pc: PortalConnector, session=None, process_key=None):
    url = '/engine-rest/process-definition/key/' + str(process_key)
    json_response = pc.execute_request(url, session=session)
    return json_response


def get_process_definition_by_id(pc: PortalConnector, session=None, process_def_if=None):
    url = '/engine-rest/process-definition/' + str(process_def_if)
    json_response = pc.execute_request(url, session=session)
    return json_response


def submit_new_process(pc: PortalConnector, session=None, process_key=None, data=None):
    url = '/engine-rest/process-definition/key/' + str(process_key) + '/start'
    # make data transformation for Camunda
    process_variables = {}
    for item in data:
        if item.type == 'StringField':
            process_variables[item.name] = {"value": item.data, "type": "String"}
        if item.type == 'FileField':
            process_variables[item.name] = {"value": base64.b64encode(item.data.stream.read()).decode('ascii'),
                                            "type": "File", "valueInfo":
                                                {"filename": item.data.filename, "mimetype": item.data.mimetype,
                                                 "encoding": "UTF-8"}}

    # process_variables = {}
    # for modification in data['modifications']:
    #    process_variables[modification["variable_id"]] = {"value": modification['value'], "type": modification['type']}
    all_vars = {"variables": process_variables}
    json_response = pc.execute_request(url, request_type='POST', session=session, data=all_vars)
    return json_response
