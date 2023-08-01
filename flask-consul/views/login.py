from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from itsdangerous import TimedJSONWebSignatureSerializer
from werkzeug.datastructures import FileStorage
import sys,base64,traceback
sys.path.append("..")
from config import admin_passwd
from units import token_auth, consul_kv
from units.ldap.LdapUser import Ldap
from units.config_log import *
secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk']
s = TimedJSONWebSignatureSerializer(secret_key,expires_in=28800)

blueprint = Blueprint('login',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('username',type=str)
parser.add_argument('password',type=str)
parser.add_argument('title',type=str)
parser.add_argument('height',type=str)
parser.add_argument('ldap',type=str)
parser.add_argument('file',type=FileStorage, location="files", help="File is wrong.")

class Logo(Resource):
    @token_auth.auth.login_required
    def post(self, logo_opt):
        if logo_opt == 'nologo':
            height = parser.parse_args().get("height")
            height = '450' if height == "" else height
            consul_kv.put_kv('ConsulManager/img/logoheight',height)
            consul_kv.put_kv('ConsulManager/img/biglogo','R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
            consul_kv.put_kv('ConsulManager/img/isbig',True)
            return {"code": 20000, "data": "设置成功！"}
        elif logo_opt == 'title':
            title = parser.parse_args().get("title")
            consul_kv.put_kv('ConsulManager/img/logintitle',title)
            return {"code": 20000, "data": "设置成功！"}
        elif logo_opt == 'rebig':
            consul_kv.del_key('ConsulManager/img/biglogo')
            consul_kv.put_kv('ConsulManager/img/isbig',True)
            return {"code": 20000, "data": "设置成功！"}
        elif logo_opt == 'resmall':
            consul_kv.del_key('ConsulManager/img/smallogo')
            consul_kv.put_kv('ConsulManager/img/isbig',False)
            return {"code": 20000, "data": "设置成功！"}
        elif logo_opt == 'rebgimg':
            consul_kv.del_key('ConsulManager/img/bgimg')
            return {"code": 20000, "data": "设置成功！"}
        elif logo_opt == 'retitle':
            consul_kv.del_key('ConsulManager/img/logintitle')
            return {"code": 20000, "data": "设置成功！"}

        elif logo_opt == 'biglogo':
            consul_kv_path = 'ConsulManager/img/biglogo'
            consul_kv.put_kv('ConsulManager/img/isbig',True)
        elif logo_opt == 'smallogo':
            consul_kv_path = 'ConsulManager/img/smallogo'
            consul_kv.put_kv('ConsulManager/img/isbig',False)
        elif logo_opt == 'bgimg':
            consul_kv_path = 'ConsulManager/img/bgimg'

        img = parser.parse_args().get("file")
        try:
            b64img = base64.b64encode(img.read()).decode('utf-8')
            consul_kv.put_kv(consul_kv_path,b64img)
            return {"code": 20000, "data": "LOGO设置成功！"}
        except Exception as e:
            logger.error(f"【logo】导入失败,{e}\n{traceback.format_exc()}")
            return {"code": 50000, "data": "LOGO导入失败！"}
    def get(self, logo_opt):
        if logo_opt == 'logo':
            isbig = consul_kv.get_value('ConsulManager/img/isbig')
            if isbig:
                consul_kv_path = 'ConsulManager/img/biglogo'
            else:
                consul_kv_path = 'ConsulManager/img/smallogo'
            b64logo = consul_kv.get_value(consul_kv_path)
            if b64logo:
                if b64logo == 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7':
                    logoheight = consul_kv.get_value('ConsulManager/img/logoheight')
                    return {"code": 20000, "isbig": isbig, "data": 'data:image/png;base64,' + b64logo, "logoheight": logoheight}
                else:
                    return {"code": 20000, "isbig": isbig, "data": 'data:image/png;base64,' + b64logo}
            else:
                return {"code": 20000, "isbig": isbig, "data": 'default'}
        elif logo_opt == 'title':
            title = consul_kv.get_value('ConsulManager/img/logintitle')
            if title:
                return {"code": 20000, "data": title}
            else:
                return {"code": 20000, "data": 'default'}
        elif logo_opt == 'bgimg':
            bgimg = consul_kv.get_value('ConsulManager/img/bgimg')
            if bgimg:
                return {"code": 20000, "data": 'data:image/png;base64,' + bgimg}
            else:
                return {"code": 20000, "data": 'default'}

class User(Resource):
    @token_auth.auth.login_required
    def get(self, user_opt):
        if user_opt == 'info':
            return {
                    "code": 20000,
                    "data": {"roles": ["admin"],"name": "admin","avatar": "/sl.png"}}
    def post(self, user_opt):
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        #ldap = args.get('ldap')
        ldap = False if username == 'admin' else 'True'
        #ldap认证
        if user_opt == 'login' and ldap == "True":
            logger.info("ldap")
            ldap_obj = Ldap()
            ldap_result = ldap_obj.authpass(username,password)
            if ldap_result == 1:
                token = str(s.dumps(admin_passwd), encoding="utf-8")
                return {"code": 20000, "data": {"token": "Bearer " + token,"username":username}}
            elif ldap_result == 0:
                return {"code": 40000, "data": "LDAP未开启。"}
            elif ldap_result == 2:
                return {"code": 40000, "data": "该LDAP用户不在白名单内。"}
            else:
                return {"code": 40000, "data": "LDAP用户密码错误！"}
        else:
            if user_opt == 'login':
                logger.info("非ldap")
                if password == admin_passwd:
                    token = str(s.dumps(admin_passwd),encoding="utf-8")
                    return {"code": 20000,"data": {"token": "Bearer " + token,"username":username}}
                else:
                    return {"code": 40000, "data": "密码错误！"}

            elif user_opt == 'logout':
                return {"code": 20000,"data": "success"}

api.add_resource(User, '/api/user/<user_opt>')
api.add_resource(Logo,'/api/login/<logo_opt>')

