from flask import Blueprint,Response
from flask_restful import reqparse, Resource, Api
from config import vendors,regions
from units import token_auth,consul_kv
from units.prom import mysql_huawei,mysql_ali,mysql_tencent,redis_huawei,redis_ali
import json
blueprint = Blueprint('cloud_metrics',__name__)
api = Api(blueprint)

class RdsExporter(Resource):
    def get(self,vendor,account,region):
        if vendor == 'huaweicloud':
            prom_metric_list = mysql_huawei.exporter(vendor,account,region)
        elif vendor == 'alicloud':
            prom_metric_list = mysql_ali.exporter(vendor,account,region)
        elif vendor == 'tencent_cloud':
            prom_metric_list = mysql_tencent.exporter(vendor,account,region)
        return Response('\n'.join(prom_metric_list).encode('utf-8'),mimetype="text/plain")

class RedisExporter(Resource):
    def get(self,vendor,account,region):
        if vendor == 'huaweicloud':
            prom_metric_list = redis_huawei.exporter(vendor,account,region)
        elif vendor == 'alicloud':
            prom_metric_list = redis_ali.exporter(vendor,account,region)
        #elif vendor == 'tencent_cloud':
            #prom_metric_list = mysql_tencent.exporter(vendor,account,region)
        return Response('\n'.join(prom_metric_list).encode('utf-8'),mimetype="text/plain")
api.add_resource(RdsExporter, '/api/cloud_mysql_metrics/<vendor>/<account>/<region>')
api.add_resource(RedisExporter, '/api/cloud_redis_metrics/<vendor>/<account>/<region>')
