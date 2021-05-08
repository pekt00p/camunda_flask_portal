from flask import Flask, render_template, request, session
from app.connector import PortalConnector
from app.portal_constants import Statuses
from app.helpers import Translations, Validations
import app.camunda.user_task as ut
import app.camunda.history_service as hs
import json
from os import path
import logging
app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]2/'
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', filename='execution.log', encoding='utf-8', level=logging.DEBUG)
tr = Translations()
vl = Validations()
connector = PortalConnector()
new_start = True
@app.route("/", methods=["POST", "GET"])
def authenticate_user(form=None):

    if 'language' not in session:
        session['language'] = 'en' #default
    if request.method == 'POST':
        print(request.form)
    translations = tr.parse_template('app/templates/login.html', session['language'])
    validations = vl.parse_template('app/templates/login.html')
    if 'is_authenticated' in session and not new_start:
        return if_user_authenticated(connector)
    elif request.form:
        result = connector.authenticate_user(request.form)
        validations = vl.parse_template('app/templates/login.html')
        validation_result = vl.validate_input(validations, request.form)
        if (result['status'] != Statuses.Success.value or not validation_result):
            if result['status'] == Statuses.Exception.value:
                return render_template('login.html',
                                       exception_message=result['message'],
                                       translations=translations,
                                       validations=validations)
            else:
                return render_template('login.html',
                                       exception_message='Authentication \
                                       error, please check login or password',
                                       translations=translations,
                                       validations=validations)
        else:
            session['is_authenticated'] = True
            return if_user_authenticated(connector)
    return render_template('login.html', translations=translations, validations=validations)

@app.route("/change_language/<language>", methods=["POST"])
def change_language(language):
    session['language'] = language
    return authenticate_user()

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('is_authenticated')
    session.pop('language')
    return render_template('login.html', translations='', validations='')    
    
@app.route("/my_tasks_button", methods=["POST"])
def get_my_tasks():
    response = ut.get_all_user_tasks(connector)
    return render_template('my_tasks.html', my_tasks=response['response'], view_type='user')
    
@app.route("/group_tasks_button", methods=["POST"])
def get_group_tasks():
    response = ut.get_group_tasks(connector)
    return render_template('my_tasks.html', my_tasks=response['response'], view_type='group')
    
@app.route("/my_requests_button", methods=["POST"])
def get_my_requests():
    response = hs.get_processes_started_by_user(connector)
    return render_template('my_requests.html', my_requests=response['response'])
    
@app.route("/get_group_task_by_id/<task_id>", methods=["POST"])
def get_group_task_by_id(task_id):    
    return get_task_form(task_id, view_type='group')

@app.route("/get_task_by_id/<task_id>", methods=["POST"])
def get_task_form(task_id, view_type='user'):
    response = ut.get_task_vars_by_id(connector, task_id)
    task = ut.get_user_task_by_id(connector, task_id)
    if task['response']['formKey'] and path.exists('app/templates/' + str(task['response']['formKey'])):    
        return render_template(task['response']['formKey'],
                               variables=response, task_id=task_id, view_type=view_type)
    else: 
         logging.error("Template " + str(task['response']['formKey']) + 
             " not found for process " + str(task['response']['processDefinitionId']))
         return render_template('errors/404_form_not_found.html')
                           
                           
@app.route("/get_process_history_by_id/<process_instance_id>", methods=["POST"])
def get_process_history_by_id(process_instance_id):
    response = hs.get_process_history_by_id(connector, process_instance_id)
    return render_template('process_instance_history.html',
                           variables=response['response'])            
            
@app.route("/complete_task_by_id/<task_id>", methods=["POST"])
def complete_task(task_id):   
    response = ut.complete_task_by_id(connector, task_id, data=request.data)
    return Statuses.Success.value

@app.route("/save_draft/<task_id>", methods=["POST"])
def save_draft(task_id):
    response = ut.update_task_variables_by_id(connector, task_id, data=request.data)

    return Statuses.Success.value
    
@app.route("/unclaim", methods=["POST"])
def unclaim():
    for task_id in json.loads(request.data):
        response = ut.unclaim(connector, task_id[0])
        if (response['status']!=Statuses.Success.value):
            #breaking the loop if at least one fails
            return response['status']
    return Statuses.Success.value
    
@app.route("/claim", methods=["POST"])
def claim():
    for task_id in json.loads(request.data):
        response = ut.claim(connector, task_id[0])
        if (response['status']!=Statuses.Success.value):
            #breaking the loop if at least one fails
            return response['status']
    return Statuses.Success.value


@app.route("/request_processor", methods=['POST'])
def request_processor(form=None):
    print('FORM:')
    print(request.form)
    pass
    
# Sets values for initial page
def if_user_authenticated(connector):
    global new_start
    new_start = False # prevents active session after restart
    user_details = ut.get_user_profile(connector)
    user_task_count = ut.count_all_user_tasks(connector)
    group_task_count = ut.count_all_group_tasks(connector)
    return render_template('main_view.html', 
        user_details=user_details['response'],
        user_task_count=user_task_count['response']['count'],
        group_task_count=group_task_count['response']['count'])

