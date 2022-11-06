from flask import Blueprint,Response
from flask_restful import reqparse, Resource, Api
from config import vendors,regions
from units import token_auth,consul_kv
from units.prom import mysql_huawei
import json
blueprint = Blueprint('cloud_mysql_metrics',__name__)
api = Api(blueprint)

class Exporter(Resource):
    def get(self,vendor,account,region):
        prom_metric_list = mysql_huawei.exporter(vendor,account,region)
        return Response('\n'.join(prom_metric_list).encode('utf-8'),mimetype="text/plain")
api.add_resource(Exporter, '/api/cloud_mysql_metrics/<vendor>/<account>/<region>')
