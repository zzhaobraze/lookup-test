# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import re
import psycopg2
from psycopg2 import sql
import configparser

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

if "AUTHENTICATION" in os.environ:
    for setting in reqSettings:
        if setting in os.environ:
            settings[setting] = os.environ[setting]
    for setting, value in optSettings.items():
        if setting in os.environ:
            settings[setting] = os.environ[setting]
        else:
            settings[setting] = value
else:
    config = configparser.RawConfigParser()
    config.read('./.env')
    if config.has_section('lookup'):
        for setting in reqSettings:
            settings[setting] = config.get('lookup', setting)
        for setting, value in optSettings.items():
            if config.has_option('lookup', setting):
                settings[setting] = config.get('lookup', setting)
            else:
                settings[setting] = value

db_create = sql.SQL("""
    CREATE TABLE {schema}.{table} (
        {field_key} VARCHAR(200) PRIMARY KEY,
        {field_value} VARCHAR
    )
    """).format(
    field_key=sql.Identifier(settings['DB_KEY_FIELD']),
    field_value=sql.Identifier(settings['DB_VALUE_FIELD']),
    schema=sql.Identifier(settings['DB_SCHEMA']),
    table=sql.Identifier(settings['DB_TABLE'])
)
try:
    db_conn = psycopg2.connect(settings['DATABASE_URL'])
    db_cursor = db_conn.cursor()
    db_cursor.execute(db_create)
    db_conn.commit()

    db_index = sql.SQL("""
            CREATE UNIQUE INDEX bz_lookup_index
            ON {schema}.{table} ({field_key});
        """).format(
        field_key=sql.Identifier(settings['DB_KEY_FIELD']),
        schema=sql.Identifier(settings['DB_SCHEMA']),
        table=sql.Identifier(settings['DB_TABLE'])
    )

    db_cursor.execute(db_index)
    db_conn.commit()

    print("Table %s.%s successfully created." % (settings['DB_SCHEMA'], settings['DB_TABLE']))
except Exception as e:
    print(str(e))
finally:
    if (db_conn):
        db_cursor.close()
        db_conn.close()
