# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

ServerTagUserForm = model_form(ServerTagUser)

class server_tag_user:
    def index(self,req,resp):
        template = env.get_template('views/server_tag_user.html')
        return template.render()

    def create(self,req,resp):
        form = ServerTagUserForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = ServerTagUser.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = ServerTagUser.get(ServerTagUser.id == server_tag_user_id)
        return item

    def edit(self,req,resp):
        try:
            server_tag_user = ServerTagUser.get(id=server_tag_user_id)
        except ServerTagUser.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = ServerTagUserForm(Request._params, obj=server_tag_user)
            if form.validate():
                form.populate_obj(server_tag_user)
                server_tag_user.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/server_tag_user.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = ServerTagUser.get(ServerTagUser.id == server_tag_user_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })