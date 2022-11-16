"""
ldap信息填写
"""
from flask import Blueprint
from flask_restful import reqparse, Resource, Api
import sys

from units.json_response import JsonResponse
from units.ldap.ldap_consul import Ldap_Consul

sys.path.append("..")
from units import token_auth, consul_kv,myaes
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
parser.add_argument('ldapusr',type=str)
parser.add_argument('allow',type=str)


class LdapView(Resource):
    """
    封装了公共返回格式
    {"code": code,"success": success, "message": msg, "data": data}
    """
    decorators = [token_auth.auth.login_required]
    def post(self,):
        args = parser.parse_args()
        Ldap_Consul.set_consul_args(**args)
        return JsonResponse(data="", code=20000, success=True, msg="添加统一认证成功")

    def get(self):
        ldap_info = consul_kv.get_value('ConsulManager/ldap/report')
        if ldap_info:
            ldap_info["password"] = myaes.decrypt(ldap_info["password"])
        else:
            ldap_info = {'port': '389', 'allow': '*'}
        return {'code': 20000, 'ldap_info': ldap_info}

    def delete(self):
        consul_kv.del_key('ConsulManager/ldap/report')
        return {'code': 20000, 'data': 'DLAP登录配置已清除！'}

api.add_resource(LdapView, '/api/ldap/config')
