import datetime,requests,json,traceback
from units import consul_kv,consul_manager,myaes
from units.config_log import *

#创建node
def create_node(jms_url,headers,now,node_id,cloud,account):
    node_url = f"{jms_url}/api/v1/assets/nodes/{node_id}/children/"
    logger.debug(f'{node_url}==>{headers}')
    jms_node_list = requests.request("GET", node_url, headers=headers).json()
    if type(jms_node_list) == dict:
        detail = jms_node_list.get('detail','未知ERROR')
        logger.error(f'  【JMS】{detail}\n{node_url}==>{headers}')
        data = {'count': '失败','update':now,'status':50000,'msg':f'同步资源失败！{detail}'}
        consul_kv.put_kv(f'ConsulManager/record/jms/{cloud}/{account}', data)
    cloud_group_dict = consul_kv.get_value(f'ConsulManager/assets/{cloud}/group/{account}')
    cloud_group_dict['nogroup'] = '未分组'
    for k,v in cloud_group_dict.items():
        if v not in [i['value'] for i in jms_node_list]:
            response = requests.request("POST", node_url, headers=headers, data = json.dumps({'value': v}))
            if response.status_code != 201:
                logger.error(f'  【JMS】创建分组失败，可能的原因：JumpServer URL 有重定向，请使用直连地址。')
            logger.debug(f'  【JMS】新增组===>{v},{response.status_code}')
    reget_node_list = requests.request("GET", node_url, headers=headers).json()
    new_node_dict = {i['value']:i['id'] for i in reget_node_list}
    return new_node_dict

def update_jms_ecs(jms_ver,jms_url,headers,new_node_dict,node_id,cloud,account,ecs_info,custom_ecs_info):
    #比较云主机与JMS中对应node的主机列表，删除jms中多余的主机
    ecs_url = f"{jms_url}/api/v1/assets/assets/"
    reget_ecs_list = requests.request("GET", f'{ecs_url}?node={node_id}', headers=headers).json()
    try:
        jms_ecs_dict = {i.get('ip',i.get('address','IPNOTFOUND')):{'name':i.get('hostname',i.get('name','NAMENOTFOUND')),'id':i['id'],'comment':i['comment'],'node':i['nodes_display'][0]} for i in reget_ecs_list}
    except:
        jms_ecs_dict = {i.get('ip',i.get('address','IPNOTFOUND')):{'name':i.get('hostname',i.get('name','NAMENOTFOUND')),'id':i['id'],'comment':i['comment'],'node':i['nodes'][0]} for i in reget_ecs_list}

    ecs_list = consul_manager.get_instances(f'{cloud}_{account}_ecs')['instances']
    ecs_ip_dict = {i['address']:i['meta'][0]['name'] for i in ecs_list}
    ecs_dict = {i['ID']:{'name':i['meta'][0]['name'],'ip':i['address'],'ent':i['meta'][0]['group'],'ostype':i['meta'][0]['os'],'region':i['meta'][0]['region'],'vendor':i['meta'][0]['vendor']} for i in ecs_list}
    del_ecs_list = [v['id'] for k,v in jms_ecs_dict.items() if k not in [i['ip'] for i in ecs_dict.values()]]
    for del_ecs in del_ecs_list:
        response = requests.request("DELETE", f'{ecs_url}{del_ecs}/', headers=headers)
        logger.info(f'  【JMS】删除主机:{del_ecs},{response.status_code}')

    #增加/更新缺少的主机
    for k,v in ecs_dict.items():
        ip = v['ip']
        iname = v['name']
        nodes = new_node_dict.get(v['ent'],new_node_dict['未分组'])
        ostype = v['ostype']
        comment = f"{v['vendor']} {account} {v['region']} {k}"
        protocols = ecs_info[ostype][0]
        platform = ostype.title()
        admin_user = ecs_info[ostype][1]
        if custom_ecs_info != {}:
            if len([i for i in custom_ecs_info.keys() if i.lower() in iname.lower()]) > 0:
                for custom_name,custom_info in custom_ecs_info.items():
                    if custom_name.lower() in iname.lower():
                        protocols = custom_info[ostype][0]
                        platform = ostype.title()
                        admin_user = custom_info[ostype][1]
        if jms_ver == 'V3':
            ecs_url = f"{jms_url}/api/v1/assets/hosts/"
            proto,port = protocols[0].split('/')
            payload = {
            "address": ip,
            "name": iname,
            "protocols": [{"name": proto,"port": port}],
            "platform": '5' if platform == 'Windows' else '1',
            "is_active": True,
            "domain": "",
            "accounts":[{"template": admin_user.strip()}],
            "nodes": [nodes],
            "comment": comment
            }
        else:
            payload = {
            "ip": ip,
            "hostname": iname,
            "protocols": protocols,
            "platform": platform,
            "is_active": True,
            "domain": "",
            "admin_user": admin_user.strip(),
            "nodes": [nodes],
            "comment": comment
            }
        try:
            if ip in jms_ecs_dict.keys():
                jms_group = '无' if jms_ecs_dict[ip]['node'].split('/')[-1] == '未分组' else jms_ecs_dict[ip]['node'].split('/')[-1]
                if jms_ecs_dict[ip]['name'] != iname or jms_group != v['ent']:
                    response = requests.request("PUT", f"{ecs_url}{jms_ecs_dict[ip]['id']}/", headers=headers, data = json.dumps(payload))
                    logger.info(f"  【JMS】update：主机名:{response.json().get('hostname',response.json())}，{response.status_code}")
            else:
                response = requests.request("POST", ecs_url, headers=headers, data = json.dumps(payload))
                logger.info(f"  【JMS】add：主机名:{iname} {ip}【{response.json().get('hostname',response.json())}，{response.status_code}】")
        except Exception as e:
            logger.error(f'【update_jms ERROR】{e}\n{traceback.format_exc()}')
            logger.error(f'{response.json()}')
    return ecs_ip_dict

#从JMS中删除IP重复的主机
def del_jms_repip(jms_url,headers,node_id,ecs_ip_dict):
    ecs_url = f"{jms_url}/api/v1/assets/assets/"
    temp_jmsecs_dict = {}
    rep_jmsecs_list = []
    new_jms_list = requests.request("GET", f'{ecs_url}?node={node_id}', headers=headers).json()
    for i in new_jms_list:
        if i.get('ip',i.get('address','IPNOTFOUND')) not in temp_jmsecs_dict:
            temp_jmsecs_dict[i.get('ip',i.get('address','IPNOTFOUND'))] = {'name':i.get('hostname',i.get('name','NAMENOTFOUND')),'id':i['id'],'ip':i.get('ip',i.get('address','IPNOTFOUND'))}
        else:
            rep_jmsecs_list.append(temp_jmsecs_dict[i.get('ip',i.get('address','IPNOTFOUND'))])
            rep_jmsecs_list.append({'name':i.get('hostname',i.get('name','NAMENOTFOUND')),'id':i['id'],'ip':i.get('ip',i.get('address','IPNOTFOUND'))})
    
    for j in rep_jmsecs_list:
        if j['name'] != ecs_ip_dict.get(j['ip']):
            del_ecs = j['id']
            response = requests.request("DELETE", f'{ecs_url}{del_ecs}/', headers=headers)
            logger.info(f"  【JMS】删除IP重复且名称不在ECS列表的主机:{j['name']},{j['ip']},{response.status_code}")

#从JMS中删除没有主机的组
def del_node(jms_url,headers,now,node_id,cloud,account):
    node_tree_url = f"{jms_url}/api/v1/assets/nodes/children/tree/?id={node_id}"
    jms_node_list = requests.request("GET", node_tree_url, headers=headers).json()
    for i in jms_node_list:
        if i['name'].endswith(' (0)'):
            if 'node' in i['meta']:
                del_node_url = f"{jms_url}/api/v1/assets/nodes/{i['meta']['node']['id']}/"
            else:
                del_node_url = f"{jms_url}/api/v1/assets/nodes/{i['meta']['data']['id']}/"
            response = requests.request("DELETE", del_node_url, headers=headers)
            logger.debug(f"  【JMS】删除空组===>{i['name']},{response.status_code}")
    ecs_count_url = f"{jms_url}/api/v1/assets/assets/?node={node_id}&limit=1&offset=1"
    ecs_count = requests.request("GET", ecs_count_url, headers=headers).json()['count']
    data = {'count':ecs_count,'update':now,'status':20000,'msg':f'同步资源成功！总数：{ecs_count}'}
    consul_kv.put_kv(f'ConsulManager/record/jms/{cloud}/{account}', data)
    return 'ok'

def run(cloud,account):
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    logger.info(f'【JOB】===>{cloud},{account},JMS同步开始')
    node_id = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/node_id')['node_id']
    temp_ecs_info = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/ecs_info')
    ecs_info = consul_kv.get_value(f'ConsulManager/jms/ecs_info') if temp_ecs_info == {} else temp_ecs_info
    temp_custom_ecs_info = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/custom_ecs_info')
    custom_ecs_info = consul_kv.get_value(f'ConsulManager/jms/custom_ecs_info') if temp_custom_ecs_info == {} else temp_custom_ecs_info

    jms = consul_kv.get_value('ConsulManager/jms/jms_info')
    jms_url = jms.get('url')
    jms_ver = jms.get('ver','V2')
    token = myaes.decrypt(jms.get('token'))
    headers = {'Content-Type': 'application/json','Authorization': f"Token {token}"}

    new_node_dict = create_node(jms_url,headers,now,node_id,cloud,account)
    ecs_ip_dict = update_jms_ecs(jms_ver,jms_url,headers,new_node_dict,node_id,cloud,account,ecs_info,custom_ecs_info)
    del_jms_repip(jms_url,headers,node_id,ecs_ip_dict)
    del_node(jms_url,headers,now,node_id,cloud,account)
    logger.info(f'【JOB】===>{cloud},{account},JMS同步完成')
