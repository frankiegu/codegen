# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

RoomForm = model_form(Room)

class room:
    def index(self,req,resp):
        template = env.get_template('views/room.html')
        return template.render()

    def create(self,req,resp):
        form = RoomForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Room.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Room.get(Room.id == room_id)
        return item

    def edit(self,req,resp):
        try:
            room = Room.get(id=room_id)
        except Room.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = RoomForm(Request._params, obj=room)
            if form.validate():
                form.populate_obj(room)
                room.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/room.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Room.get(Room.id == room_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })