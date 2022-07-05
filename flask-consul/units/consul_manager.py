import requests,json
import sys 
sys.path.append("..") 
from config import consul_token,consul_url

headers = {'X-Consul-Token': consul_token}

def get_hosts():
    url = f'{consul_url}/agent/host'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        pmem = round(info["Memory"]["usedPercent"])
        pdisk = round(info["Disk"]["usedPercent"])
        host = {'hostname':info["Host"]["hostname"],'uptime':f'{round(info["Host"]["uptime"]/3600/24)}天',
                 'os':f'{info["Host"]["platform"]} {info["Host"]["platformVersion"]}','kernel':info["Host"]["kernelVersion"]}
        cpu = {'cores':f'{len(info["CPU"])}核','vendorId':info["CPU"][0]["vendorId"],'modelName':info["CPU"][0]["modelName"]}
        memory = {'total':f'{round(info["Memory"]["total"]/1024**3)}GB','available':f'{round(info["Memory"]["available"]/1024**3)}GB',
                  'used':f'{round(info["Memory"]["used"]/1024**3)}GB','usedPercent':f'{pmem}%'}
        disk = {'path':info["Disk"]["path"],'fstype':info["Disk"]["fstype"],'total':f'{round(info["Disk"]["total"]/1024**3)}GB',
                'free':f'{round(info["Disk"]["free"]/1024**3)}GB','used':f'{round(info["Disk"]["used"]/1024**3)}GB','usedPercent':f'{pdisk}%'}
        return {'code': 20000,'host':host,'cpu':cpu,'memory':memory,'disk':disk, 'pmem':pmem, 'pdisk':pdisk}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}
def get_services():
    url = f'{consul_url}/internal/ui/services'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        services_list = [{'Name':i['Name'],'Datacenter':i.get('Datacenter','Null'),'InstanceCount':i['InstanceCount'],'ChecksCritical':i['ChecksCritical'],'ChecksPassing':i['ChecksPassing'],'Tags':i['Tags'],'Nodes':list(set(i['Nodes']))} for i in info if i['Name'] != 'consul']
        return {'code': 20000,'services':services_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}
def get_services_nameonly():
    url = f'{consul_url}/catalog/services'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        info.pop('consul')
        return {'code': 20000,'services_name':list(info.keys())}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}
def get_instances(service_name):
    url = f'{consul_url}/health/service/{service_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        instances_list = []
        for i in info:
            instance_dict = {}
            instance_dict['ID'] = i['Service']['ID']
            instance_dict['name'] = i['Service']['Service']
            instance_dict['tags'] = '无' if i['Service']['Tags'] == [] else i['Service']['Tags']
            instance_dict['address'] = i['Service'].get('Address')
            instance_dict['port'] = i['Service'].get('Port')
            if i['Service']['Meta'] == {} or i['Service']['Meta'] is None:
                instance_dict['meta'] = '无'
            else:
                instance_dict['meta'] = [i['Service']['Meta']]
                instance_dict['meta_label'] = [{'prop': x, 'label': x} for x in i['Service']['Meta'].keys()]
            if len(i['Checks']) ==2:
                instance_dict['status'] = i['Checks'][1]['Status']
                instance_dict['output'] = i['Checks'][1]['Output']
            else:
                instance_dict['status'] = '无'
                instance_dict['output'] = '无'
            instances_list.append(instance_dict)
        return {'code': 20000,'instances':instances_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def del_instance(service_id):
    reg = requests.put(f'{consul_url}/agent/service/deregister/{service_id}', headers=headers)
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{service_id}】删除成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{service_id}】{reg.text}"}

def add_instance(instance_dict):
    sid = instance_dict['ID']
    if '//' in sid or sid.startswith('/') or sid.endswith('/'):
        return {"code": 50000, "data": f"服务ID【{sid}】首尾不能包含'/'，并且不能包含两个连续的'/'"}
    isMeta = instance_dict['metaInfo']['isMeta']
    isCheck = instance_dict['checkInfo']['isCheck']
    address = instance_dict['address']
    port = None if (instance_dict['port'] == '' or instance_dict['port'] is None) else int(instance_dict['port'])
    instance_dict['port'] = port
    if isMeta:
        try:
            metaJson = json.loads(instance_dict['metaInfo']['metaJson'])
            instance_dict['meta'] = metaJson
        except:
            return {"code": 50000, "data": "Meta必须JSON字符串格式！"}
    if isCheck:
        ctype = instance_dict['checkInfo']['ctype']
        interval = instance_dict['checkInfo']['interval']
        timeout = instance_dict['checkInfo']['timeout']
        if instance_dict['checkInfo']['isAddress'] == 'true':
            if port is not None and address != '' and ctype != 'HTTP':
                checkaddress = f'{address}:{port}'
            elif port is not None and address != '' and ctype == 'HTTP':
                checkaddress = f'http://{address}:{port}'
            else:
                return {"code": 50000, "data": "健康检查地址使用与实例IP端口一致时，地址/端口不可为空！"}
        else:
            checkaddress = instance_dict['checkInfo']['caddress']
            if checkaddress == '':
                return {"code": 50000, "data": "自定义健康检查，地址信息不可为空！"}

        check = {ctype: checkaddress,"Interval": interval,"Timeout": timeout}
        instance_dict['check'] = check
            
    del instance_dict['metaInfo']
    del instance_dict['checkInfo']
    print(instance_dict, flush=True)

    reg = requests.put(f'{consul_url}/agent/service/register', headers=headers, data=json.dumps(instance_dict))
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】增加成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

