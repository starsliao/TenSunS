from huaweicloudsdkcore.auth.credentials import GlobalCredentials,BasicCredentials
from huaweicloudsdkeps.v1.region.eps_region import EpsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkeps.v1 import *
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkecs.v2 import *
import sys,datetime
from units import consul_kv
from units.cloud import sync_ecs
def group(account):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    credentials = GlobalCredentials(ak, sk)
    try:
        client = EpsClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(EpsRegion.value_of("cn-north-4")) \
            .build()
        request = ListEnterpriseProjectRequest()
        request.status = 1
        request.offset = 0
        info = client.list_enterprise_project(request).to_dict()['enterprise_projects']
        group_dict = {i['id']:i['name'] for i in info}
        consul_kv.put_kv(f'ConsulManager/assets/huaweicloud/group/{account}',group_dict)
        count = len(group_dict)
        data = {'count':count,'update':now,'status':20000,'msg':f'同步企业项目成功！总数：{count}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/group', data)
        print('【JOB】===>', 'huaweicloud_group', account, data, flush=True)
    except exceptions.ClientRequestException as e:
        print(e.status_code, flush=True)
        print(e.request_id, flush=True)
        print(e.error_code, flush=True)
        print(e.error_msg, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/group', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/group', data)

def ecs(account,region):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/huaweicloud/group/{account}')
    credentials = BasicCredentials(ak, sk)
    try:
        client = EcsClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(EcsRegion.value_of(region)) \
            .build()
        request = ListServersDetailsRequest()
        request.limit = 1000
        info = client.list_servers_details(request).to_dict()['servers']
        ecs_dict = {i['id']:{'name':i['name'],
                             'ip':i['addresses'][i['metadata']['vpc_id']][0].addr,
                             'region':region,
                             'group':group_dict[i['enterprise_project_id']],
                             'status':i['status'],
                             'ostype':i['metadata']['os_type'].lower(),
                             'cpu':i['flavor']['vcpus'] + '核',
                             'mem':f"{str(round(int(i['flavor']['ram'])/1024,1)).rstrip('.0')}GB",
                             'exp': '-'
                            } for i in info}
        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('huaweicloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)
        print('【JOB】===>', 'huaweicloud_ecs', account,region, data, flush=True)
    except exceptions.ClientRequestException as e:
        print(e.status_code, flush=True)
        print(e.request_id, flush=True)
        print(e.error_code, flush=True)
        print(e.error_msg, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'on':0,'off':0,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)
