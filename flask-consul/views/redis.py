from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('redis',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_redis_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobredis_name',type=str)
parser.add_argument('checked',type=str)

class Redis(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobredis':
            jobredis = consul_kv.get_keys_list('ConsulManager/jobs')
            jobredis_list = [i.split('/jobs/')[1] for i in jobredis if '/redis/' in i]
            return {'code': 20000,'jobredis':jobredis_list}
        elif stype == 'redis_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/redis/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'redisrules':
            return gen_config.get_redisrules()
        elif stype == 'cstredisconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_redis_config = consul_kv.get_value(f'ConsulManager/assets/sync_redis_custom/{iid}')
            cst_redis_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_redis_config and cst_redis_config['ip'] != '':
                cst_redis_config['ipswitch'] = True
            if 'port' in cst_redis_config and cst_redis_config['port'] != '':
                cst_redis_config['portswitch'] = True
            return {'code': 20000, 'cst_redis': cst_redis_config}
        elif stype == 'cstredislist':
            args = parser.parse_args()
            jobredis_name = args['jobredis_name']
            checked = args['checked']
            cst_redis_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_redis_custom/')
            cst_redis_keylist = [k.split('/')[-1] for k,v in cst_redis_dict.items() if v != {}]
            redis_info = consul_kv.get_res_services(jobredis_name)
            if checked == 'false':
                return redis_info
            else:
                cst_redis_list = [i for i in redis_info['res_list'] if i['iid'] in cst_redis_keylist]
                return {'code': 20000, 'res_list': cst_redis_list}
                
    def post(self, stype):
        if stype == 'redispconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.redis_config(services_dict['jobredis_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstredis':
            args = parser.parse_args()
            cst_redis_dict = args['cst_redis_dict']
            consul_redis_cst = {}
            iid = cst_redis_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_redis_dict['portswitch'] and cst_redis_dict['port'] != '':
                    consul_redis_cst['port'] = int(cst_redis_dict['port'])
                    sid_dict['Port'] = consul_redis_cst['port']
                if cst_redis_dict['ipswitch'] and cst_redis_dict['ip'] != '':
                    consul_redis_cst['ip'] = cst_redis_dict['ip']
                    sid_dict['Address'] = consul_redis_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_redis_custom/{iid}',consul_redis_cst)
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

api.add_resource(Redis, '/api/redis/<stype>')
