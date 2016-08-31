# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

ServerTagForm = model_form(ServerTag)

class server_tag:
    def index(self,req,resp):
        template = env.get_template('views/server_tag.html')
        return template.render()

    def create(self,req,resp):
        form = ServerTagForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = ServerTag.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = ServerTag.get(ServerTag.id == server_tag_id)
        return item

    def edit(self,req,resp):
        try:
            server_tag = ServerTag.get(id=server_tag_id)
        except ServerTag.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = ServerTagForm(Request._params, obj=server_tag)
            if form.validate():
                form.populate_obj(server_tag)
                server_tag.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/server_tag.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = ServerTag.get(ServerTag.id == server_tag_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })