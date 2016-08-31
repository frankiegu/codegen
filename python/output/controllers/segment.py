# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

SegmentForm = model_form(Segment)

class segment:
    def index(self,req,resp):
        template = env.get_template('views/segment.html')
        return template.render()

    def create(self,req,resp):
        form = SegmentForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = Segment.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = Segment.get(Segment.id == segment_id)
        return item

    def edit(self,req,resp):
        try:
            segment = Segment.get(id=segment_id)
        except Segment.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = SegmentForm(Request._params, obj=segment)
            if form.validate():
                form.populate_obj(segment)
                segment.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/segment.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = Segment.get(Segment.id == segment_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })