# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

DeviceForm = model_form(Device)

class device:
    def index(self,req,resp):
        template = env.get_template('views/device.html')
        return template.render()

    def create(self,req,resp):
        form = DeviceForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Device.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Device.get(Device.id == device_id)
        return item

    def edit(self,req,resp):
        try:
            device = Device.get(id=device_id)
        except Device.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = DeviceForm(Request._params, obj=device)
            if form.validate():
                form.populate_obj(device)
                device.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/device.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Device.get(Device.id == device_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })