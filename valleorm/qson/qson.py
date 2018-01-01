# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   25-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 01-Jan-2018
# @License: Apache license vesion 2.0

from kivy.network.urlrequest import UrlRequest
import urllib
import json

class QSonHelper:

    def __init__(self, model):

        self.model = {
            'reg' : model.toDICT(),
            'name' : model.__class__.__name__,
            'childs' : []
        }

    def append_child(self, model, tipo="ForeignKey", relation_field=None):
        if relation_field == None:
            relation_field =  model.__class__.__name__.lower()
        child = {
            "name": model.__class__.__name__,
            "reg": model.toDICT(),
            "tipo": tipo,
            "relation_field": relation_field
        }
        self.model['childs'].append(child)

class QSonQHelper:

    def __init__(self, model, query):

        self.model = {
            'reg' : model.toDICT(),
            'name' : model.__class__.__name__,
            'childs' : []
        }

    def append_child(self, model, tipo="ForeignKey", relation_field=None):
        if relation_field == None:
            relation_field =  model.__class__.__name__.lower()
        child = {
            "name": model.__class__.__name__,
            "reg": model.toDICT(),
            "tipo": tipo,
            "relation_field": relation_field
        }
        self.model['childs'].append(child)


class QSonSender:
    db_name = None
    url = None
    token = None

    def send_add(self, on_success, wait=False, qsonhelper=()):
        qson_add = {"add": {"db": self.db_name,
                            "rows": []}}

        for m in qsonhelper:
            qson_add["add"]["rows"].append(m.model)

        SEND_DATA = {'data':json.dumps(qson_add)}

        data = urllib.urlencode(SEND_DATA)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/json'}
        r = UrlRequest(self.url, on_success=on_success, req_body=data,
                       req_headers=headers, method="POST")
        if wait:
            r.wait()

    def send_get(self, on_success, wait=False, qsonhelper=()):
        qson_add = {"get": {"db": self.db_name,
                            "rows": []}}

        for m in qsonhelper:
            qson_add["send"]["rows"].append(m.model)

        SEND_DATA = {'data':json.dumps(qson_add)}

        data = urllib.urlencode(SEND_DATA)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/json'}
        r = UrlRequest(self.url, on_success=on_success, req_body=data,
                       req_headers=headers, method="POST")
        if wait:
            r.wait()
