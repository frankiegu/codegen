# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

SwitchMacTableForm = model_form(SwitchMacTable)

class switch_mac_table:
    def index(self,req,resp):
        template = env.get_template('views/switch_mac_table.html')
        return template.render()

    def create(self,req,resp):
        form = SwitchMacTableForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = SwitchMacTable.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = SwitchMacTable.get(SwitchMacTable.id == switch_mac_table_id)
        return item

    def edit(self,req,resp):
        try:
            switch_mac_table = SwitchMacTable.get(id=switch_mac_table_id)
        except SwitchMacTable.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = SwitchMacTableForm(Request._params, obj=switch_mac_table)
            if form.validate():
                form.populate_obj(switch_mac_table)
                switch_mac_table.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/switch_mac_table.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = SwitchMacTable.get(SwitchMacTable.id == switch_mac_table_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })