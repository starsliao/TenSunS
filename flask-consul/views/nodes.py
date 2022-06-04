from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config

blueprint = Blueprint('nodes',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)

class Nodes(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'group':
            cloud,account,itype = job_id.split('/')
            group_dict = consul_kv.get_value(f'ConsulManager/assets/{cloud}/group/{account}')
            group_list = [{'gid':k,'gname':v}for k,v in group_dict.items()]
            return {'code': 20000,'group':group_list}
        elif stype == 'ecs':
            if job_id == '':
                return {'code': 20000,'ecs_list': [] }
            else:
                return consul_kv.get_ecs_services(job_id) 
        elif stype == 'jobecs':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/ecs/' in i]
            return {'code': 20000,'jobecs':jobecs_list}
        elif stype == 'ecs_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/ecs/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'rules':
            return gen_config.get_rules()
    def post(self, stype):
        if stype == 'config':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.ecs_config(services_dict['services_list'],services_dict['ostype_list'])
api.add_resource(Nodes, '/api/nodes/<stype>')
