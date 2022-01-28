#!/usr/bin/env python3
from flask import Flask
from flask_restful import reqparse, Api, Resource
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer
#from flask_cors import CORS
import requests,json,os

app = Flask(__name__)
#CORS(app)
auth = HTTPTokenAuth()
api = Api(app)

consul_token = os.environ.get('consul_token')
consul_url = os.environ.get('consul_url')
admin_passwd = os.environ.get('admin_passwd')
secret_key = os.environ.get('secret_key',consul_token)

headers = {'X-Consul-Token': consul_token}
s = TimedJSONWebSignatureSerializer(secret_key)

@auth.verify_token
def verify_token(token):
    try:
        data = s.loads(token)
    except:
        return False
    return True

def get_all_list(module,company,project,env):
    module = f'and Meta.module=="{module}"' if module != '' else f'and Meta.module != ""'
    company = f'and Meta.company=="{company}"' if company != '' else f'and Meta.company != ""'
    project = f'and Meta.project=="{project}"' if project != '' else f'and Meta.project != ""'
    env = f'and Meta.env=="{env}"' if env != '' else f'and Meta.env != ""'
    url = f'{consul_url}/agent/services?filter=Service == blackbox_exporter {module} {company} {project} {env}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        module_list = sorted(list(set([i['module'] for i in all_list])))
        company_list = sorted(list(set([i['company'] for i in all_list])))
        project_list = sorted(list(set([i['project'] for i in all_list])))
        env_list = sorted(list(set([i['env'] for i in all_list])))
        return {'code': 20000,'all_list':all_list,'module_list':module_list,
                'company_list':company_list,'project_list':project_list,'env_list':env_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def get_service():
    response = requests.get(f'{consul_url}/agent/services?filter=Service == blackbox_exporter', headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        module_list = sorted(list(set([i['module'] for i in all_list])))
        company_list = sorted(list(set([i['company'] for i in all_list])))
        project_list = sorted(list(set([i['project'] for i in all_list])))
        env_list = sorted(list(set([i['env'] for i in all_list])))
        return {'code': 20000,'all_list':all_list,'module_list':module_list,
                'company_list':company_list,'project_list':project_list,'env_list':env_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def add_service(module,company,project,env,name,instance):
    sid = f"{module}/{company}/{project}/{env}@{name}"
    data = {
            "id": sid,
            "name": 'blackbox_exporter',
            "tags": [module],
            "Meta": {'module':module,'company':company,'project':project,'env':env,'name':name,'instance':instance}
           }
    reg = requests.put(f'{consul_url}/agent/service/register', headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】增加成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}
def del_service(module,company,project,env,name):
    sid = f"{module}/{company}/{project}/{env}@{name}"
    reg = requests.put(f'{consul_url}/agent/service/deregister/{sid}', headers=headers)
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】删除成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

parser = reqparse.RequestParser()
parser.add_argument('module',type=str)
parser.add_argument('company',type=str)
parser.add_argument('project',type=str)
parser.add_argument('env',type=str)
parser.add_argument('name',type=str)
parser.add_argument('instance',type=str)
parser.add_argument('username',type=str)
parser.add_argument('password',type=str)
parser.add_argument('del_dict',type=dict)
parser.add_argument('up_dict',type=dict)

class User(Resource):
    @auth.login_required
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

class GetAllList(Resource):
    @auth.login_required
    def get(self):
        args = parser.parse_args()
        return get_all_list(args['module'],args['company'],args['project'],args['env'])

class ConsulApi(Resource):
    decorators = [auth.login_required]
    def get(self):
        return get_service()
    def post(self):
        args = parser.parse_args()
        return add_service(args['module'],args['company'],args['project'],args['env'],args['name'],args['instance'])
    def put(self):
        args = parser.parse_args()
        del_dict = args['del_dict']
        up_dict = args['up_dict']
        resp_del = del_service(del_dict['module'],del_dict['company'],
                               del_dict['project'],del_dict['env'],del_dict['name'])
        resp_add = add_service(up_dict['module'],up_dict['company'],up_dict['project'],
                               up_dict['env'],up_dict['name'],up_dict['instance'])
        if resp_del["code"] == 20000 and resp_add["code"] == 20000:
            return {"code": 20000, "data": f"更新成功！"}
        else:
            return {"code": 50000, "data": f"更新失败！"}
    def delete(self):
        args = parser.parse_args()
        return del_service(args['module'],args['company'],args['project'],args['env'],args['name'])

api.add_resource(GetAllList,'/api/consul/alllist')
api.add_resource(ConsulApi, '/api/consul/service')
api.add_resource(User, '/api/user/<user_opt>')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2026)
