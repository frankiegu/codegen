# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

IpForm = model_form(Ip)

class ip:
    def index(self,req,resp):
        template = env.get_template('views/ip.html')
        return template.render()

    def create(self,req,resp):
        form = IpForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Ip.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Ip.get(Ip.id == ip_id)
        return item

    def edit(self,req,resp):
        try:
            ip = Ip.get(id=ip_id)
        except Ip.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = IpForm(Request._params, obj=ip)
            if form.validate():
                form.populate_obj(ip)
                ip.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/ip.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Ip.get(Ip.id == ip_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })