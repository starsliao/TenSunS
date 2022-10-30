# -*- coding:utf-8 -*-
import requests,json,sys,os
from base64 import b64decode
from config import consul_token,consul_url
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#import myaes

headers = {'X-Consul-Token': consul_token}

def get_value(path):
    url = f'{consul_url}/kv/{path}?raw'
    response = requests.get(url, headers=headers)
    response.encoding='utf-8'
    if response.status_code == 200:
        return response.json()
    else:
        return {}
def get_kv_dict(path):
    url = f'{consul_url}/kv/{path}?recurse'
    response = requests.get(url, headers=headers)
    response.encoding='utf-8'
    if response.status_code == 200 and response.text != '':
        info = response.json()
        kv_dict = {i['Key']:json.loads(b64decode(i['Value']).decode('utf-8')) for i in info if i['Value'] != None}
        if kv_dict != {}:
            return kv_dict
        else:
            return {}
    else:
        return {}
def get_keys_list(path):
    url = f'{consul_url}/kv/{path}?keys'
    response = requests.get(url, headers=headers)
    response.encoding='utf-8'
    if response.status_code == 200:
        return response.json()
    else:
        return []
def put_kv(path,value):
    url = f'{consul_url}/kv/{path}'
    payload = json.dumps(value,ensure_ascii=False).encode("utf-8")
    response = requests.put(url, headers=headers, data=payload)
    return response.json()

def del_key(path):
    url = f'{consul_url}/kv/{path}'
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
def del_key_all(path):
    url = f'{consul_url}/kv/{path}?recurse=true'
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_res_services(job_id):
    cloud,account,itype,region = job_id.split('/')
    service = f'{cloud}_{account}_{itype}'
    region = f'and "{region}" in Tags'
    url = f'{consul_url}/agent/services?filter=Service == "{service}" {region}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        res_list = [i['Meta'] for i in info.values()]
        return {'code': 20000,'res_list': res_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}
 
def get_services_meta(services_name):
    url = f'{consul_url}/agent/services?filter=Service == "{services_name}"'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        ecs_list = [i['Meta'] for i in info.values()]
        return {'code': 20000,'ecs_list': ecs_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def get_aksk(cloud,account):
    import myaes
    aksk_dict = get_value(f'ConsulManager/assets/{cloud}/aksk/{account}')
    ak = myaes.decrypt(aksk_dict['ak'])
    sk = myaes.decrypt(aksk_dict['sk'])
    return ak, sk

def put_aksk(cloud,account,ak,sk):
    import myaes
    encrypt_aksk = {'ak': myaes.encrypt(ak), 'sk': myaes.encrypt(sk)}
    return put_kv(f'ConsulManager/assets/{cloud}/aksk/{account}', encrypt_aksk)
