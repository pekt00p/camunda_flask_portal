from flask import Flask, render_template, request, session, flash
from app.connector import PortalConnector
from app.portal_constants import Statuses
from app.helpers import Translations, Validations
import app.camunda.user_task as ut
import app.camunda.history_service as hs
import app.camunda.process_service as ps
import json
from os import path
import logging
import app.forms.common_form_factory as cff

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'your_secret_key_here'
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', filename='execution.log',
                    encoding='utf-8', level=logging.DEBUG)
tr = Translations()
vl = Validations()
connector = PortalConnector()


@app.route("/", methods=["POST", "GET"])
def authenticate_user():
    try:
        if 'language' not in session:
            session['language'] = 'en'  # default
        translations = tr.parse_template('app/templates/login.html', session['language'])
        validations = vl.parse_template('app/templates/login.html')
        if 'username' in session:
            return if_user_authenticated(connector)
        elif request.form:
            result = connector.authenticate_user(request.form)
            validations = vl.parse_template('app/templates/login.html')
            validation_result = vl.validate_input(validations, request.form)
            if result['status'] != Statuses.Success.value or not validation_result:
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
                session['username'] = request.form['uname']
                session['password'] = request.form['pswd']
                return if_user_authenticated(connector)
        return render_template('login.html', translations=translations, validations=validations)
    except Exception as ex:
        logging.error("Error during authentication" + str(ex))
        return render_template('/errors/server_not_found.html')  # assume server not responding


@app.route("/change_language/<language>", methods=["POST"])
def change_language(language):
    session['language'] = language
    return authenticate_user()


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('language')
    session.pop('username')
    session.pop('password')
    return authenticate_user()


@app.route("/my_tasks_button", methods=["POST"])
def get_my_tasks():
    response = ut.get_all_user_tasks(connector, session=session)
    return render_template('my_tasks.html', my_tasks=response['response'], view_type='user')


@app.route("/group_tasks_button", methods=["POST"])
def get_group_tasks():
    response = ut.get_group_tasks(connector, session=session)
    return render_template('my_tasks.html', my_tasks=response['response'], view_type='group')


@app.route("/my_requests_button", methods=["POST"])
def get_my_requests():
    response = hs.get_processes_started_by_user(connector, session=session)
    return render_template('my_requests.html', my_requests=response['response'])


@app.route("/get_group_task_by_id/<task_id>", methods=["POST"])
def get_group_task_by_id(task_id):
    return get_task_form(task_id, view_type='group')


@app.route("/get_task_by_id/<task_id>", methods=["POST"])
def get_task_form(task_id, view_type='user'):

    task_vars = ut.get_task_vars_by_id(connector, session=session, task_id=task_id)
    task = ut.get_user_task_by_id(connector, session=session, task_id=task_id)
    variable_instances = ut.get_variable_instance_by_proc_inst_id_and_name(connector, session=session, proc_inst_id=task['response']['processInstanceId'])
    process_definition = ps.get_process_definition_by_id(connector, session=session,
                                                         process_def_if=task['response']['processDefinitionId'])
    try:
        form = cff.factory.get_ut_form(connector, session=session,
                                       task_vars=variable_instances['response'],
                                       task=task['response'],
                                       process_definition=process_definition['response'])
    except Exception as ex:
        logging.error("Error during for determination" + str(ex))
        return render_template('errors/404_form_not_found.html')
    if task['response']['formKey'] and path.exists('app/templates/' + str(task['response']['formKey'])):
        return render_template(task['response']['formKey'], form=form, view_type=view_type)
    else:
        logging.error("Template " + str(task['response']['formKey']) +
                      " not found for process " + str(task['response']['processDefinitionId']))
        return render_template('errors/404_form_not_found.html')


@app.route("/get_process_history_by_id/<process_instance_id>", methods=["POST"])
def get_process_history_by_id(process_instance_id):
    response = hs.get_process_history_by_id(connector, session=session, execution_id=process_instance_id)
    assert response['status'] == Statuses.Success.value, response['status']
    return render_template('process_instance_history.html', variables=response['response'])


@app.route("/complete_task/<task_id>", methods=["POST"])
def complete_task(task_id):
    if 'submit_unclaim_task' in request.form:
        response = ut.unclaim(connector, task_id=task_id, session=session)
        if response['status'] != Statuses.Success.value:
            # breaking the loop if at least one fails
            return response['status']
        return Statuses.Success.value
    elif 'submit_claim_task' in request.form:
        response = ut.claim(connector, task_id=task_id, session=session)
        if response['status'] != Statuses.Success.value:
            # breaking the loop if at least one fails
            return response['status']
        return Statuses.Success.value

    elif 'complete_unclaim_task' in request.form:
        task_vars = ut.get_task_vars_by_id(connector, session=session, task_id=task_id)
        task = ut.get_user_task_by_id(connector, session=session, task_id=task_id)
        process_definition = ps.get_process_definition_by_id(connector, session=session,
                                                             process_def_if=task['response']['processDefinitionId'])
        form = cff.factory.get_ut_form(task_vars=task_vars['response'], task=task['response'],
                                       process_definition=process_definition['response'], with_variables=False)
        print(request.form)
        if form.validate():
            response = ut.complete_task_by_id(connector, session=session, task_id=task_id, data=task_vars)

            if response['status'] == Statuses.Success.value:
                return render_template('user_forms/uf_submitted_success.html', response=response['response'])
            return Statuses.Failed.value
        else:
            # Internal validation failed, returning to form
            flash('Input validation error')
            return Statuses.Failed.value

    elif 'submit_save_as_draft' in request.form:
        response = ut.update_task_variables_by_id(connector, session=session, task_id=task_id, data=request.form)
        assert response['status'] == Statuses.Success.value, response['status']
        return Statuses.Success.value
    else:
        return Statuses.Failed.value


@app.route("/submit_process/<process_key>", methods=["POST"])
def submit_process(form=None, process_key=None):
    # Submitting only latest version of the process.
    if form is None:
        form = cff.factory.get_start_form(process_key)
        process_start_form_name = ps.get_process_start_form(connector, session=session,
                                                            process_key=process_key)['response']['key']
    process_definition = ps.get_process_definition(connector, session=session, process_key=process_key)
    form.process_key = process_key
    form.process_name = process_definition['response']['name']
    form.process_description = process_definition['response']['description']
    if form.validate():
        response = ps.submit_new_process(connector, session=session, process_key=process_key, data=form)
        if response['status'] == Statuses.Success.value:
            return render_template('new_process_success.html', response=response['response'])
        return Statuses.Failed.value

    else:
        # Internal validation failed, returning to form
        flash('Input validation error')
        return render_template(process_start_form_name, form=form)


@app.route("/save_draft/<task_id>", methods=["POST"])
def save_draft(task_id):
    # For draft it is allowed to skip validation on required fields.
    response = ut.update_task_variables_by_id(connector, session=session, task_id=task_id, data=request.data)
    assert response['status'] == Statuses.Success.value, response['status']
    return Statuses.Success.value


@app.route("/unclaim", methods=["POST"])
def unclaim():
    for task_id in json.loads(request.data):
        response = ut.unclaim(connector, task_id=task_id[0], session=session)
        if response['status'] != Statuses.Success.value:
            # breaking the loop if at least one fails
            return response['status']
    return Statuses.Success.value


@app.route("/claim", methods=["POST"])
def claim():
    for task_id in json.loads(request.data):
        response = ut.claim(connector, task_id=task_id[0], session=session)
        if response['status'] != Statuses.Success.value:
            # breaking the loop if at least one fails
            return response['status']
    return Statuses.Success.value


@app.route("/create_request_button", methods=["POST"])
def get_user_allowed_processes():
    response = ps.get_user_allowed_processes(connector, session=session)
    return render_template('user_processes.html', processes=response['response'])


@app.route("/get_process_description/<process_key>", methods=["POST"])
def get_process_description(process_key):
    response = ps.get_user_allowed_process_by_key(connector, session=session, process_key=process_key)
    return render_template('process_description.html', process=response['response'])


@app.route("/start_new_process_instance/<process_key>", methods=["POST"])
def start_new_process_instance(process_key, form=None):
    # Opens the form of new process.
    if form is None:
        form = cff.factory.get_start_form(process_key)

    process_start_form_name = \
        ps.get_process_start_form(connector, session=session, process_key=process_key)['response']['key']
    process_definition = ps.get_process_definition(connector, session=session, process_key=process_key)
    form.process_key = process_key
    form.process_name = process_definition['response']['name']
    form.process_description = process_definition['response']['description']
    return render_template(process_start_form_name, form=form, process=process_definition['response'])


@app.route("/request_processor", methods=['POST'])
def request_processor():
    pass


# Sets values for initial page
def if_user_authenticated(connector=None):
    user_details = ut.get_user_profile(connector, session)
    print(user_details)
    user_task_count = ut.count_all_user_tasks(connector, session)
    group_task_count = ut.count_all_group_tasks(connector, session)
    return render_template('main_view.html',
                           user_details=user_details['response'],
                           user_task_count=user_task_count['response']['count'],
                           group_task_count=group_task_count['response']['count'])
