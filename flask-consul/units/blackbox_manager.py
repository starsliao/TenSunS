import requests,json
import sys 
sys.path.append("..") 
from config import consul_token,consul_url

headers = {'X-Consul-Token': consul_token}

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
