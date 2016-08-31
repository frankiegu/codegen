# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

RackForm = model_form(Rack)

class rack:
    def index(self,req,resp):
        template = env.get_template('views/rack.html')
        return template.render()

    def create(self,req,resp):
        form = RackForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Rack.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Rack.get(Rack.id == rack_id)
        return item

    def edit(self,req,resp):
        try:
            rack = Rack.get(id=rack_id)
        except Rack.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = RackForm(Request._params, obj=rack)
            if form.validate():
                form.populate_obj(rack)
                rack.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/rack.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Rack.get(Rack.id == rack_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })