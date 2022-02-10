from flask import Blueprint
from flask_restful import reqparse, Resource, Api
import sys
sys.path.append("..")
from units import token_auth,consul_manager

blueprint = Blueprint('consul',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('service_name',type=str)
parser.add_argument('sid',type=str)
parser.add_argument('instance_dict',type=dict)

class ConsulApi(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        if stype == 'services':
            return consul_manager.get_services()
        elif stype == 'services_name':
            return consul_manager.get_services_nameonly()
        elif stype == 'instances':
            args = parser.parse_args()
            return consul_manager.get_instances(args['service_name'])
        elif stype == 'hosts':
            return consul_manager.get_hosts()

    def post(self, stype):
        if stype == 'sid':
            args = parser.parse_args()
            return consul_manager.add_instance(args['instance_dict'])

    def put(self, stype):
        if stype == 'sid':
            args = parser.parse_args()
            resp_del = consul_manager.del_instance(args['sid'])
            resp_add = consul_manager.add_instance(args['instance_dict'])
            if resp_del["code"] == 20000 and resp_add["code"] == 20000:
                return {"code": 20000, "data": f"更新成功！"}
            else:
                return {"code": 50000, "data": f"更新失败！"}

    def delete(self, stype):
        if stype == 'sid':
            args = parser.parse_args()
            return consul_manager.del_instance(args['sid'])

api.add_resource(ConsulApi, '/api/consul/<stype>')
