from flask import Flask, render_template, request, session
from app.connector import PortalConnector
from app.portal_constants import Statuses
from app.translator import Translations
import app.camunda.user_task as ut
import app.camunda.history_service as hs
app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]2/'

tr = Translations()
connector = PortalConnector()
new_start = True
@app.route("/", methods=["POST", "GET"])
def authenticate_user(form=None):

    if 'language' not in session:
        session['language'] = 'en' #default
    if request.method == 'POST':
        print(request.form)
    translations = tr.parse_template('app/templates/login.html', session['language'])
    if 'is_authenticated' in session and not new_start:
        return if_user_authenticated(connector)
    elif request.form:
        result = connector.authenticate_user(request.form)
        if result['status'] != Statuses.Success:
            if result['status'] == Statuses.Exception:
                return render_template('login.html',
                                       exception_message=result['message'],
                                       translations=translations)
            else:
                return render_template('login.html',
                                       exception_message='Authentication \
                                       error, please check login or password',
                                       translations=translations)
        else:
            session['is_authenticated'] = True
            return if_user_authenticated(connector)
    return render_template('login.html', translations=translations)

@app.route("/change_language/<language>", methods=["POST"])
def change_language(language):
    session['language'] = language
    return authenticate_user()

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('is_authenticated')
    return render_template('login.html', translations='')    
    
@app.route("/my_tasks_button", methods=["POST"])
def get_my_tasks():
    response = ut.get_all_user_tasks(connector)
    return render_template('my_tasks.html', my_tasks=response['response'])
    
@app.route("/my_requests_button", methods=["POST"])
def get_my_requests():
    response = hs.get_processes_started_by_user(connector)
    return render_template('my_requests.html', my_requests=response['response'])

@app.route("/get_task_by_id/<task_id>", methods=["POST"])
def get_task_form(task_id):
    response = ut.get_task_vars_by_id(connector, task_id)
    return render_template('user_forms/wind_farm_management_process/check_status/check_status_v_1_0.html',
                           variables=response, task_id=task_id)
                           
                           
@app.route("/get_process_history_by_id/<process_instance_id>", methods=["POST"])
def get_process_history_by_id(process_instance_id):
    response = hs.get_process_history_by_id(connector, process_instance_id)
    return render_template('process_instance_history.html',
                           variables=response['response'])            
            
@app.route("/complete_task_by_id/<task_id>", methods=["POST"])
def complete_task(task_id):   
    #response = ut.complete_task_by_id(connector, task_id, data=data)
    print("REQUEST:")
    print(request.data)
    response = ut.get_all_user_tasks(connector)
    return render_template('my_tasks.html', my_tasks=response['response'])

@app.route("/request_processor", methods=['POST'])
def request_processor(form=None):
    pass
    
# Sets values for initial page
def if_user_authenticated(connector):
    print("if_user_authenticated")
    global new_start
    new_start = False # prevents active session after restart
    user_details = ut.get_user_profile(connector)
    user_task_count = ut.count_all_user_tasks(connector)
    group_task_count = ut.count_all_group_tasks(connector)
    return render_template('main_view.html', 
        user_details=user_details['response'],
        user_task_count=user_task_count['response']['count'],
        group_task_count=group_task_count['response']['count'])

