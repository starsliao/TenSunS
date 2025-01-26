from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('clickhouse',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_clickhouse_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobclickhouse_name',type=str)
parser.add_argument('checked',type=str)

class Clickhouse(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobclickhouse':
            jobclickhouse = consul_kv.get_keys_list('ConsulManager/jobs')
            jobclickhouse_list = [i.split('/jobs/')[1] for i in jobclickhouse if '/clickhouse/' in i]
            return {'code': 20000,'jobclickhouse':jobclickhouse_list}
        elif stype == 'clickhouse_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/clickhouse/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'clickhouserules':
            return gen_config.get_clickhouserules()
        elif stype == 'cstclickhouseconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_clickhouse_config = consul_kv.get_value(f'ConsulManager/assets/sync_clickhouse_custom/{iid}')
            cst_clickhouse_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_clickhouse_config and cst_clickhouse_config['ip'] != '':
                cst_clickhouse_config['ipswitch'] = True
            if 'port' in cst_clickhouse_config and cst_clickhouse_config['port'] != '':
                cst_clickhouse_config['portswitch'] = True
            return {'code': 20000, 'cst_clickhouse': cst_clickhouse_config}
        elif stype == 'cstclickhouselist':
            args = parser.parse_args()
            jobclickhouse_name = args['jobclickhouse_name']
            checked = args['checked']
            cst_clickhouse_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_clickhouse_custom/')
            cst_clickhouse_keylist = [k.split('/')[-1] for k,v in cst_clickhouse_dict.items() if v != {}]
            clickhouse_info = consul_kv.get_res_services(jobclickhouse_name)
            if checked == 'false':
                return clickhouse_info
            else:
                cst_clickhouse_list = [i for i in clickhouse_info['res_list'] if i['iid'] in cst_clickhouse_keylist]
                return {'code': 20000, 'res_list': cst_clickhouse_list}
                
    def post(self, stype):
        if stype == 'clickhousepconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.clickhouse_config(services_dict['jobclickhouse_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstclickhouse':
            args = parser.parse_args()
            cst_clickhouse_dict = args['cst_clickhouse_dict']
            consul_clickhouse_cst = {}
            iid = cst_clickhouse_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_clickhouse_dict['portswitch'] and cst_clickhouse_dict['port'] != '':
                    consul_clickhouse_cst['port'] = int(cst_clickhouse_dict['port'])
                    sid_dict['Port'] = consul_clickhouse_cst['port']
                if cst_clickhouse_dict['ipswitch'] and cst_clickhouse_dict['ip'] != '':
                    consul_clickhouse_cst['ip'] = cst_clickhouse_dict['ip']
                    sid_dict['Address'] = consul_clickhouse_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_clickhouse_custom/{iid}',consul_clickhouse_cst)
                del sid_dict['Weights']
                del sid_dict['ContentHash']
                del sid_dict['Datacenter']
                sid_dict['name'] = sid_dict.pop('Service')
                sid_dict['Meta']['instance'] = f"{sid_dict['Address']}:{sid_dict['Port']}"
                sid_dict["check"] = { "tcp": sid_dict['Meta']['instance'],"interval": "60s" }
                consul_svc.del_sid(iid)
                consul_svc.add_sid(sid_dict)
                return {'code': 20000, 'data': '自定义实例信息修改成功！'}
            except Exception as e:
                logger.error(f'{e}\n{traceback.format_exc()}')
                return {'code': 50000, "data": '提交自定义实例信息格式错误！'}

api.add_resource(Clickhouse, '/api/clickhouse/<stype>')
