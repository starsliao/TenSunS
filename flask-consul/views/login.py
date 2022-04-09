from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from itsdangerous import TimedJSONWebSignatureSerializer
import sys
sys.path.append("..")
from config import admin_passwd
from units import token_auth, consul_kv
secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk']
s = TimedJSONWebSignatureSerializer(secret_key)

blueprint = Blueprint('login',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('username',type=str)
parser.add_argument('password',type=str)

class User(Resource):
    @token_auth.auth.login_required
    def get(self, user_opt):
        if user_opt == 'info':
            return {
                    "code": 20000,
                    "data": {"roles": ["admin"],"name": "admin","avatar": "/sl.png"}}
    def post(self, user_opt):
        if user_opt == 'login':
            args = parser.parse_args()
            username = args.get('username')
            password = args.get('password')
            if password == admin_passwd:
                token = str(s.dumps(admin_passwd),encoding="utf-8")
                return {"code": 20000,"data": {"token": "Bearer " + token}}
            else:
                return {"code": 40000, "data": "密码错误！"}
        elif user_opt == 'logout':
            return {"code": 20000,"data": "success"}

api.add_resource(User, '/api/user/<user_opt>')
