import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

import sys,datetime
#sys.path.append("..")
#import consul_kv,sync_ecs
from units import consul_kv
from units.cloud import sync_ecs

def group(account):
    from tencentcloud.dcdb.v20180411 import dcdb_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dcdb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dcdb_client.DcdbClient(cred, "ap-guangzhou", clientProfile)
        req = models.DescribeProjectsRequest()
        params = {}
        req.from_json_string(json.dumps(params))
        proj_list = client.DescribeProjects(req).Projects

        group_dict = {i.ProjectId:i.Name for i in proj_list}
        consul_kv.put_kv(f'ConsulManager/assets/tencent_cloud/group/{account}',group_dict)
        count = len(group_dict)
        data = {'count':count,'update':now,'status':20000,'msg':f'同步资源组成功！总数：{count}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/group', data)
        print('【JOB】===>', 'tencent_cloud_group', account, data, flush=True)
    except TencentCloudSDKException as err:
        print(err, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/group', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/group', data)

def ecs(account,region):
    from tencentcloud.cvm.v20170312 import cvm_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/tencent_cloud/group/{account}')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region, clientProfile)
        req = models.DescribeInstancesRequest()
        offset = 0
        total = 0
        ecs_dict = {}
        while offset <= total:
            params = {"Offset": offset, "Limit": 100}
            req.from_json_string(json.dumps(params))
            resp = client.DescribeInstances(req)
            ecs_list = resp.InstanceSet
            total = resp.TotalCount
            ecs_dict_temp = {i.InstanceId:{'name':i.InstanceName,'group':group_dict.get(str(i.Placement.ProjectId),'无'),
                'ostype': 'windows' if 'win' in i.OsName.lower() else 'linux',
                'status': i.InstanceState, 'region': region, 'ip':i.PrivateIpAddresses[0],
                'cpu': f'{i.CPU}核','mem': f'{i.Memory}GB','exp': i.ExpiredTime.split('T')[0]
                } for i in ecs_list}
            offset = offset + 100
            ecs_dict.update(ecs_dict_temp)

        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('tencent_cloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)
        print('【JOB】===>', 'tencent_cloud_ecs', account,region, data, flush=True)
    except TencentCloudSDKException as err:
        print(err, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)
