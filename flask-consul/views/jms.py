from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from units import token_auth,consul_kv,myaes
from config import vendors
import json,traceback
from .jobs import deljob,addjob,runjob,getjob
from units.config_log import *
blueprint = Blueprint('jms',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('query_dict',type=str)
parser.add_argument('jms_config',type=dict)
parser.add_argument('jms_sync',type=dict)
parser.add_argument('switch_dict',type=dict)

class Jms(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self,stype):
        if stype == 'list':
            switch = consul_kv.get_value(f'ConsulManager/jms/jms_info')
            if switch == {}:
                return({'code': 20000,'ecs_list':[],'vendor_list':[],'account_list':[]})
            args = parser.parse_args()
            query_dict = json.loads(args['query_dict'])
            if query_dict['vendor'] != '':
                query_dict['vendor'] = {v : k for k, v in vendors.items()}[query_dict['vendor']]
            query_set = set({k:v for k,v in query_dict.items() if v != ''}.items())
            cloud_job_list = consul_kv.get_keys_list('ConsulManager/jobs')
            cloud_list = [i for i in cloud_job_list if i.endswith('/group')]

            ecs_list = []
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
                    if i['os'] == 'linux':
                        count_linux = count_linux + 1
                    elif i['os'] == 'windows':
                        count_win = count_win + 1
                    if i.get('stat') == 'off':
                        count_off = count_off + 1
                    else:
                        count_on = count_on + 1
                    cpu = int(i['cpu'].replace('核',''))
                    count_cpu = count_cpu + cpu
                    mem = int(i['mem'].replace('GB',''))
                    count_mem = count_mem + mem

                jms_job = consul_kv.get_value(f"ConsulManager/jms/jobs/{vendor}/{account}")
                if jms_job == {}:
                    count_sync,interval,runtime,nextime,sync = '无','无','无','无',False
                else:
                    interval = f"{jms_job['minutes']}分钟"
                    jms_job = consul_kv.get_value(f'ConsulManager/record/jms/{vendor}/{account}')
                    runtime = jms_job.get('update')
                    count_sync = jms_job.get('count')
                    nextime = getjob(f'{vendor}/{account}/jms').next_run_time.strftime("%m.%d/%H:%M")
                    sync = True
                ecs_list.append({'vendor':vendors[vendor],'account':account,'count_linux':count_linux,
                                 'count_win':count_win,'count_mem':f'{count_mem}GB','count_cpu':f'{count_cpu}核',
                                 'count_ecs':count_ecs,'count_on':count_on,'count_off':count_off,'sync':sync,
                                 'count_sync':count_sync,'interval':interval,'runtime':runtime,'nextime':nextime})
            vendor_list = sorted(list(set([i['vendor'] for i in ecs_list])))
            account_list = sorted(list(set([i['account'] for i in ecs_list])))
            return {'code': 20000,'ecs_list':ecs_list,'vendor_list':vendor_list,'account_list':account_list}
        if stype == 'config':
            ecs_info = consul_kv.get_value('ConsulManager/jms/ecs_info')
            jms_info = consul_kv.get_value('ConsulManager/jms/jms_info')
            custom_ecs_info = consul_kv.get_value('ConsulManager/jms/custom_ecs_info')
            if ecs_info != {} and jms_info != {}:
                linuxport = ecs_info['linux'][0][0].split('/')[-1]
                linuxuid = ecs_info['linux'][-1]
                winport = ecs_info['windows'][0][0].split('/')[-1]
                winuid = ecs_info['windows'][-1]
                token = myaes.decrypt(jms_info['token'])
                custom_ecs_json = json.dumps(custom_ecs_info, indent=8) if custom_ecs_info != {} else ''
                jms_config = {'url': jms_info['url'], 'token': token, 'ver': jms_info.get('ver','V2'),
                    'linuxport': linuxport, 'linuxuid': linuxuid, 
                    'winport': winport, 'winuid': winuid, 'custom_ecs_info':custom_ecs_json}
            else:
                jms_config = {}
            return {'code': 20000, 'jms_config': jms_config}
    def post(self,stype):
        if stype == 'config':
            args = parser.parse_args()
            jms_config = args['jms_config']
            token = myaes.encrypt(jms_config['token'])
            jms_info = {'url': jms_config['url'], 'token': token, 'ver': jms_config.get('ver','V2')}
            consul_kv.put_kv('ConsulManager/jms/jms_info', jms_info)
            ecs_info = {"linux": [[f"ssh/{jms_config['linuxport']}"],jms_config['linuxuid']],
                "windows": [[f"rdp/{jms_config['winport']}"],jms_config['winuid']]}
            consul_kv.put_kv('ConsulManager/jms/ecs_info', ecs_info)
            custom_ecs_info = jms_config['custom_ecs_info']
            if custom_ecs_info != '':
                try:
                    custom_ecs_dict = json.loads(custom_ecs_info)
                    consul_kv.put_kv('ConsulManager/jms/custom_ecs_info',custom_ecs_dict)
                except Exception as e:
                    logger.error(f'{e}\n{traceback.format_exc()}')
                    return {'code': 50000, 'data': 'Json解析错误，请检查！'}
            else:
                consul_kv.put_kv('ConsulManager/jms/custom_ecs_info',{})
            return {'code': 20000, 'data': '配置完成'}
        if stype == 'switch':
            args = parser.parse_args()
            switch_dict = args['switch_dict']
            vendor = {v : k for k, v in vendors.items()}[switch_dict['vendor']]
            account = switch_dict['account']
            sync = switch_dict['sync']
            if sync:
                node = consul_kv.get_value(f'ConsulManager/jms/{vendor}/{account}/node_id')
                nodeid = node.get('node_id','')
                interval = node.get('interval',3)
                return {'code': 20000, 'interval': interval, 'nodeid': nodeid}
            else:
                deljob(f'{vendor}/{account}/jms')
                consul_kv.del_key(f'ConsulManager/jms/jobs/{vendor}/{account}')
                return {'code': 20000, 'data': f'【{vendor}/{account}】同步功能关闭！'}
        if stype == 'sync':
            args = parser.parse_args()
            jms_sync = args['jms_sync']
            vendor = {v : k for k, v in vendors.items()}[jms_sync['vendor']]
            account = jms_sync['account']
            nodeid = jms_sync['nodeid']
            interval = int(jms_sync['interval'])
            consul_kv.put_kv(f'ConsulManager/jms/{vendor}/{account}/node_id',{'node_id':nodeid,'interval':interval})

            jms_job_id = f'{vendor}/{account}/jms'
            jms_job_func = "__main__:sync_jms.run"
            jms_job_args = [vendor,account]

            addjob(jms_job_id,jms_job_func,jms_job_args,interval)
            try:
                runjob(jms_job_id)
            except Exception as e:
                deljob(jms_job_id)
                logger.error(f'{e}\n{traceback.format_exc()}\n【{vendor}/{account}】同步功能开启失败！')
                return {'code': 50000, 'data': f'【{vendor}/{account}】同步功能开启失败，请查看后端日志！'}

            jms_job_dict = {'id':jms_job_id,'func':jms_job_func,'args':jms_job_args,'minutes':interval,
                            'trigger': 'interval','replace_existing': True}
            consul_kv.put_kv(f'ConsulManager/jms/jobs/{vendor}/{account}',jms_job_dict)
            return {'code': 20000, 'data': f'【{vendor}/{account}】同步JumpServer功能开启！首次同步完成'}
api.add_resource(Jms, '/api/jms/<stype>')
