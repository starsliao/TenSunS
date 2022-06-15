from alibabacloud_resourcemanager20200331.client import Client as ResourceManager20200331Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_resourcemanager20200331 import models as resource_manager_20200331_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from Tea.exceptions import TeaException

import sys,datetime
from units import consul_kv
from units.cloud import sync_ecs

def group(account):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = f'resourcemanager.aliyuncs.com'
    client = ResourceManager20200331Client(config)
    list_resource_groups_request = resource_manager_20200331_models.ListResourceGroupsRequest(page_size=100)
    try:
        proj = client.list_resource_groups(list_resource_groups_request)
        proj_list = proj.body.resource_groups.to_map()['ResourceGroup']
        group_dict = {i['Id']:i['DisplayName'] for i in proj_list}
        consul_kv.put_kv(f'ConsulManager/assets/alicloud/group/{account}',group_dict)
        count = len(group_dict)
        data = {'count':count,'update':now,'status':20000,'msg':f'同步资源组成功！总数：{count}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/group', data)
        print('【JOB】===>', 'alicloud_group', account, data, flush=True)
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        print("【code:】",e.code,"\n【message:】",emsg, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/group', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/group', data)

def ecs(account,region):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = f'ecs.{region}.aliyuncs.com'
    client = Ecs20140526Client(config)

    next_token = '0'
    ecs_dict = {}
    try:
        while next_token != '':
            describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
                max_results=100,
                region_id=region,
                next_token=next_token
            )
            ecs = client.describe_instances(describe_instances_request)
            ecs_list = ecs.body.instances.to_map()['Instance']
            ecs_dict_temp = {i['InstanceId']:{
                'name':i['InstanceName'],'group':group_dict.get(i['ResourceGroupId'],'无'),'ostype':i['OSType'].lower(),
                'status':i['Status'],'region':region,
                'ip':i["InnerIpAddress"]["IpAddress"] if len(i["InnerIpAddress"]["IpAddress"]) != 0 else i['NetworkInterfaces']['NetworkInterface'][0]['PrimaryIpAddress'],
                'cpu':f"{i['Cpu']}核",'mem':f"{str(round(i['Memory']/1024,1)).rstrip('.0')}GB",'exp':i['ExpiredTime'].split('T')[0],'ecstag': i.get('Tags',{}).get('Tag',[])
                }for i in ecs_list}
            ecs_dict.update(ecs_dict_temp)
            next_token = ecs.body.next_token

        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('alicloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)
        print('【JOB】===>', 'alicloud_ecs', account,region, data, flush=True)
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        print("【code:】",e.code,"\n【message:】",emsg, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)
