#!/usr/bin/python3
import requests,json
from units import consul_kv
from config import consul_token,consul_url,vendors,regions
headers = {'X-Consul-Token': consul_token}
geturl = f'{consul_url}/agent/services'
delurl = f'{consul_url}/agent/service/deregister'
puturl = f'{consul_url}/agent/service/register'
def w2consul(vendor,account,region,ecs_dict):
    service_name = f'{vendor}_{account}_ecs'
    params = {'filter': f'Service == "{service_name}" and "{region}" in Tags and Meta.account == "{account}"'}
    try:
        consul_ecs_iid_list = requests.get(geturl, headers=headers, params=params).json().keys()
    except:
        consul_ecs_iid_list = []
        
    #在consul中删除云厂商不存在的ecs
    for del_ecs in [x for x in consul_ecs_iid_list if x not in ecs_dict.keys()]:
        dereg = requests.put(f'{delurl}/{del_ecs}', headers=headers)
        if dereg.status_code == 200:
            print({"code": 20000,"data": f"{account}-删除成功！"}, flush=True)
        else:
            print({"code": 50000,"data": f'{dereg.status_code}:{dereg.text}'}, flush=True)
    off,on = 0,0
    for k,v in ecs_dict.items():
        iid = k
        #去除consul中关机的ecs
        if v['status'] in ['SHUTOFF','Stopped','STOPPED']:
            off = off + 1
            if k in consul_ecs_iid_list:
                dereg = requests.put(f'{delurl}/{iid}', headers=headers)
                if dereg.status_code == 200:
                    print({"code": 20000,"data": f"{account}-删除成功！"}, flush=True)
                else:
                    print({"code": 50000,"data": f'{dereg.status_code}:{dereg.text}'}, flush=True)
        else:
            on = on + 1
            custom_ecs = consul_kv.get_value(f'ConsulManager/assets/sync_ecs_custom/{iid}')
            port = custom_ecs.get('port')
            ip = custom_ecs.get('ip')
            if port == None:
                port = 9100 if v['ostype'] == 'linux' else 9182
            if ip == None:
                ip = v['ip'] if isinstance(v['ip'],list) is False else v['ip'][0]
            instance = f'{ip}:{port}'
            data = {
                'id': iid,
                'name': service_name,
                'Address': ip,
                'port': port,
                'tags': [v['ostype'],region],
                'Meta': {
                    'iid': iid,
                    'name': v['name'],
                    'region': regions[vendor].get(region,'未找到'),
                    'group': v['group'],
                    'instance': instance,
                    'account': account,
                    'vendor': vendors.get(vendor,'未找到'),
                    'os': v['ostype'],
                    'cpu': v['cpu'],
                    'mem': v['mem'],
                    'exp': v['exp']
                },
                "check": {
                    "tcp": f"{ip}:{port}",
                    "interval": "60s"
                }
            }
            if vendor == 'alicloud' and v['ecstag'] != []:
                ecstag_dict = {}
                for ecstag in v['ecstag']:
                    if ecstag['TagKey'].encode().isalnum():
                        ecstag_dict[ecstag['TagKey']] = ecstag['TagValue']
                data['Meta'].update(ecstag_dict)
            reg = requests.put(puturl, headers=headers, data=json.dumps(data))
            if reg.status_code == 200:
                pass
                #print({f"{account}:code": 20000,"data": "增加成功！"}, flush=True)
            else:
                print({f"{account}:code": 50000,"data": f'{reg.status_code}:{reg.text}'}, flush=True)
                #return {"code": 50000,"data": f'{reg.status_code}:{reg.text}'}
    return off,on
