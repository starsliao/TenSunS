from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from units import token_auth,consul_kv,myaes
from config import vendors
import json
from .jobs import deljob,addjob,runjob
blueprint = Blueprint('jms',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('query_dict',type=str)
parser.add_argument('jms_config',type=dict)
parser.add_argument('isnotify_dict',type=dict)

class Jms(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self,stype):
        if stype == 'list':
            switch = consul_kv.get_value(f'ConsulManager/jms/jms_info')
            if switch == {}:
                return({'code': 20000,'exp_list':[],'vendor_list':[],'account_list':[]})
            args = parser.parse_args()
            query_dict = json.loads(args['query_dict'])
            if query_dict['vendor'] != '':
                query_dict['vendor'] = {v : k for k, v in vendors.items()}[query_dict['vendor']]
            query_set = set({k:v for k,v in query_dict.items() if v != ''}.items())
            cloud_job_list = consul_kv.get_keys_list('ConsulManager/jobs')
            cloud_list = [i for i in cloud_job_list if i.endswith('/group')]

            exp_list = []
            for i in cloud_list:
                vendor,account = i.split('/')[2:4]
                cloud_info_dict = {'vendor':vendor,'account':account}
                if query_set.issubset(cloud_info_dict.items()):
                    pass
                else:
                    continue
                count_group = consul_kv.get_value(f'ConsulManager/record/jobs/{vendor}/{account}/group')['count']
                services_meta = consul_kv.get_services_meta(f'{vendor}_{account}_ecs').get('ecs_list',[])
                count_ecs = len(services_meta)
                count_off,count_on,count_cpu,count_mem,count_win,count_linux = 0,0,0,0,0,0
                for i in services_meta:
                    if i['os'] == linux:
                        count_linux = count_linux + 1
                    elif i['os'] == windows:
                        count_win = count_win + 1
                    if i.get('stat') == off:
                        count_off = count_off + 1
                    else:
                        count_on = count_on + 1
                    cpu = int(i['cpu'].replace('核',''))
                    count_cpu = count_cpu + cpu
                    mem = int(i['cpu'].replace('GB',''))
                    count_mem = count_mem + mem
                
                exp_list.append({'vendor':vendors[vendor],'account':account,'id':k,'Region':v['Region'],
                        'Product':v['Product'],'Name':v.get('Name','Null'),'EndTime':v['EndTime'],
                        'Ptype':v['Ptype'].replace('hws.resource.type.',''),
                        'notify_id': v['notify_id'],'isnotify':isnotify})
            vendor_list = sorted(list(set([i['vendor'] for i in exp_list])))
            account_list = sorted(list(set([i['account'] for i in exp_list])))
            return {'code': 20000,'exp_list':exp_list,'vendor_list':vendor_list,'account_list':account_list,'amount_list':amount_list}
        if stype == 'config':
            ecs_info = consul_kv.get_value('ConsulManager/jms/ecs_info')
            jms_info = consul_kv.get_value('ConsulManager/jms/jms_info')
            if ecs_info != {} and jms_info != {}:
                linuxport = ecs_info['linux'][0][0].split('/')[-1]
                linuxuid = ecs_info['linux'][-1]
                winport = ecs_info['windows'][0][0].split('/')[-1]
                winuid = ecs_info['windows'][-1]
                token = myaes.decrypt(jms_info['token'])
                jms_config = {'url': jms_info['url'], 'token': token, 
                    'linuxport': linuxport, 'linuxuid': linuxuid, 
                    'winport': winport, 'winuid': winuid}
            else:
                jms_config = {}
            return {'code': 20000, 'jms_config': jms_config}
    def post(self,stype):
        if stype == 'config':
            args = parser.parse_args()
            jms_config = args['jms_config']
            token = myaes.encrypt(jms_config['token'])
            jms_info = {'url': jms_config['url'], 'token': token}
            consul_kv.put_kv('ConsulManager/jms/jms_info', jms_info)
            ecs_info = {"linux": [[f"ssh/{jms_config['linuxport']}"],jms_config['linuxuid']],
                "windows": [[f"rdp/{jms_config['winport']}"],jms_config['winuid']]}
            consul_kv.put_kv('ConsulManager/jms/ecs_info', ecs_info)
            return {'code': 20000, 'data': '配置完成'}
api.add_resource(Jms, '/api/jms/<stype>')
