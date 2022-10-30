from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc

blueprint = Blueprint('nodes',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_ecs_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobecs_name',type=str)
parser.add_argument('checked',type=str)

class Nodes(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'group':
            cloud,account,itype = job_id.split('/')
            group_dict = consul_kv.get_value(f'ConsulManager/assets/{cloud}/group/{account}')
            group_list = [{'gid':k,'gname':v}for k,v in group_dict.items()]
            return {'code': 20000,'group':group_list}
        elif stype == 'res':
            if job_id == '' or job_id == None:
                return {'code': 20000,'res_list': [] }
            else:
                return consul_kv.get_res_services(job_id) 
        elif stype == 'jobecs':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/ecs/' in i]
            return {'code': 20000,'jobecs':jobecs_list}
        elif stype == 'jobrds':
            jobrds = consul_kv.get_keys_list('ConsulManager/jobs')
            jobrds_list = [i.split('/jobs/')[1] for i in jobrds if '/rds/' in i]
            return {'code': 20000,'jobrds':jobrds_list}
        elif stype == 'ecs_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/ecs/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'rds_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/rds/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'rules':
            return gen_config.get_rules()
        elif stype == 'rdsrules':
            return gen_config.get_rdsrules()
        elif stype == 'cstecsconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_ecs_config = consul_kv.get_value(f'ConsulManager/assets/sync_ecs_custom/{iid}')
            cst_ecs_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_ecs_config and cst_ecs_config['ip'] != '':
                cst_ecs_config['ipswitch'] = True
            if 'port' in cst_ecs_config and cst_ecs_config['port'] != '':
                cst_ecs_config['portswitch'] = True
            return {'code': 20000, 'cst_ecs': cst_ecs_config}
        elif stype == 'cstecslist':
            args = parser.parse_args()
            jobecs_name = args['jobecs_name']
            checked = args['checked']
            cst_ecs_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_ecs_custom/')
            cst_ecs_keylist = [k.split('/')[-1] for k,v in cst_ecs_dict.items() if v != {}]
            ecs_info = consul_kv.get_res_services(jobecs_name)
            if checked == 'false':
                return ecs_info
            else:
                cst_ecs_list = [i for i in ecs_info['res_list'] if i['iid'] in cst_ecs_keylist]
                return {'code': 20000, 'res_list': cst_ecs_list}
                
    def post(self, stype):
        if stype == 'config':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.ecs_config(services_dict['services_list'],services_dict['ostype_list'])
        elif stype == 'rdspconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.rds_config(services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstecs':
            args = parser.parse_args()
            cst_ecs_dict = args['cst_ecs_dict']
            consul_ecs_cst = {}
            iid = cst_ecs_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_ecs_dict['portswitch'] and cst_ecs_dict['port'] != '':
                    consul_ecs_cst['port'] = int(cst_ecs_dict['port'])
                    sid_dict['Port'] = consul_ecs_cst['port']
                if cst_ecs_dict['ipswitch'] and cst_ecs_dict['ip'] != '':
                    consul_ecs_cst['ip'] = cst_ecs_dict['ip']
                    sid_dict['Address'] = consul_ecs_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_ecs_custom/{iid}',consul_ecs_cst)
                del sid_dict['TaggedAddresses']
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
                print(e,flush=True)
                return {'code': 50000, "data": '提交自定义实例信息格式错误！'}


api.add_resource(Nodes, '/api/nodes/<stype>')
