from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

import sys,datetime,hashlib,json,traceback
#sys.path.append("..")
#import consul_kv,sync_ecs
from units import consul_kv
from units.cloud import sync_ecs,sync_rds,sync_redis,notify
from units.config_log import *

def exp(account,collect_days,notify_days,notify_amount):
    from tencentcloud.billing.v20180709 import billing_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    exp_dict = {}
    isnotify_list = consul_kv.get_keys_list(f'ConsulManager/exp/isnotify/tencent_cloud/{account}')
    isnotify_list = [i.split('/')[-1] for i in isnotify_list]
    notify_dict = {}
    amount_dict = {}
    try:
        ecs_list = consul_kv.get_services_meta(f'tencent_cloud_{account}_ecs').get('ecs_list',[])
        now = datetime.datetime.now()
        for i in [x for x in ecs_list if x['exp'] != '按量']:
            exp_day = datetime.datetime.strptime(i['exp'], '%Y-%m-%d')
            if (exp_day - now).days <= collect_days:
                notify_id = hashlib.md5(str(i).encode(encoding='UTF-8')).hexdigest()
                exp_dict[i['iid']] = {'Region':i['region'],'Product':i['os'],'Name':i['name'],
                    'EndTime':i['exp'],'Ptype':i['cpu']+i['mem'],'Group':i['group'],'notify_id':notify_id}
            if (exp_day - now).days <= notify_days and notify_id not in isnotify_list:
                notify_dict[i['iid']] = exp_dict[i['iid']]
        consul_kv.put_kv(f'ConsulManager/exp/lists/tencent_cloud/{account}/exp', exp_dict)

        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "billing.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = billing_client.BillingClient(cred, "", clientProfile)

        req = models.DescribeAccountBalanceRequest()
        params = {}
        req.from_json_string(json.dumps(params))

        amount = client.DescribeAccountBalance(req).RealBalance/100
        consul_kv.put_kv(f'ConsulManager/exp/lists/tencent_cloud/{account}/amount',{'amount':amount})
        if amount < notify_amount:
            amount_dict = {'amount':amount}
        exp_config = consul_kv.get_value('ConsulManager/exp/config')
        wecomwh = exp_config.get('wecomwh','')
        dingdingwh = exp_config.get('dingdingwh','')
        feishuwh = exp_config.get('feishuwh','')
        isatall = exp_config.get('isatall', True)
        if notify_dict != {}:
            msg = [f'### 腾讯云账号 {account}：\n### 以下资源到期日小于 {notify_days} 天：']
            for k,v in notify_dict.items():
                msg.append(f"- {v['Region']}：{v['Product']}：{v['Group']}：{v['Name']}：<font color=\"#ff0000\">{v['EndTime']}</font>")
            content = '\n'.join(msg)
            if exp_config['switch'] and exp_config.get('wecom',False):
                notify.wecom(wecomwh,content)
            if exp_config['switch'] and exp_config.get('dingding',False):
                notify.dingding(dingdingwh,content,isatall)
            if exp_config['switch'] and exp_config.get('feishu',False):
                title = '腾讯云资源到期通知'
                md = content
                notify.feishu(feishuwh,title,md,isatall)
        if amount_dict != {}:
            content = f'### 腾讯云账号 {account}：\n### 可用余额：<font color=\"#ff0000\">{amount}</font> 元'
            if exp_config['switch'] and exp_config.get('wecom',False):
                notify.wecom(wecomwh,content)
            if exp_config['switch'] and exp_config.get('dingding',False):
                notify.dingding(dingdingwh,content,isatall)
            if exp_config['switch'] and exp_config.get('feishu',False):
                title = '腾讯云余额不足通知'
                md = content
                notify.feishu(feishuwh,title,md,isatall)
    except TencentCloudSDKException as e:
        logger.error(f'{e}\n{traceback.format_exc()}')

def group(account):
    from tencentcloud.dcdb.v20180411 import dcdb_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
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
        logger.info(f'【JOB】===>tencent_cloud_group {account} {data}')
    except TencentCloudSDKException as err:
        logger.error(f'{err}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/group', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/group', data)

def ecs(account,region,isextip=False):
    from tencentcloud.cvm.v20170312 import cvm_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
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
        ecs_list_temp = []
        while offset <= total:
            params = {"Offset": offset, "Limit": 100}
            req.from_json_string(json.dumps(params))
            resp = client.DescribeInstances(req)
            ecs_list = resp.InstanceSet
            ecs_list_temp.extend(ecs_list)
            total = resp.TotalCount
            ecs_dict_temp = {i.InstanceId:{'name':i.InstanceName,'group':group_dict.get(str(i.Placement.ProjectId),'无'),
                'ostype': 'windows' if 'win' in i.OsName.lower() else 'linux',
                'status': i.InstanceState, 'region': region, 'ip':i.PrivateIpAddresses[0],
                'cpu': f'{i.CPU}核','mem': f'{i.Memory}GB',
                'exp': '按量' if i.ExpiredTime is None else i.ExpiredTime.split('T')[0]
                } for i in ecs_list}
            offset = offset + 100
            ecs_dict.update(ecs_dict_temp)

        if isextip:
            for i in ecs_list_temp:
                try:
                    if i.PublicIpAddresses:
                        ecs_dict[i.InstanceId]['ip'] = i.PublicIpAddresses[0]
                    else:
                        pass
                except:
                    pass

        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('tencent_cloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)
        logger.info(f'【JOB】===>tencent_cloud_ecs {account} {region} {data}')
    except TencentCloudSDKException as err:
        logger.error(f'{err}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/ecs/{region}', data)

def rds(account,region):
    from tencentcloud.cdb.v20170320 import cdb_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/tencent_cloud/group/{account}')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, region, clientProfile)
        req = models.DescribeDBInstancesRequest()
        params = {"Limit": 2000}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeDBInstances(req)
        rds_list = resp.Items
        total = resp.TotalCount
        rds_dict = {i.InstanceId:{'name':i.InstanceName,
                             'domain':i.Vip,
                             'ip':i.Vip,
                             'port':i.Vport,
                             'region':region,
                             'group':group_dict.get(str(i.ProjectId),'无'),
                             'status': '运行中' if i.Status == 1 else '非运行中',
                             'itype':{1:'主实例',2:'灾备实例',3:'只读实例'}[i.InstanceType],
                             'ver':i.EngineVersion,
                             'exp': '按量' if i.DeadlineTime == "0000-00-00 00:00:00" else i.DeadlineTime.split(' ')[0],
                             'cpu':f"{i.Cpu}核",
                             'mem':f"{round(i.Memory/1024)}GB",
                             'disk':f"{i.Volume}GB"
                            } for i in rds_list}
        count = len(rds_dict)
        off,on = sync_rds.w2consul('tencent_cloud',account,region,rds_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'rds同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/rds/{region}', data)
        logger.info(f'【JOB】===>tencent_cloud_rds {account} {region} {data}')
    except TencentCloudSDKException as err:
        logger.error(f'{err}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/rds/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/rds/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/rds/{region}', data)

def redis(account,region):
    from tencentcloud.redis.v20180412 import redis_client, models
    ak,sk = consul_kv.get_aksk('tencent_cloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/tencent_cloud/group/{account}')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "redis.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = redis_client.RedisClient(cred, region, clientProfile)
        req = models.DescribeInstancesRequest()
        params = {"Limit": 1000}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req)
        redis_list = resp.InstanceSet
        total = resp.TotalCount
        redis_dict = {i.InstanceId:{'name':i.InstanceName,
                             'domain':i.WanIp,
                             'ip':i.WanIp,
                             'port':i.Port,
                             'region':region,
                             'group':group_dict.get(str(i.ProjectId),'无'),
                             'status': '运行中' if i.Status == 2 else '非运行中',
                             'itype':{6:'主从',7:'集群',8:'主从',9:'集群'}.get(i.Type,i.Type),
                             'ver':i.CurrentRedisVersion,
                             'exp': '按量' if i.DeadlineTime == "0000-00-00 00:00:00" else i.DeadlineTime.split(' ')[0],
                             'mem':f"{i.Size}MB",
                            } for i in redis_list}
        count = len(redis_dict)
        off,on = sync_redis.w2consul('tencent_cloud',account,region,redis_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'redis同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/redis/{region}', data)
        logger.info(f'【JOB】===>tencent_cloud_redis {account} {region} {data}')
    except TencentCloudSDKException as err:
        logger.error(f'{err}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/tencent_cloud/{account}/redis/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败','status':50000,'msg':str(err)}
        else:
            data['update'] = f'失败'
            data['msg'] = str(err)
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/redis/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/tencent_cloud/{account}/redis/{region}', data)
