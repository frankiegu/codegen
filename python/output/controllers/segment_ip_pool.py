# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

SegmentIpPoolForm = model_form(SegmentIpPool)

class segment_ip_pool:
    def index(self,req,resp):
        template = env.get_template('views/segment_ip_pool.html')
        return template.render()

    def create(self,req,resp):
        form = SegmentIpPoolForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = SegmentIpPool.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = SegmentIpPool.get(SegmentIpPool.id == segment_ip_pool_id)
        return item

    def edit(self,req,resp):
        try:
            segment_ip_pool = SegmentIpPool.get(id=segment_ip_pool_id)
        except SegmentIpPool.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = SegmentIpPoolForm(Request._params, obj=segment_ip_pool)
            if form.validate():
                form.populate_obj(segment_ip_pool)
                segment_ip_pool.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/segment_ip_pool.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = SegmentIpPool.get(SegmentIpPool.id == segment_ip_pool_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })