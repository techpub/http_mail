__author__ = 'herbertqiao'

import falcon
import utils
import re
from error import RError
from database import RDataBase


class RUser:
    def __init__(self):
        self.db = RDataBase()


    @utils.require_login
    @utils.require_domain_owner
    def on_get(self, req, resp, domain_id, user):
        req.context['result'] = {
            'result': self.db.query('SELECT id, domain_id, email FROM virtual_users WHERE domain_id = %s',
                                    (domain_id, ))}
        resp.status = falcon.HTTP_200

    @utils.require_login
    @utils.require_domain_owner
    def on_post(self, req, resp, domain_id, user):
        if 'request' not in req.context.keys():
            raise RError(16)
        request = req.context['request']
        if 'username' not in request.keys():
            raise RError(20)
        if not re.match('^[a-z0-9A-Z][a-z0-9A-Z_\+\.]{0,60}$', request['username']):
            raise RError(13)
        if 'password' not in request.keys():
            raise RError(14)
        domain = self.db.query('SELECT name FROM virtual_domains WHERE id = %s', (domain_id,))
        if self.db.query('SELECT * FROM virtual_users WHERE email = %s',
                         ((request['username'] + "@" + domain[0]['name']),)):
            raise RError(17)
        self.db.execute(
            "INSERT INTO virtual_users (domain_id,password, email) VALUES "
            "(%s, ENCRYPT(%s, CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), %s)",
            (domain_id, request['password'], (request['username'] + "@" + domain[0]['name'])))
        resp.status = falcon.HTTP_200


class RUserModify:
    def __init__(self):
        self.db = RDataBase()


    @utils.require_login
    @utils.require_domain_owner
    def on_get(self, req, resp, domain_id, user_id, user):
        result = self.db.query(
            'SELECT id, domain_id, email FROM virtual_users WHERE id = %s AND domain_id = %s', (user_id, domain_id))
        if not result:
            raise RError(26)
        req.context['result'] = {'result': result[0]}


    @utils.require_login
    @utils.require_domain_owner
    def on_put(self, req, resp, domain_id, user_id, user):
        if 'request' not in req.context.keys():
            raise RError(16)
        request = req.context['request']
        if not user_id:
            raise RError(15)
        if 'password' not in request.keys():
            raise RError(14)
        if not self.db.execute(
            "UPDATE virtual_users SET password = ENCRYPT(%s, CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))) "
            "WHERE  domain_id = %s AND id = %s",
            (request['password'], domain_id, user_id)):
            raise RError(18)
        resp.status = falcon.HTTP_200


    @utils.require_login
    @utils.require_domain_owner
    def on_delete(self, req, resp, domain_id, user_id, user):
        if not user_id:
            raise RError(15)
        if not self.db.execute("DELETE FROM virtual_users WHERE id = %s AND domain_id = %s", (user_id, domain_id)):
            raise RError(26)
        resp.status = falcon.HTTP_200

