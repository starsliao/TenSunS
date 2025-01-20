from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('mongodb',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_mongodb_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobmongodb_name',type=str)
parser.add_argument('checked',type=str)

class Mongodb(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobmongodb':
            jobmongodb = consul_kv.get_keys_list('ConsulManager/jobs')
            jobmongodb_list = [i.split('/jobs/')[1] for i in jobmongodb if '/mongodb/' in i]
            return {'code': 20000,'jobmongodb':jobmongodb_list}
        elif stype == 'mongodb_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/mongodb/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'mongodbrules':
            return gen_config.get_mongodbrules()
        elif stype == 'cstmongodbconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_mongodb_config = consul_kv.get_value(f'ConsulManager/assets/sync_mongodb_custom/{iid}')
            cst_mongodb_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_mongodb_config and cst_mongodb_config['ip'] != '':
                cst_mongodb_config['ipswitch'] = True
            if 'port' in cst_mongodb_config and cst_mongodb_config['port'] != '':
                cst_mongodb_config['portswitch'] = True
            return {'code': 20000, 'cst_mongodb': cst_mongodb_config}
        elif stype == 'cstmongodblist':
            args = parser.parse_args()
            jobmongodb_name = args['jobmongodb_name']
            checked = args['checked']
            cst_mongodb_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_mongodb_custom/')
            cst_mongodb_keylist = [k.split('/')[-1] for k,v in cst_mongodb_dict.items() if v != {}]
            mongodb_info = consul_kv.get_res_services(jobmongodb_name)
            if checked == 'false':
                return mongodb_info
            else:
                cst_mongodb_list = [i for i in mongodb_info['res_list'] if i['iid'] in cst_mongodb_keylist]
                return {'code': 20000, 'res_list': cst_mongodb_list}
                
    def post(self, stype):
        if stype == 'mongodbpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.mongodb_config(services_dict['jobmongodb_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstmongodb':
            args = parser.parse_args()
            cst_mongodb_dict = args['cst_mongodb_dict']
            consul_mongodb_cst = {}
            iid = cst_mongodb_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_mongodb_dict['portswitch'] and cst_mongodb_dict['port'] != '':
                    consul_mongodb_cst['port'] = int(cst_mongodb_dict['port'])
                    sid_dict['Port'] = consul_mongodb_cst['port']
                if cst_mongodb_dict['ipswitch'] and cst_mongodb_dict['ip'] != '':
                    consul_mongodb_cst['ip'] = cst_mongodb_dict['ip']
                    sid_dict['Address'] = consul_mongodb_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_mongodb_custom/{iid}',consul_mongodb_cst)
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

api.add_resource(Mongodb, '/api/mongodb/<stype>')
