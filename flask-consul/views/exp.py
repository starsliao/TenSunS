from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from units import token_auth,consul_kv
from config import vendors
import json
from .jobs import deljob,addjob,runjob
blueprint = Blueprint('exp',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('query_dict',type=str)
parser.add_argument('exp_config_dict',type=dict)
parser.add_argument('isnotify_dict',type=dict)

class Exp(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self,stype):
        if stype == 'list':
            switch = consul_kv.get_value(f'ConsulManager/exp/config').get('switch',False)
            if not switch:
                return({'code': 20000,'exp_list':[],'vendor_list':[],'account_list':[],'amount_list':[]})
            args = parser.parse_args()
            query_dict = json.loads(args['query_dict'])
            if query_dict['vendor'] != '':
                query_dict['vendor'] = {v : k for k, v in vendors.items()}[query_dict['vendor']]
            query_set = set({k:v for k,v in query_dict.items() if v != ''}.items())
            cloud_job_list = consul_kv.get_keys_list('ConsulManager/jobs')
            cloud_list = [i for i in cloud_job_list if i.endswith('/group')]
            exp_dict = consul_kv.get_kv_dict(f'ConsulManager/exp/lists')
            exp_list = []
            amount_list = []
            for i in cloud_list:
                vendor,account = i.split('/')[2:4]
                cloud_info_dict = {'vendor':vendor,'account':account}
                if query_set.issubset(cloud_info_dict.items()):
                    pass
                else:
                    continue
                amount = consul_kv.get_value(f'ConsulManager/exp/lists/{vendor}/{account}/amount')['amount']
                amount_list.append({'vendor':vendors[vendor],'account':account,'amount':amount})
                exp_dict = consul_kv.get_value(f'ConsulManager/exp/lists/{vendor}/{account}/exp')
                for k,v in exp_dict.items():
                    isnotify = consul_kv.get_value(f"ConsulManager/exp/isnotify/{vendor}/{account}/{v['notify_id']}").get('isnotify',True)
                    exp_list.append({'vendor':vendors[vendor],'account':account,'id':k,'Region':v['Region'],
                        'Product':v['Product'],'Name':v.get('Name','Null'),'EndTime':v['EndTime'],
                        'Ptype':v['Ptype'].replace('hws.resource.type.',''),
                        'notify_id': v['notify_id'],'isnotify':isnotify})
            vendor_list = sorted(list(set([i['vendor'] for i in exp_list])))
            account_list = sorted(list(set([i['account'] for i in exp_list])))
            return {'code': 20000,'exp_list':exp_list,'vendor_list':vendor_list,'account_list':account_list,'amount_list':amount_list}
        if stype == 'config':
            exp_config = consul_kv.get_value('ConsulManager/exp/config')
            return {'code': 20000, 'exp_config': exp_config}
    def post(self,stype):
        if stype == 'isnotify':
            args = parser.parse_args()
            isnotify_dict = args['isnotify_dict']
            vendor = {v : k for k, v in vendors.items()}[isnotify_dict['vendor']]
            account = isnotify_dict['account']
            notify_id = isnotify_dict['notify_id']
            isnotify = isnotify_dict['isnotify']
            if not isnotify:
                consul_kv.put_kv(f'ConsulManager/exp/isnotify/{vendor}/{account}/{notify_id}',{'isnotify':isnotify})
                return {'code': 20000, 'data': '此条资源告警关闭！', 'type': 'warning'}
            else:
                consul_kv.del_key(f'ConsulManager/exp/isnotify/{vendor}/{account}/{notify_id}')
                return {'code': 20000, 'data': '此条资源告警开启！', 'type': 'success'}
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
api.add_resource(Exp, '/api/exp/<stype>')
