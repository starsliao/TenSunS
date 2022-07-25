import datetime,requests,json
from units import consul_kv,consul_manager,myaes

#创建node
def create_node(jms_url,headers,now,node_id,cloud,account):
    node_url = f"{jms_url}/api/v1/assets/nodes/{node_id}/children/"
    jms_node_list = requests.request("GET", node_url, headers=headers).json()
    if type(jms_node_list) == dict:
        detail = jms_node_list.get('detail','ERROR')
        print('  【JMS】',detail,flush=True)
        data = {'count': '失败','update':now,'status':50000,'msg':f'同步资源失败！{detail}'}
        consul_kv.put_kv(f'ConsulManager/record/jms/{cloud}/{account}', data)
    cloud_group_dict = consul_kv.get_value(f'ConsulManager/assets/{cloud}/group/{account}')
    cloud_group_dict['nogroup'] = '未分组'
    for k,v in cloud_group_dict.items():
        if v not in [i['value'] for i in jms_node_list]:
            response = requests.request("POST", node_url, headers=headers, data = json.dumps({'value': v}))
            print('  【JMS】新增组===>',v,response.status_code,flush=True)
    reget_node_list = requests.request("GET", node_url, headers=headers).json()
    new_node_dict = {i['value']:i['id'] for i in reget_node_list}
    return new_node_dict

def update_jms_ecs(jms_url,headers,new_node_dict,node_id,cloud,account,ecs_info,custom_ecs_info):
    #比较云主机与JMS中对应node的主机列表，删除jms中多余的主机
    ecs_url = f"{jms_url}/api/v1/assets/assets/"
    reget_ecs_list = requests.request("GET", f'{ecs_url}?node={node_id}', headers=headers).json()
    jms_ecs_dict = {i['ip']:{'name':i['hostname'],'id':i['id'],'comment':i['comment'],'node':i['nodes_display'][0]} for i in reget_ecs_list}
    ecs_list = consul_manager.get_instances(f'{cloud}_{account}_ecs')['instances']
    ecs_ip_dict = {i['address']:i['meta'][0]['name'] for i in ecs_list}
    ecs_dict = {i['ID']:{'name':i['meta'][0]['name'],'ip':i['address'],'ent':i['meta'][0]['group'],'ostype':i['meta'][0]['os'],'region':i['meta'][0]['region'],'vendor':i['meta'][0]['vendor']} for i in ecs_list}
    del_ecs_list = [v['id'] for k,v in jms_ecs_dict.items() if k not in [i['ip'] for i in ecs_dict.values()]]
    for del_ecs in del_ecs_list:
        response = requests.request("DELETE", f'{ecs_url}{del_ecs}/', headers=headers)
        print('  【JMS】删除主机:',del_ecs,response.status_code,flush=True)

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
        payload = {
            "ip": ip,
            "hostname": iname,
            "protocols": protocols,
            "platform": platform,
            "is_active": True,
            "domain": "",
            "admin_user": admin_user,
            "nodes": [nodes],
            "comment": comment
        }
        if ip in jms_ecs_dict.keys():
            jms_group = '无' if jms_ecs_dict[ip]['node'].split('/')[-1] == '未分组' else jms_ecs_dict[ip]['node'].split('/')[-1]
            if jms_ecs_dict[ip]['name'] != iname or jms_group != v['ent']:
                response = requests.request("PUT", f"{ecs_url}{jms_ecs_dict[ip]['id']}/", headers=headers, data = json.dumps(payload))
                print('  【JMS】update：主机名:',response.json()['hostname'],response.status_code,flush=True)
        else:
            response = requests.request("POST", ecs_url, headers=headers, data = json.dumps(payload))
            print('  【JMS】add：主机名:',iname,ip,f"【{response.json()['hostname']}，{response.status_code}】",flush=True)
    return ecs_ip_dict

#从JMS中删除IP重复的主机
def del_jms_repip(jms_url,headers,node_id,ecs_ip_dict):
    ecs_url = f"{jms_url}/api/v1/assets/assets/"
    temp_jmsecs_dict = {}
    rep_jmsecs_list = []
    new_jms_list = requests.request("GET", f'{ecs_url}?node={node_id}', headers=headers).json()
    for i in new_jms_list:
        if i['ip'] not in temp_jmsecs_dict:
            temp_jmsecs_dict[i['ip']] = {'name':i['hostname'],'id':i['id'],'ip':i['ip']}
        else:
            rep_jmsecs_list.append(temp_jmsecs_dict[i['ip']])
            rep_jmsecs_list.append({'name':i['hostname'],'id':i['id'],'ip':i['ip']})
    
    for j in rep_jmsecs_list:
        if j['name'] != ecs_ip_dict.get(j['ip']):
            del_ecs = j['id']
            response = requests.request("DELETE", f'{ecs_url}{del_ecs}/', headers=headers)
            print('  【JMS】删除IP重复且名称不在ECS列表的主机:',j['name'],j['ip'],response.status_code,flush=True)

#从JMS中删除没有主机的组
def del_node(jms_url,headers,now,node_id,cloud,account):
    node_tree_url = f"{jms_url}/api/v1/assets/nodes/children/tree/?id={node_id}"
    jms_node_list = requests.request("GET", node_tree_url, headers=headers).json()
    for i in jms_node_list:
        if i['name'].endswith(' (0)'):
            del_node_url = f"{jms_url}/api/v1/assets/nodes/{i['meta']['node']['id']}/"
            response = requests.request("DELETE", del_node_url, headers=headers)
            print('  【JMS】删除空组===>',i['name'],response.status_code,flush=True)
    ecs_count_url = f"{jms_url}/api/v1/assets/assets/?node={node_id}&limit=1&offset=1"
    ecs_count = requests.request("GET", ecs_count_url, headers=headers).json()['count']
    data = {'count':ecs_count,'update':now,'status':20000,'msg':f'同步资源成功！总数：{ecs_count}'}
    consul_kv.put_kv(f'ConsulManager/record/jms/{cloud}/{account}', data)
    return 'ok'

def run(cloud,account):
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    print('【JOB】===>',cloud,account,'JMS同步开始',flush=True)
    node_id = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/node_id')['node_id']
    temp_ecs_info = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/ecs_info')
    ecs_info = consul_kv.get_value(f'ConsulManager/jms/ecs_info') if temp_ecs_info == {} else temp_ecs_info
    temp_custom_ecs_info = consul_kv.get_value(f'ConsulManager/jms/{cloud}/{account}/custom_ecs_info')
    custom_ecs_info = consul_kv.get_value(f'ConsulManager/jms/custom_ecs_info') if temp_custom_ecs_info == {} else temp_custom_ecs_info

    jms = consul_kv.get_value('ConsulManager/jms/jms_info')
    jms_url = jms.get('url')
    token = myaes.decrypt(jms.get('token'))
    headers = {'Content-Type': 'application/json','Authorization': f"Token {token}"}

    new_node_dict = create_node(jms_url,headers,now,node_id,cloud,account)
    ecs_ip_dict = update_jms_ecs(jms_url,headers,new_node_dict,node_id,cloud,account,ecs_info,custom_ecs_info)
    del_jms_repip(jms_url,headers,node_id,ecs_ip_dict)
    del_node(jms_url,headers,now,node_id,cloud,account)
    print('【JOB】===>',cloud,account,'JMS同步完成',flush=True)
