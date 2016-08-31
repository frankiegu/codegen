# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

ManufacturerForm = model_form(Manufacturer)

class manufacturer:
    def index(self,req,resp):
        template = env.get_template('views/manufacturer.html')
        return template.render()

    def create(self,req,resp):
        form = ManufacturerForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Manufacturer.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Manufacturer.get(Manufacturer.id == manufacturer_id)
        return item

    def edit(self,req,resp):
        try:
            manufacturer = Manufacturer.get(id=manufacturer_id)
        except Manufacturer.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = ManufacturerForm(Request._params, obj=manufacturer)
            if form.validate():
                form.populate_obj(manufacturer)
                manufacturer.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/manufacturer.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Manufacturer.get(Manufacturer.id == manufacturer_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })