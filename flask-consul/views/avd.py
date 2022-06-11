from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from units import token_auth,consul_kv
import json
from .jobs import deljob,addjob,runjob
blueprint = Blueprint('avd',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('avd_config_dict',type=dict)
 
class Avd(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self,stype):
        if stype == 'list':
            avd_dict = consul_kv.get_kv_dict('ConsulManager/avd/list')
            avd_list = list(avd_dict.values())
            return {'code': 20000, 'avd_list': avd_list}
        if stype == 'config':
            avd_config = consul_kv.get_value('ConsulManager/avd/switch')
            return {'code': 20000, 'avd_config': avd_config}
    def post(self,stype):
        if stype == 'config':
            args = parser.parse_args()
            avd_config_dict = args['avd_config_dict']
            consul_kv.put_kv('ConsulManager/avd/switch',avd_config_dict)
            avd_job_id = 'avd_list'
            avd_job_func = '__main__:avd_list.get_avd'
            avd_job_args = []
            avd_job_interval = 60
            if avd_config_dict['switch']:
                addjob(avd_job_id,avd_job_func,avd_job_args,avd_job_interval)
                avd_job_dict = {'id':avd_job_id,'func':avd_job_func,'args':avd_job_args,'minutes':avd_job_interval,
                                'trigger': 'interval','replace_existing': True}
                consul_kv.put_kv('ConsulManager/avd/jobs/avd_list',avd_job_dict)
                runjob(avd_job_id)
                return {'code': 20000, 'data': '漏洞采集通知功能开启！'}
            else:
                deljob(avd_job_id)
                consul_kv.del_key('ConsulManager/avd/jobs/avd_list')
                consul_kv.del_key_all('ConsulManager/avd/list/')
                return {'code': 20000, 'data': '漏洞采集通知功能关闭！'}
        if stype == 'run':
            avd_config_dict = consul_kv.get_value('ConsulManager/avd/switch')
            if avd_config_dict['switch']:
                consul_kv.del_key('ConsulManager/avd/list/0')
                runjob('avd_list')
                return {'code': 20000, 'data': '漏洞采集通知执行成功！'}
            else:
                return {'code': 50000, 'data': '漏洞采集功能未开启！'}
api.add_resource(Avd, '/api/avd/<stype>')
