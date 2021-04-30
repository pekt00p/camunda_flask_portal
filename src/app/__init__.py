from flask import Flask, render_template, request, session
from app.connector import PortalConnector
from app.portal_constants import Statuses
import app.camunda.user_task as ut
app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]2/'

connector = PortalConnector()

@app.route("/", methods=['GET', 'POST'])
def authenticate_user(form=None):
    print(session)
    if 'is_authenticated' in session:
        return render_template('main_view.html',
                                       task_count=10)
    elif request.form:
        result = connector.authenticate_user(request.form)
        if result['status'] != Statuses.Success:
            if result['status'] == Statuses.Exception:
                return render_template('login.html',
                                       exception_message=result['message'])
            else:
                return render_template('login.html',
                                       exception_message='Authentication \
                                       error, please check login or password')
        else:
            session['is_authenticated'] = True
            return render_template('main_view.html',
                                       task_count=result['response']['count'])
    return render_template('login.html')


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('is_authenticated')
    return render_template('login.html')    
    
@app.route("/my_tasks_button", methods=["POST"])
def get_my_tasks():
    response = ut.get_all_user_tasks(connector)
    return render_template('my_tasks.html', my_tasks=response['response'])

@app.route("/get_task_by_id/<task_id>", methods=["POST"])
def get_task_form(task_id):
    response = ut.get_task_vars_by_id(connector, task_id)
    return render_template('user_forms/wind_farm_management_process/check_status/check_status_v_1_0.html',
                           variables=response, task_id=task_id)
                           
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
