import requests,json
import sys 
sys.path.append("..") 
from config import consul_token,consul_url

headers = {'X-Consul-Token': consul_token}

def get_sid(iid):
    url = f'{consul_url}/agent/service/{iid}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        return {'code': 20000,'instance':info}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def del_sid(iid):
    reg = requests.put(f'{consul_url}/agent/service/deregister/{iid}', headers=headers)
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{iid}】删除成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{iid}】{reg.text}"}

def add_sid(instance_dict):
    reg = requests.put(f'{consul_url}/agent/service/register', headers=headers, data=json.dumps(instance_dict))
    if reg.status_code == 200:
        return {"code": 20000, "data": f"增加成功！"}
    else:
        print(f"{reg.status_code}:{reg.text}")
        return {"code": 50000, "data": f"{reg.status_code}:{reg.text}"}

