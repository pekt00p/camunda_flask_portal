__author__ = 'Oleg Ladizhensky'

from app.connector import PortalConnector


def get_member_groups(pc: PortalConnector, session=None):
    url = '/engine-rest/group?member=' + str(session['username'])
    json_response = pc.execute_request(url, session=session)
    return json_response
