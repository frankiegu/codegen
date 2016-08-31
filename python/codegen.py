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
import pyclbr
import time
import MySQLdb
from playhouse.reflection import Introspector
from peewee import *
from jinja2 import Environment, FileSystemLoader, Template
from wtfpeewee.orm import model_form,model_fields

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
        '''<label for="assets">Assets</label>'''
        self.form_template = '''

          <div class="modal fade" tabindex="-1" role="dialog" id="{{table_name}}_form">
                <div class="modal-dialog modal-dialog-confrim" role="document">
                    <div class="modal-content">
                        <div class="modal-body">
                            <form method="post" id="{{ table_name }}_form">
                                {% for field in form %}
                                  <p>{{ field.label }} : {{ field }}</p>
                                {% endfor %}
                                <p><button type="submit">Submit</button></p>
                            </form>
                        </div>
                    </div>
                </div>
          </div>
          

          <div class="mz-body-right">
                <div class="panel panel-default">
                    <div class="panel-heading noline">
                        <h3 class="panel-title">{{model_name}}</h3>
                    </div>
                    <div class="panel-body" style="position:relative">
                        <table class="table table-striped" id="table">
                            <thead>
                                <tr>
                                    <th><label class="checkbox"><input type="checkbox" id="checkAll"><i></i></label></th>
                                    {% for field in form %}
                                    <th>{{ field.description }}</th>
                                    {% endfor %}
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody id="list_body">

                            </tbody>
                        </table>
                        <nav class="mz-text-right">
                            <ul class="pagination">
                                <li class="active">分页</li>
                            </ul>
                        </nav>

                        <div class="toolbox" id="toolbox">
                            <p class="tip">你已经选择 <b id="tip_num"></b> 项</p>
                            <button type="button" class="btn btn-danger" data-dismiss="modal">删除</button>
                        </div>


                    </div>
                </div>
            </div>
            <div class="mz-clear"></div>
    
            <div class="modal fade" tabindex="-1" role="dialog" id="delModal">
                <div class="modal-dialog modal-dialog-confrim" role="document">
                    <div class="modal-content">
                        <div class="modal-body">
                            你确定要删除吗？
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-cancel" data-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-danger" id="delModal-del" data-id="" data-dismiss="modal">删除</button>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="modal fade" tabindex="-1" role="dialog" id="tipsModal">
                <div class="modal-dialog modal-dialog-confrim" role="document">
                    <div class="modal-content">
                        <div class="modal-body" id="tipsModal-modal-body">
                            操作成功
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal fade" tabindex="-1" role="dialog" id="detailModal">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                            <h4 class="modal-title">详情</h4>
                        </div>
                        <div class="modal-body" style="min-height: 350px;padding-top: 50px;">
                            <div style="padding-left:100px;" id ="msg_content">
    
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">返回</button>
                            <button type="button" class="btn btn-danger" id="detailModal-del" data-id="" data-dismiss="modal">删除</button>
                        </div>
                    </div>
                </div>
            </div>
'''
        self.header_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="assets/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/css/select2.css">
    <link rel="stylesheet" href="assets/css/daterangepicker.css">
    <link rel="stylesheet" href="assets/css/mzui.css">
    <link rel="stylesheet" href="assets/css/custom.css">
    <link rel="stylesheet" href="assets/css/user.css">
    <!--[if lt IE 9]>
    <script type="text/javascript" src="assets/js/html5shiv.min.js"></script>
    <![endif]-->
    <script type="text/javascript" src="assets/js/jquery.min.js"></script>
    <script type="text/javascript" src="assets/js/parsley.min.js"></script>
    <script type="text/javascript" src="assets/js/bootstrap.min.js"></script>
    <script type="text/javascript" src="assets/js/moment.min.js"></script>
    <script type="text/javascript" src="assets/js/select2.min.js"></script>
    <script type="text/javascript" src="assets/js/daterangepicker.min.js"></script>
    <script type="text/javascript" src="assets/js/util.js"></script>
    <script type="text/javascript" src="assets/js/common.js"></script>

</head>
<body>

    <div class="mz-header">
        <div class="w1240">
            <a href="index.html" class="mz-logo"></a>
            <div class="mz-shortcut">{% for url,title in top.iteritems() %}
                {% if loop.index0 == 1 %}<a class="action i-user">{{ title }}</a>{% endif %}
                {% if loop.index0 == 2 %}<a href="{{ url }}"  title="{{ title }}"  class="action i-charge"></a>{% endif %}
                {% if loop.index0 == 3 %}<a href="{{ url }}"  title="{{ title }}" class="action i-notify"></a>{% endif %}
                {% if loop.index0 == 4 %}<a href="{{ url }}"  title="{{ title }}"  class="action i-help"></a>{% endif %}
                {% if loop.last %}<a href="{{ url }}"  class="btn btn-primary">{{ title }}</a>{% endif %}
                {% endfor %}
            </div>
        </div>
    </div>
'''
        self.footer_template = '''
        <div class="footer" id="footer">

        </div>
        <script type="text/javascript">
            $(function() {
                var deleteUrl = '{{table_name}}/delete',
                    addUrl = '{{table_name}}/create',
                    editUrl = '{{table_name}}/edit',
                    getUrl = '{{table_name}}/lists';
                var table = $("#table"),
                    toolbox = $('#toolbox'),
                    tips = $('#tips'),
                    checkAll = table.find('#checkAll'),
                    checkItem = table.find("td :checkbox"),
                    delBtn = table.find(".del"),
                    deleteBtn = $(".modal-footer .btn-danger"),
                    deletemManyBtn = $("#toolbox .btn-danger"),
                    defaultBtn = $('#toolbox .btn-default'),
                    detailBtn = table.find(".detail");
                //全选
                checkAll.on("click", function(e) {
                    table.find(':checkbox').not(this).prop('checked', this.checked);
                    this.checked ? toolbox.fadeIn('fast') : toolbox.fadeOut('fast');
                    var checkedItem = table.find('td :checked');
                    $('#tip_num').html(checkedItem.length)
                });
                //单选
                checkItem.on("change", function(e) {
                    var checkedItem = table.find('td :checked');
                    checkAll.prop('checked', checkedItem.length === checkItem.length);
                    checkedItem.length ? toolbox.fadeIn('fast') : toolbox.fadeOut('fast');
                    $('#tip_num').html(checkedItem.length)
                });
                //显示删除弹窗
                delBtn.on("click", function(e) {
                    var id = $(e.currentTarget).attr('data-id')
                    $('#delModal-del').attr('data-id',id)
                    $('#delModal').modal({
                        "keyboard": true,
                        "show": true
                    });
                });
                //详情
                detailBtn.on("click", function(e) {
                    e.stopPropagation()
                    var id = $(e.currentTarget).attr('data-id')
                    content = '' //todo
                    $('#msg_content').html(content)
                    $('#detailModal').modal({
                        "keyboard": true,
                        "show": true
                    });
                });
                var get_check_msg_id = function (e) {
                    var checkedItem = table.find('td :checked');
                    msg_id_arr = new Array()
                    for (var i = 0; i < checkedItem.length; i++) {
                        id = $(checkedItem[i]).attr('data-id')
                        msg_id_arr.push(id)
                    }
                    msg_ids = msg_id_arr.join(",")
                    return msg_ids
                };
                var tip_show = function (text) {
                    $('#tipsModal-modal-body').html(text)
                    $('#tipsModal').modal({
                        "keyboard": true,
                        "show": true
                    });
                    setTimeout(function (e) {
                        $('#tipsModal').modal('hide')
                    }, 1000);
                };
                var remove_checked = function (e) {
                    var checkedItem = table.find('td :checked');
                    for (var i = 0; i < checkedItem.length; i++) {
                        $(checkedItem[i]).removeAttr('checked')
                    }
                };
                var tip_sucess="操作成功",
                    tips_error='操作失败';
                var ajax = function (url,data,show_tips) {
                    $.ajax({
                        type: "POST",
                        dataType: "json",
                        url: url,
                        data: data,
                        success: function (data) {
                            if(show_tips != false){
                                tip_show(tip_sucess)
                                window.location.reload()
                            }
                        },
                        error: function (data) {
                            if(show_tips != false){
                                tip_show(tips_error)
                            }
                        }
                    });
                };
                //删除
                deleteBtn.on("click", function(e) {
                    var id = $(e.currentTarget).attr('data-id')
                    ajax(deleteUrl,{'id':id})
                });
                //批量删除
                deletemManyBtn.on("click", function(e) {
                    id = get_check_msg_id()
                    ajax(deleteUrl,{'id':id})
                    toolbox.fadeOut('fast')
                    remove_checked()
                });

                //获取某一页列表
                var list_body = function(page_num,page_count){
                    $.ajax({
                        type: "POST",
                        dataType: "json",
                        url: getUrl,
                        data: {'page_num':page_num,'page_count':page_count},
                        success: function (data) {
                            if(data.length>1){
                                html_content = '';
                                for(item in data){
                                    html_content += '<tr>'+
                                                        '<td><label class="checkbox"><input type="checkbox" data-id="'+data[item].{{primary_field}}+'"><i></i></label></td>'+
                                                        {% for field in form %}'<th>'+data[item].{{ field.field_name }}+'</th>'+
                                                        {% endfor %}
                                                        '<td>'+
                                                            '<a href="#" data-id="'+data[item].{{primary_field}}+'" class="action detail">详情</a>'+
                                                            '<a href="#" data-id="'+data[item].{{primary_field}}+'" class="action del">删除</a>'+
                                                        '</td>'+
                                                    '</tr>';
                                }
                            }

                            $('#list_body').html(html_content)

                        },
                        error: function (data) {
                            tip_show('获取列表数据出错')
                        }
                    });
                }

                list_body()

            });
        </script>
    </div>

</body>
</html>
'''
        self.body_left_template = '''
<div class="mz-body">
    <div class="mz-body-left">
        <div class="panel panel-default">
            <div class="panel-body no-padding">
                <ul class="mz-menu">
                    {% for group,items in nav.iteritems() %}
                    <li class="open">
                        <a><span class="i-home"></span>{{ group }}<i></i></a>
                        <ul>
                            {% for url,title in items.iteritems() %}
                            <li><a href="{{ url }}">{{ title }}</a></li>
                            {% endfor %}
                        </ul>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>

    <div id="popmenu">
        <ul class="mz-popmenu">
            {% for url,title in popmenu.iteritems() %}
            <li><a href="{{ url |e }}">{{ title |e }}</a></li>
            {% endfor %}
        </ul>
    </div>

'''
        self.controller_template = """# -*- coding:utf8 -*-
import falcon
from models.{{ db_name }} import *
from wtfpeewee.orm import model_form
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

{{ model_name }}Form = model_form({{ model_name }})

class {{ table_name }}:
    def index(self,req,resp):
        template = env.get_template('views/{{ table_name }}.html')
        return template.render()

    def lists(self,req,resp):
        result = []
        list_items = {{ model_name}}.select()
        return result

    def create(self,req,resp):
        form = {{ model_name }}Form(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = {{ model_name }}.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = {{ model_name }}.get({{ model_name}}.id == {{ table_name }}_id)
        return item

    def edit(self,req,resp):
        try:
            {{ table_name}} = {{ model_name}}.get(id={{ table_name}}_id)
        except {{ model_name}}.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = {{ model_name}}Form(Request._params, obj={{ table_name}})
            if form.validate():
                form.populate_obj({{ table_name}})
                {{ table_name}}.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/{{table_name}}.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = {{ model_name }}.get({{ model_name }}.id == {{ table_name }}_id)
        item.delete_instance()
        return {
            'status': 'success',
            'message': 'Item was deleted'
        }"""

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
            print "gen models error %s" % stderr
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

    def gen_header(self,title=''):
        top = {}
        top.update({'http://www.qq.com':'qq'})
        top.update({'http://www.google.com':'google'})
        top.update({'http://www.taobao.com':'淘宝'})
        top.update({'http://www.alipay.com':'支付宝'})
        top.update({'http://www.momo.im':'陌陌'})
        nav = {}
        nav.update({'组1':{'http://www.taobao.com':'淘宝'}})
        nav.update({'组1':{'http://www.google.com':'google'}})
        nav.update({'组2': {'http://www.alipay.com':'支付宝'}})
        nav.update({'组2':{'http://www.qq.com':'qq'}})
        popmenu = {}
        popmenu.update({'http://www.xiaomatech.us':'aaa'})
        popmenu.update({'http://www.nofwa.im':'bbbb'})

        t = Template(self.header_template + '\n\n' + self.body_left_template)
        content = t.render(top=top,nav=nav,popmenu=popmenu,title=title)
        return content
    def gen_view(self, table, model_name):
        view_dir = output_dir + '/views/'
        view_file = output_dir + '/views/' + table + '.html'
        if os.path.exists(view_dir) is False:
            os.makedirs(view_dir)
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
        t = Template(self.form_template + '\n\n' + self.footer_template)
        content = t.render(table_name=table,model_name=model_name,form=form,primary_field=primary_field)
        with open(view_file, 'w+') as fout:
            fout.writelines(self.gen_header(title=model_name) + content)

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
