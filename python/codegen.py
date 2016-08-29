#!/usr/bin/env python
# -*- coding:utf8 -*-

db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
}

db_name = 'test'
import subprocess
import functools
import jinja2
import os
import sys
import contextlib
import shutil
import peewee
import wtforms
import inspect
import pyclbr
import importlib
from playhouse.reflection import Introspector
from peewee import print_, MySQLDatabase, SqliteDatabase, PostgresqlDatabas
from random import randint
from jinja2 import Environment, FileSystemLoader,Template
env = Environment(loader=FileSystemLoader('views'))
from peewee import *
db = MySQLDatabase(db_name, **db_config)

def render_template(tpl_name, *args, **kwagrs):
    """
    Render template helper function
    """
    template = env.get_template(tpl_name)
    return template.render(*args, **kwagrs)

def view(template_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            template = env.get_template(template_name)

            if isinstance(response, dict):
                return template.render(**response)
            else:
                return template.render()
        return wrapper
    return decorator

@contextlib.contextmanager
def to_file(where):
    sys.stdout = open(where, 'a')
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


def get_list_of_files(directory, ext='', full_path=True):
    files = []
    for file_name in os.listdir(directory):
        if file_name.endswith(ext):
            file_path = os.path.join(directory, file_name) if full_path else file_name
            yield file_path


def get_only_files(directory, ext='', full_path=True):
    for file_name in os.listdir(directory):
        path = os.path.join(directory, file_name)
        if not os.path.isdir(path):
            if file_name.endswith(ext):
                yield path if full_path else file_name

fj = os.path.join  # Folder join


