"""
ldap信息填写
"""
from flask import Blueprint
from flask_restful import reqparse, Resource, Api
import sys

from units.json_response import JsonResponse
from units.ldap.ldap_consul import Ldap_Consul

sys.path.append("..")
from units import token_auth, consul_kv
from itsdangerous import TimedJSONWebSignatureSerializer

secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk']
s = TimedJSONWebSignatureSerializer(secret_key,expires_in=28800)

blueprint = Blueprint('ldap',__name__)
api = Api(blueprint)
parser = reqparse.RequestParser()

parser.add_argument('ldap_url',type=str)
parser.add_argument('password',type=str)
parser.add_argument('port',type=str)
parser.add_argument('rule',type=str)




class LdapView(Resource):
    """
    封装了公共返回格式
    {"code": code,"success": success, "message": msg, "data": data}
    """
    def post(self,):
        args = parser.parse_args()
        Ldap_Consul.set_consul_args(**args)
        return JsonResponse(data="", code=20000, success=True, msg="添加统一认证成功")

api.add_resource(LdapView, '/api/ldap/config')
