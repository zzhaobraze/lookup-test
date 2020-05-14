# !/usr/bin/env python
# -*- coding: utf-8 -*-
import falcon
import os
import json
import re
import psycopg2
from psycopg2 import sql
import configparser
import datetime

class DBLookup(object):
    reqSettings = [
        "DATABASE_URL",
        "AUTHENTICATION"
    ]
    optSettings = {
        "DB_SCHEMA": "public",
        "DB_TABLE": "lookup",
        "DB_KEY_FIELD": "id",
        "DB_VALUE_FIELD": "value"
    }
    settings = {}

    # Initialized class variables
    def __init__(self):
        # if variable is preset then load from env, else load from .env file
        if "AUTHENTICATION" in os.environ:
            for setting in self.reqSettings:
                if setting in os.environ:
                    self.settings[setting] = os.environ[setting]
            for setting, value in self.optSettings.items():
                if setting in os.environ:
                    self.settings[setting] = os.environ[setting]
                else:
                    self.settings[setting] = value
        else:
            config = configparser.RawConfigParser()
            config.read('./.env')
            if config.has_section('lookup'):
                for setting in self.reqSettings:
                    self.settings[setting] = config.get('lookup', setting)
                for setting, value in self.optSettings.items():
                    if config.has_option('lookup', setting):
                        self.settings[setting] = config.get('lookup', setting)
                    else:
                        self.settings[setting] = value

    # Handle get request for the endpoint only for better cache performance
    def on_get(self, req, res):
        req_header = req.headers
        settings = self.settings
        if ('AUTHORIZATION' not in req_header) or (req_header['AUTHORIZATION'] != settings['AUTHENTICATION']):
            res.body = "401 Unauthorized"
            res.status = falcon.HTTP_401
        else:
            params = {}
            err = False
            lookup_val = ''
            db_limit = 1
            if 'id' not in req.params:
                err = True
            else:
                lookup_val = req.params['id']

            if err:
                res.body = '400 Bad Request'
                res.status = falcon.HTTP_400
            else:
                db_query = sql.SQL("select {field_key},{field_value} from {schema}.{table} where {id} = %s limit {limit}").format(
                    field_key=sql.Identifier(settings['DB_KEY_FIELD']),
                    field_value=sql.Identifier(settings['DB_VALUE_FIELD']),
                    schema=sql.Identifier(settings['DB_SCHEMA']),
                    table=sql.Identifier(settings['DB_TABLE']),
                    id=sql.Identifier(settings['DB_KEY_FIELD']),
                    limit=sql.Literal(db_limit)
                )
                try:
                    db_conn = psycopg2.connect(settings['DATABASE_URL'])
                    db_cursor = db_conn.cursor()
                    db_cursor.execute(db_query, (lookup_val,))
                    results = [dict((db_cursor.description[i][0], value) for i, value in enumerate(row)) for row in db_cursor.fetchall()]
                    result = {}
                    if len(results) >= 1:
                        result = results[0]
                    res_json = json.dumps(result, ensure_ascii=False, default = self.db_converter)
                    res.body = res_json
                    res.status = falcon.HTTP_200
                except Exception as e:
                    print(str(e))
                    res.body = '400 Bad Request'
                    res.status = falcon.HTTP_400

    # Ignore post since caching isn't available
    def on_post(self, req, res):
        res.body = "405 Method Not Allowed"
        res.status = falcon.HTTP_405

    def db_converter(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__str__()

api = falcon.API()
api.add_route('/lookup', DBLookup())
