from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('polardb',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_polardb_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobpolardb_name',type=str)
parser.add_argument('checked',type=str)

class Polardb(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobpolardb':
            jobpolardb = consul_kv.get_keys_list('ConsulManager/jobs')
            jobpolardb_list = [i.split('/jobs/')[1] for i in jobpolardb if '/polardb/' in i]
            return {'code': 20000,'jobpolardb':jobpolardb_list}
        elif stype == 'polardb_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/polardb/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'polardbrules':
            return gen_config.get_polardbrules()
        elif stype == 'cstpolardbconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_polardb_config = consul_kv.get_value(f'ConsulManager/assets/sync_polardb_custom/{iid}')
            cst_polardb_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_polardb_config and cst_polardb_config['ip'] != '':
                cst_polardb_config['ipswitch'] = True
            if 'port' in cst_polardb_config and cst_polardb_config['port'] != '':
                cst_polardb_config['portswitch'] = True
            return {'code': 20000, 'cst_polardb': cst_polardb_config}
        elif stype == 'cstpolardblist':
            args = parser.parse_args()
            jobpolardb_name = args['jobpolardb_name']
            checked = args['checked']
            cst_polardb_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_polardb_custom/')
            cst_polardb_keylist = [k.split('/')[-1] for k,v in cst_polardb_dict.items() if v != {}]
            polardb_info = consul_kv.get_res_services(jobpolardb_name)
            if checked == 'false':
                return polardb_info
            else:
                cst_polardb_list = [i for i in polardb_info['res_list'] if i['iid'] in cst_polardb_keylist]
                return {'code': 20000, 'res_list': cst_polardb_list}
                
    def post(self, stype):
        if stype == 'polardbpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.polardb_config(services_dict['jobpolardb_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstpolardb':
            args = parser.parse_args()
            cst_polardb_dict = args['cst_polardb_dict']
            consul_polardb_cst = {}
            iid = cst_polardb_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_polardb_dict['portswitch'] and cst_polardb_dict['port'] != '':
                    consul_polardb_cst['port'] = int(cst_polardb_dict['port'])
                    sid_dict['Port'] = consul_polardb_cst['port']
                if cst_polardb_dict['ipswitch'] and cst_polardb_dict['ip'] != '':
                    consul_polardb_cst['ip'] = cst_polardb_dict['ip']
                    sid_dict['Address'] = consul_polardb_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_polardb_custom/{iid}',consul_polardb_cst)
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

api.add_resource(Polardb, '/api/polardb/<stype>')
