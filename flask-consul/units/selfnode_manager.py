import requests,json,re
#import sys
#sys.path.append("..")
from config import consul_token,consul_url
from units.config_log import *

headers = {'X-Consul-Token': consul_token}

def get_all_list(vendor,account,region,group):
    vendor = f'and Meta.vendor=="{vendor}"' if vendor != '' else f'and Meta.vendor != ""'
    account = f'and Meta.account=="{account}"' if account != '' else f'and Meta.account != ""'
    region = f'and Meta.region=="{region}"' if region != '' else f'and Meta.region != ""'
    group = f'and Meta.group=="{group}"' if group != '' else f'and Meta.group != ""'
    url = f'{consul_url}/agent/services?filter=Service == selfnode_exporter {vendor} {account} {region} {group}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        vendor_list = sorted(list(set([i['vendor'] for i in all_list])))
        account_list = sorted(list(set([i['account'] for i in all_list])))
        region_list = sorted(list(set([i['region'] for i in all_list])))
        group_list = sorted(list(set([i['group'] for i in all_list])))
        return {'code': 20000,'all_list':all_list,'vendor_list':vendor_list,
                'account_list':account_list,'region_list':region_list,'group_list':group_list}
    else:
        logger.error(f"{response.status_code}：{response.text}")
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def get_service():
    response = requests.get(f'{consul_url}/agent/services?filter=Service == selfnode_exporter', headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        vendor_list = sorted(list(set([i['vendor'] for i in all_list])))
        account_list = sorted(list(set([i['account'] for i in all_list])))
        region_list = sorted(list(set([i['region'] for i in all_list])))
        group_list = sorted(list(set([i['group'] for i in all_list])))
        return {'code': 20000,'all_list':all_list,'vendor_list':vendor_list,
                'account_list':account_list,'region_list':region_list,'group_list':group_list}
    else:
        logger.error(f"{response.status_code}：{response.text}")
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def add_service(vendor,account,region,group,name,ip,port,os):
    if port is None or name is None:
        return {"code": 50000, "data": f"名称或IP不能为空！"}
    sid = f"{vendor}/{account}/{region}/{group}@{name}".strip()
    sid = re.sub('[[ \]`~!\\\#$^&*=|"{}\':;?\t\n]','_',sid)
    instance = f'{ip}:{port}'
    if '//' in sid or sid.startswith('/') or sid.endswith('/'):
        return {"code": 50000, "data": f"服务ID【{sid}】首尾不能包含'/'，并且不能包含两个连续的'/'"}
    data = {
            "id": sid,
            "name": 'selfnode_exporter',
            'Address': ip,
            'port': int(port),
            "tags": [vendor,os],
            "Meta": {'vendor':vendor,'account':account,'region':region,'group':group,
                     'name':name,'instance':instance,'os':os},
            #"check": {"tcp": instance,"interval": "60s"}
           }
    reg = requests.put(f'{consul_url}/agent/service/register', headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】增加成功！"}
    else:
        logger.error(f"{reg.status_code}【{sid}】{reg.text}")
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

def del_service(vendor,account,region,group,name):
    sid = f"{vendor}/{account}/{region}/{group}@{name}".strip()
    sid = re.sub('[[ \]`~!\\\#$^&*=|"{}\':;?\t\n]','_',sid)
    reg = requests.put(f'{consul_url}/agent/service/deregister/{sid}', headers=headers)
    if reg.status_code == 200:
        logger.debug(f"【{sid}】删除成功！")
        return {"code": 20000, "data": f"【{sid}】删除成功！"}
    else:
        logger.error(f"{reg.status_code}【{sid}】{reg.text}")
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

