from flask import Flask, render_template, request
from app import authenticator
from app.portal_constants import Statuses
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def authenticate_user(form=None):

    if request.form:
        result = authenticator.authenticate_user(request.form)
        if result['status'] != Statuses.Success:
            if result['status'] == Statuses.Exception:
                return render_template('login.html',
                                       exception_message=result['message'])
            else:
                return render_template('login.html',
                                       exception_message='Authentication \
                                       error, please check login or password')
        else:
            return render_template('main_view.html',
                                   task_count=result['response']['count'])
    return render_template('login.html')


@app.route("/request_processor", methods=['POST'])
def request_processor(form=None):
    pass
