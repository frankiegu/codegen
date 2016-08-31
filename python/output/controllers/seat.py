# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

SeatForm = model_form(Seat)

class seat:
    def index(self,req,resp):
        template = env.get_template('views/seat.html')
        return template.render()

    def create(self,req,resp):
        form = SeatForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Seat.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Seat.get(Seat.id == seat_id)
        return item

    def edit(self,req,resp):
        try:
            seat = Seat.get(id=seat_id)
        except Seat.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = SeatForm(Request._params, obj=seat)
            if form.validate():
                form.populate_obj(seat)
                seat.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/seat.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Seat.get(Seat.id == seat_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })