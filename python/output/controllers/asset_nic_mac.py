# -*- coding:utf8 -*-
import falcon
from models.cmdb import *
from wtfpeewee.orm import model_form
from helpers.logger import *
from helpers.cache import *
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('views'))

AssetNicMacForm = model_form(AssetNicMac)

class asset_nic_mac:
    def index(self,req,resp):
        template = env.get_template('views/asset_nic_mac.html')
        return template.render()

    def create(self,req,resp):
        form = AssetNicMacForm(req._params)
        if req.method == 'POST':
            if form.validate():
                new_item = AssetNicMac.create(**form.data)
                return 'sucess'
            else:

        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def info(self,req,resp):
        item = AssetNicMac.get(AssetNicMac.id == asset_nic_mac_id)
        return item

    def edit(self,req,resp):
        try:
            asset_nic_mac = AssetNicMac.get(id=asset_nic_mac_id)
        except AssetNicMac.DoesNotExist:
            raise falcon.HTTPNotFound(description="The requested resource does not exist",code=falcon.HTTP_404)

        if req.method == 'POST':
            form = AssetNicMacForm(Request._params, obj=asset_nic_mac)
            if form.validate():
                form.populate_obj(asset_nic_mac)
                asset_nic_mac.save()
                return 'sucess'
            else:
                raise falcon.HTTPInvalidParam(msg='form invalid', param_name='controllers/asset_nic_mac.py')
        else:
            raise falcon.HTTPMethodNotAllowed(['POST'])

    def delete(self,req,resp):
        item = AssetNicMac.get(AssetNicMac.id == asset_nic_mac_id)
        item.delete_instance()
        return json.dumps({
            'status': 'success',
            'message': 'Item was deleted'
        })