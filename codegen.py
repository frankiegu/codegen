#!/usr/bin/env python
# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
import os
import json
import itertools
import shutil
import re
import MySQLdb
from playhouse.reflection import Introspector
from peewee import *
from jinja2 import Environment, FileSystemLoader, Template
from wtfpeewee.orm import model_form

db = MySQLDatabase(db_name, **db_config)
conn = MySQLdb.connect(host=db_config.get('host'),
                       user=db_config.get('user'),
                       passwd=db_config.get('password'),
                       db=db_name)
cursor = conn.cursor()

env = Environment(loader=FileSystemLoader(output_dir + 'views'))

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
    def __init__(self, db):
        self.db = db
        self.table_data = self.gen_tables()
        with open('./views/form.j2', 'rb+') as fp:
            self.form_template = fp.read()
        with open('./views/header.j2', 'rb+') as fp:
            self.header_template = fp.read()
        with open('./views/footer_all.j2', 'rb+') as fp:
            self.footer_template_all = fp.read()
        with open('./views/nav.j2', 'rb+') as fp:
            self.nav_template = fp.read()
        with open('./views/controller.j2', 'rb+') as fp:
            self.controller_template = fp.read()
        with open('./views/footer.j2', 'rb+') as fp:
            self.footer_template = fp.read()
        with open('./views/footer_js.j2', 'rb+') as fp:
            self.footer_js_template = fp.read()
        self.header_top = {}
        self.nav = {}
        self.popmenu = {}
        self.gen_common()

    def add_header_top(self,header_top):
        '''
            添加顶部导航
        :param header_top: dict 类似 {'http://www.qq.com':'qq'}
        '''
        self.header_top.update(header_top)

    def add_nav(self,nav):
        '''
            添加左边导航
        :param header_top: dict 类似 {'分组1':{'http://www.taobao.com':'淘宝'}}
        '''
        self.nav.update(nav)

    def add_popmenu(self,popmenu):
        '''
            添加顶部下拉提示
        :param header_top: dict 类似 {'http://www.qq.com':'qq'}
        '''
        self.popmenu.update(popmenu)

    def gen_models(self):
        models_dir = output_dir + '/models/'
        model_file = models_dir + db_name + '.py'
        if os.path.exists(models_dir) is False:
            os.makedirs(models_dir)
        if db_config.get('password') != '':
            cmd = '''python -m pwiz -e mysql -u%s -H%s -P%s -p%s %s> %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('password'), db_config.get('port'), db_name,
                model_file)
        else:
            cmd = '''python -m pwiz -e mysql -u%s -H%s -p%s %s> %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('port'), db_name, model_file)
        rc, stdout, stderr = exec_cmd(cmd)
        if rc != 0:
            raise Exception(stderr)
        shutil.copy(model_file,'model/__init__.py')
        db_conf_file = output_dir + '/configs/db.py'
        if os.path.exists(output_dir + '/configs') is False:
            os.makedirs(output_dir + '/configs')
        with open(db_conf_file, 'w+') as fp:
            fp.write('db_config = %s' % json.dumps(db_config))
        with open(model_file, 'r+') as fp:
            content = fp.readlines()
            content[1] = "from configs.db import * \n"
            content[2] = "database = MySQLDatabase('%s', **db_config) \n" % db_name
        with open(model_file, 'w+') as fp:
            fp.writelines(content)

    def gen_alls(self):
        for table in self.table_data:
            model_name = self.table_data.get(table).get('class_name')
            self.gen_one(table,model_name)
        #还原 model/__init__.py
        with(open('model/__init__.py','w+')) as fout:
            fout.write('')

    def gen_one(self,table,model_name):
        self.gen_ctr_model(table,model_name)
        self.gen_view(table,model_name)

    def create_model_file(self):
        self.model_file = 'model/__init__.py'
        if db_config.get('password') != '':
            cmd = '''python -m pwiz -e mysql -u%s -H%s -P%s -p%s %s> %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('password'), db_config.get('port'), db_name,
                self.model_file)
        else:
            cmd = '''python -m pwiz -e mysql -u%s -H%s -p%s %s> %s''' % (
                db_config.get('user'), db_config.get('host'),
                db_config.get('port'), db_name, self.model_file)
        rc, stdout, stderr = exec_cmd(cmd)
        if rc != 0:
            raise Exception(stderr)

    def gen_ctr_model(self,table,model_name):
        #生成controller

        #生成model

        pass

    #admin & resutful
    def gen_controllers(self):
        for table in self.table_data:
            model_name = self.table_data.get(table).get('class_name')
            self.gen_controller(table, model_name)

    def gen_controller(self, table, model_name):
        controller_file = output_dir + '/controllers/' + table + '.py'
        t = Template(self.controller_template)
        controller_content = t.render(db_name=db_name,
                                      table_name=table,
                                      model_name=model_name)
        if os.path.exists(os.path.dirname(controller_file)) is False:
            os.makedirs(os.path.dirname(controller_file))
        with open(controller_file, 'w+') as fout:
            fout.writelines(controller_content)

    #list include curd form views
    def gen_views(self):
        for table in self.table_data:
            model_name = self.table_data.get(table).get('class_name')
            self.gen_view(table,model_name)
        #还原 model/__init__.py
        with(open('model/__init__.py','w+')) as fout:
            fout.write('')

    def gen_common(self):
        view_dir = output_dir + '/views/common'
        if os.path.exists(view_dir) is False:
            os.makedirs(view_dir)
        header_file = view_dir + '/header.html'
        if os.path.exists(header_file) is False:
            t = Template(self.header_template)
            header_content = t.render(top=self.header_top,nav=self.nav,popmenu=self.popmenu)
            with open(header_file, 'w+') as fout:
                fout.writelines(header_content)
        else:
            with open(header_file, 'rb+') as fp:
                header_content = fp.read()
        nav_file = view_dir + '/nav.html'
        if os.path.exists(nav_file) is False:
            t = Template(self.nav_template)
            nav_content = t.render(top=self.header_top,nav=self.nav,popmenu=self.popmenu)
            with open(nav_file, 'w+') as fout:
                fout.writelines(nav_content)
        else:
            with open(nav_file, 'rb+') as fp:
                nav_content = fp.read()
        self.header_content = header_content
        self.nav_content = nav_content

        footer_file = view_dir + '/footer.html'
        if os.path.exists(footer_file) is False:
            t = Template(self.footer_template)
            footer_content = t.render(top=self.header_top,nav=self.nav,popmenu=self.popmenu)
            with open(nav_file, 'w+') as fout:
                fout.writelines(footer_content)
        else:
            with open(footer_file, 'rb+') as fp:
                footer_content = fp.read()
        self.footer_content = footer_content

    def gen_view(self, table, model_name):
        view_dir = output_dir + '/views/models/'
        view_dir_all = output_dir + '/views/all/'
        view_file = view_dir + table + '.html'
        view_file_all = view_dir_all + table + '.html'
        if os.path.exists(view_dir) is False:
            os.makedirs(view_dir)
        if os.path.exists(view_dir_all) is False:
            os.makedirs(view_dir_all)
        from model import *
        mode_class = eval(model_name)
        EntryForm = model_form(mode_class)
        form = EntryForm()
        fields = self.table_data[table].get('fields')
        for field in form:
            field_name = field.__dict__.get('short_name')
            field.__dict__.update(fields.get(field_name))
            field.label = '<label for="' + field.__dict__['comment'] + '">' + field.__dict__['comment']  + '</label>'
            field.description = field.__dict__['comment']
        primary_field = mode_class._meta.primary_key.db_column

        t = Template(self.form_template + '\n\n' + self.footer_js_template)
        all_content = t.render(table_name=table,model_name=model_name,form=form,primary_field=primary_field)

        with open(view_file_all, 'w+') as fout:
            fout.writelines(self.header_content + '\n' + self.nav_content + '\n' + all_content + '\n' + self.footer_content)

        with open(view_file, 'w+') as fout:
            fout.writelines(all_content)

    def render(self, table, form_fields):
        t = Template(self.form_header + self.form_template)
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
        for table, class_name in itertools.izip(table_list, class_list):
            item = {}
            item['class_name'] = class_name
            columns = database.columns[table]

            foreign_keys = database.foreign_keys[table]
            foreign_key_item = []
            for foreign_key in foreign_keys:
                dest_table = foreign_key.dest_table
                foreign_key_item.append({foreign_key: dest_table})
            item['foreign_keys'] = foreign_key_item

            cursor.execute("show full fields from %s" % table)
            sql_res = cursor.fetchall()
            field_item = {}
            for field_name, column in columns.items():
                field = {}
                field['field_name'] = field_name
                field['raw_column_type'] = column.raw_column_type
                field['nullable'] = column.nullable
                field['is_primary_key'] = column.primary_key
                #field_item.append({field_name: field})
                for res in sql_res:
                    if res[0] == field_name:
                        field['comment'] = res[8] or re.sub('_+', ' ', field_name).title()
                        field['default'] = res[5]
                        field['raw_types'] = res[1]
                field_item.update({column.name: field})
            item['fields'] = field_item
            result.update({table: item})
        return result

def gen_all():
    g = Generator(db)
    g.gen_models()
    g.gen_controllers()
    g.gen_views()

def gen_table(table):
    g = Generator(db)
    model_name = g.table_data.get(table).get('class_name')
    g.gen_models()
    g.gen_controller(table,model_name)
    g.gen_view(table,model_name)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        table = sys.argv[1]
        gen_table(table)
    else:
        gen_all()
