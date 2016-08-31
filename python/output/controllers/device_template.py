# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

DeviceTemplateForm = model_form(DeviceTemplate)

class device_template:
    def index(self,req,resp):
        template = env.get_template('views/device_template.html')
        return template.render()

    def create(self,req,resp):
        form = DeviceTemplateForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = DeviceTemplate.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = DeviceTemplate.get(DeviceTemplate.id == device_template_id)
        return item

    def edit(self,req,resp):
        try:
            device_template = DeviceTemplate.get(id=device_template_id)
        except DeviceTemplate.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = DeviceTemplateForm(Request._params, obj=device_template)
            if form.validate():
                form.populate_obj(device_template)
                device_template.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/device_template.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = DeviceTemplate.get(DeviceTemplate.id == device_template_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })