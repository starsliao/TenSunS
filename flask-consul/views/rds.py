from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('rds',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_rds_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobrds_name',type=str)
parser.add_argument('checked',type=str)

class Rds(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobrds':
            jobrds = consul_kv.get_keys_list('ConsulManager/jobs')
            jobrds_list = [i.split('/jobs/')[1] for i in jobrds if '/rds/' in i]
            return {'code': 20000,'jobrds':jobrds_list}
        elif stype == 'rds_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/rds/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'rdsrules':
            return gen_config.get_rdsrules()
        elif stype == 'cstrdsconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_rds_config = consul_kv.get_value(f'ConsulManager/assets/sync_rds_custom/{iid}')
            cst_rds_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_rds_config and cst_rds_config['ip'] != '':
                cst_rds_config['ipswitch'] = True
            if 'port' in cst_rds_config and cst_rds_config['port'] != '':
                cst_rds_config['portswitch'] = True
            return {'code': 20000, 'cst_rds': cst_rds_config}
        elif stype == 'cstrdslist':
            args = parser.parse_args()
            jobrds_name = args['jobrds_name']
            checked = args['checked']
            cst_rds_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_rds_custom/')
            cst_rds_keylist = [k.split('/')[-1] for k,v in cst_rds_dict.items() if v != {}]
            rds_info = consul_kv.get_res_services(jobrds_name)
            if checked == 'false':
                return rds_info
            else:
                cst_rds_list = [i for i in rds_info['res_list'] if i['iid'] in cst_rds_keylist]
                return {'code': 20000, 'res_list': cst_rds_list}
                
    def post(self, stype):
        if stype == 'rdspconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.rds_config(services_dict['jobrds_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstrds':
            args = parser.parse_args()
            cst_rds_dict = args['cst_rds_dict']
            consul_rds_cst = {}
            iid = cst_rds_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_rds_dict['portswitch'] and cst_rds_dict['port'] != '':
                    consul_rds_cst['port'] = int(cst_rds_dict['port'])
                    sid_dict['Port'] = consul_rds_cst['port']
                if cst_rds_dict['ipswitch'] and cst_rds_dict['ip'] != '':
                    consul_rds_cst['ip'] = cst_rds_dict['ip']
                    sid_dict['Address'] = consul_rds_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_rds_custom/{iid}',consul_rds_cst)
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

api.add_resource(Rds, '/api/rds/<stype>')
