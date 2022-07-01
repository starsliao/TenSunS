from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from units import token_auth,consul_kv
import json
from .jobs import deljob,addjob,runjob
blueprint = Blueprint('exp',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('exp_config_dict',type=dict)
 
class Exp(Resource):
    #decorators = [token_auth.auth.login_required]
    def get(self,stype):
        if stype == 'list':
            exp_dict = consul_kv.get_kv_dict('ConsulManager/exp/list')
            exp_list = list(exp_dict.values())
            return {'code': 20000, 'exp_list': exp_list}
        if stype == 'config':
            exp_config = consul_kv.get_value('ConsulManager/exp/switch')
            return {'code': 20000, 'exp_config': exp_config}
    def post(self,stype):
        if stype == 'config':
            args = parser.parse_args()
            exp_config_dict = args['exp_config_dict']
            consul_kv.put_kv('ConsulManager/exp/config',exp_config_dict)
            cloud_job_list = consul_kv.get_keys_list('ConsulManager/jobs')
            cloud_list = [i for i in cloud_job_list if i.endswith('/group')]
            collect_days = exp_config_dict['collect_days']
            notify_days = exp_config_dict['notify_days']
            notify_amount = exp_config_dict['notify_amount']
            if exp_config_dict['switch']:
                for i in cloud_list:
                    vendor,account = i.split('/')[2:4]
                    exp_job_id = f'{vendor}/{account}/exp'
                    exp_job_func = f'__main__:{vendor}.exp'
                    exp_job_args = [account,collect_days,notify_days,notify_amount]
                    exp_job_interval = 60
                    addjob(exp_job_id,exp_job_func,exp_job_args,exp_job_interval)
                    exp_job_dict = {'id':exp_job_id,'func':exp_job_func,'args':exp_job_args,'minutes':exp_job_interval,'trigger': 'interval','replace_existing': True}
                    consul_kv.put_kv(f'ConsulManager/exp/jobs/{vendor}/{account}',exp_job_dict)
                    runjob(exp_job_id)
                return {'code': 20000, 'data': '到期日与余额采集功能开启！'}
            else:
                for i in cloud_list:
                    vendor,account = i.split('/')[2:4]
                    exp_job_id = f'{vendor}/{account}/exp'
                    deljob(exp_job_id)
                    consul_kv.del_key_all('ConsulManager/exp/jobs/')
                    consul_kv.del_key_all('ConsulManager/exp/lists/')
                return {'code': 20000, 'data': '到期日与余额采集功能关闭！'}
        if stype == 'run':
            exp_config_dict = consul_kv.get_value('ConsulManager/exp/switch')
            if exp_config_dict['switch']:
                consul_kv.del_key('ConsulManager/exp/list/0')
                runjob('exp_list')
                return {'code': 20000, 'data': '漏洞采集通知执行成功！'}
            else:
                return {'code': 50000, 'data': '漏洞采集功能未开启！'}
api.add_resource(Exp, '/api/exp/<stype>')
