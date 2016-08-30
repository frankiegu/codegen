#!/usr/bin/env python
# -*- coding:utf8 -*-

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'port': 3306,
}

db_name = 'cmdb'

output_dir = './output'

import subprocess
from subprocess import Popen, PIPE
import functools
import os
import json
import itertools
import shutil
import peewee
import wtforms
from wtforms.fields.core import *
from wtforms.fields.simple import *
from wtforms.fields.html5 import *
import inspect
import pyclbr
import importlib
import MySQLdb
from playhouse.reflection import Introspector
from peewee import *
from jinja2 import Environment, FileSystemLoader, Template
import jinja2

env = Environment(loader=FileSystemLoader('views'))
db = MySQLDatabase(db_name, **db_config)
conn = MySQLdb.connect(host=db_config.get('host'),user=db_config.get('user'),passwd=db_config.get('password'),db=db_name)
cursor = conn.cursor()
'''
 'FieldList','FormField',  'RadioField', 'SelectField','SelectMultipleField', 'URLField', 'PasswordField', 'FileField', 'MultipleFileField','HiddenField', 'SubmitField',
'DateTimeLocalField','DecimalRangeField', 'EmailField',  'IntegerRangeField','SearchField', 'TelField'
'''
field_type_to_wtforms = {
    'char': StringField,
    'varchar':StringField,
    'longtext':TextAreaField,
    'mediumtext':TextAreaField,
    'text':TextAreaField,
    'tinytext':TextAreaField,
    'tinyblob':TextAreaField,
    'blob':TextAreaField,
    'longblob':TextAreaField,
    'varbinary':TextAreaField,
    'binary':TextAreaField,

    'int': IntegerField,
    'tinyint':IntegerField,
    'smallint':IntegerField,
    'mediumint':IntegerField,
    'bigint':IntegerField,
    'numeric':IntegerField,
    'decimal':DecimalField,
    'double':FloatField,
    'float':FloatField,

    'bool': BooleanField,
    'boolean': BooleanField,

    'enum':SelectField,
    'set':SelectMultipleField,

    'datetime': DateTimeField,
    'date': DateField,
    'timestamp': DateTimeField,
    'time': DateTimeField,
}

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

def compile_module(module_file,**kwargs):
    with open(module_file, 'r') as fin:
        template = fin.read()

    with open(module_file, 'w') as fout:
        jinja_template = Template(template)
        result = jinja_template.render(kwargs)
        fout.write(result)


fj = os.path.join  # Folder join


def exec_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr = p.communicate()
    finally:
        subprocess._cleanup()
        p.stdout.close()
        p.stderr.close()
    rc = p.returncode
    return rc, stdout, stderr

class Generator:
    def __init__(self,db):
        self.db = db
        self.table_data = self.gen_tables()
        self.form_header = '''
# -*- coding: utf-8 -*-
import wtforms
from wtforms.fields.core import *
from wtforms.fields.simple import *
from wtforms.fields.html5 import *
from wtforms import Form, validators
from peewee_validates import ModelValidator
from peewee_validates import Validator, Field
class {{ class_name }}Validator(Validator):
    {% for field in class_fields %}
    {{ field.name }} = Field(required=True)
    {% endfor %}

        '''
        self.form_template = """
class {{ class_name }}(Form):
    {% for field in class_fields %}
    {{ field.name }} = {{ field.type_}}(validators=[validators.InputRequired()])
    {% endfor %}"""
        self.controller_template = """
from models.{{ db_name }} import *
from helpers.logger import *
from helpers.cache import *

class {{ table_name }}:
    def __init__(self):
        pass

    def create_{{ table_name }}(self,req,resp):
        template = env.get_template('templates/{{ table_name }}/form.html')
        form = {{ model_name }}Form(req._params)
        items = {{ model_name }}.select()
        if request.method == 'POST':
            if form.validate():
                new_item = {{ model_name }}.create(**form.data)
                form = {{ model_name }}Form()
        return template.render(items=items, form=form)

    def info_{{ table_name }}(self,req,resp):
        item = {{ model_name }}.get({{ model_name}}.id == {{ table_name }}_id)
        return render_template('templates/{{ table_name }}/view.html', item=item)

    def edit_{{ table_name }}(self,req,resp):
        item = {{ model_name }}.get({{ model_name }}.id == {{ table_name }}_id)

        form = {{ model_name }}Form(req._params)
        if form.validate():
            for attr, value in form.data.iteritems():
                setattr(item, attr, value)
            item.save()
            redirect('/list_{{ table_name }}')

        items = {{ model_name }}.select()
        template = env.get_template('templates/{{ table_name }}/form.html')
        return template.render(items=items, form=form)

    def delete_{{ table_name }}(self,req,resp):
        item = {{ model_name }}.get({{ model_name }}.id == {{ table_name }}_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })
        """
    def gen_models(self):
        models_dir = output_dir + '/models/'
        models_file = models_dir + db_name + '.py'
        if db_config.get('password') != '':
            cmd = '''python -m pwiz -e mysql -u%s -H%s -P%s -p%s %s > %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('password'), db_config.get('port'), db_name,
                models_file)
        else:
            cmd = '''python -m pwiz -e mysql -u%s -H%s -p%s %s > %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('port'), db_name, models_file)
        rc, stdout, stderr = exec_cmd(cmd)
        if rc != 0:
            print 'generator models error ,%s' % stderr
        else:
            db_conf_file = output_dir + '/configs/db.py'
            with open(db_conf_file,'w+') as fp:
                fp.write('db_config = %s' % json.dumps(db_config))
            with open(models_file,'r+') as fp:
                content = fp.readlines()
                content[1] = "from configs.db import * \n"
                content[2] = "database = MySQLDatabase('%s', **db_config) \n"
            with open(models_file,'w+') as fp:
                fp.writelines(content)

    #admin & resutful
    def gen_controllers(self):
        controllers_dir = output_dir + '/controllers/'


    def gen_controller(self,table,model):
        t = Template(self.controller_template)
        controller_content = t.render(db_name=db_name,table_name=table,
                                      model_name=model)
        return controller_content

    #list include curd form views
    def gen_views(self):
        views_dir = output_dir + '/views/'

    def gen_view(self,table,model):
        pass

    def gen_forms(self):
        for table in self.table_data:
	    model_name = self.table_data.get(table).get('class_name')
	    self.gen_form(table,model_name)

    def gen_form(self,table,model_name):
        form_file = output_dir + '/views/' + table + '/' + 'form.html'
        form_fields = []
	import sys
        fields = self.table_data.get(table)
        for item in fields['fields']:
            field_name = item.keys()[0]
            field_type = field_type_to_wtforms[item[field_name]['raw_column_type']].__name__
            form_fields.append({'name': field_name, 'type_': field_type})
	if os.path.exists(form_file) is False:
	    os.makedirs(os.path.dirname(form_file))
        with open(form_file,'w+') as fout:
            fout.writelines(self.render(model_name,form_fields))

    def render(self,table,form_fields):
        t = Template(self.form_header + '\n\n' + self.form_template)
        return t.render(class_name=table, class_fields=form_fields)

    def gen_tables(self):
        class_list = []
        table_list = []
        result = {}
	introspector = Introspector.from_database(self.db)
        database = introspector.introspect()
        for table in sorted(database.model_names.values()):
            class_list.append(table)
        for table in sorted(database.model_names.keys()):
            table_list.append(table)
        for table,class_name in itertools.izip(table_list,class_list):
            item = {}
            item['class_name'] = class_name
            columns = database.columns[table]

            foreign_keys = database.foreign_keys[table]
            foreign_key_item = []
            for foreign_key in foreign_keys:
                dest_table = foreign_key.dest_table
                foreign_key_item.append({foreign_key:dest_table})
            item['foreign_keys'] = foreign_key_item

            cursor.execute("show full fields from %s"% table)
            sql_res = cursor.fetchall()
            field_item = []
            for field_name,column in columns.items():
                field = {}
                field['field_name'] = field_name;
                field['raw_column_type'] = column.raw_column_type;
                field['nullable'] = column.nullable;
                field['is_primary_key'] = column.primary_key
                field_item.append({ field_name : field })
                for res in sql_res:
                    if res[0] == field_name:
                        field['comment'] = res[8]
                        field['default'] = res[5]
                        field['raw_types'] = res[1]
            item['fields'] = sorted(field_item)
            result.update({table:item})
        return result

g = Generator(db)
g.gen_forms()
