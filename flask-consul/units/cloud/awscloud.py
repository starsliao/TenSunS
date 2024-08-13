from Tea.exceptions import TeaException
import boto3

import sys,datetime,hashlib,math,traceback
from units import consul_kv,consul_svc
from units.cloud import sync_ecs,sync_rds,sync_redis,notify
from units.config_log import *

def exp(account,collect_days,notify_days,notify_amount):
    pass

def group(account):
    try:
        now = datetime.datetime.now().strftime('%m.%d/%H:%M')
        group_dict = {"1": "1"} # AWS没有资产组概念
        consul_kv.put_kv(f'ConsulManager/assets/awscloud/group/{account}',group_dict)
        count = len(group_dict)
        data = {'count':count,'update':now,'status':20000,'msg':f'同步资源组成功！总数：{count}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/group', data)
        logger.info(f'【JOB】===>awscloud_group {account} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{emsg}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/awscloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/group', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/group', data)

def ecs(account,region,isextip=False):
    ak,sk = consul_kv.get_aksk('awscloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/awscloud/group/{account}')  # {"1":"1"}

    ecs_dict = {}
    try:
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name=region,
        )
        response = ec2.describe_instances()

        for reservations in response['Reservations']:
            for instances in reservations['Instances']:
                InstanceId = instances["InstanceId"]
                ecs_dict_temp = {InstanceId: {}}
                for tag in instances["Tags"]:
                    if tag["Key"] == "Name":
                        ecs_dict_temp[InstanceId]["name"] = tag["Value"]
                ecs_dict_temp[InstanceId]["group"] = "无"
                ecs_dict_temp[InstanceId]["ostype"] = "windows" if "win" in instances["PlatformDetails"].lower() else "linux"
                ecs_dict_temp[InstanceId]["status"] = instances["State"]["Name"]
                ecs_dict_temp[InstanceId]["region"] = region
                ecs_dict_temp[InstanceId]["ip"] = instances["PrivateIpAddress"]
                ecs_dict_temp[InstanceId]["cpu"] = f'{instances["CpuOptions"]["CoreCount"]*instances["CpuOptions"]["ThreadsPerCore"]}核'
                ecs_dict_temp[InstanceId]["mem"] = "无"
                ecs_dict_temp[InstanceId]["exp"] = "按量" # AWS仅按量 
                if isextip:
                    ecs_dict_temp[InstanceId]["ip"] = instances["PublicIpAddress"]
                ecs_dict.update(ecs_dict_temp)

        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('awscloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/ecs/{region}', data)
        logger.info(f'【JOB】===>awscloud_ecs {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{emsg}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/awscloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/ecs/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/ecs/{region}', data)

def redis(account,region):
    ak,sk = consul_kv.get_aksk('awscloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/awscloud/group/{account}')

    redis_dict = {}
    try:
        elasticache = boto3.client(
            'elasticache',
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name=region,
        )
        response = elasticache.describe_cache_clusters()

        for rdb in response["CacheClusters"]:
            CacheClusterId = rdb["CacheClusterId"]
            redis_dict_temp = {CacheClusterId: {}}
            redis_dict_temp[CacheClusterId]["name"] = rdb["CacheClusterId"]
            redis_dict_temp[CacheClusterId]["domain"] = rdb.get("PrivateIp","null")
            redis_dict_temp[CacheClusterId]["ip"] = rdb.get("PrivateIp","null")
            redis_dict_temp[CacheClusterId]["port"] = 6379
            redis_dict_temp[CacheClusterId]["region"] = region
            redis_dict_temp[CacheClusterId]["group"] = rdb["ReplicationGroupId"]
            redis_dict_temp[CacheClusterId]["status"] = rdb["CacheClusterStatus"]
            redis_dict_temp[CacheClusterId]["itype"] = rdb["Engine"]
            redis_dict_temp[CacheClusterId]["ver"] = rdb["EngineVersion"]
            redis_dict_temp[CacheClusterId]["mem"] = "无"
            redis_dict_temp[CacheClusterId]["exp"] = "按量"
            redis_dict.update(redis_dict_temp)

        count = len(redis_dict)
        off,on = sync_redis.w2consul('awscloud',account,region,redis_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'redis同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/redis/{region}', data)
        logger.info(f'【JOB】===>awscloud_redis {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/awscloud/{account}/redis/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/redis/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/redis/{region}', data)

def rds(account,region):
    ak,sk = consul_kv.get_aksk('awscloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/awscloud/group/{account}')

    rds_dict = {}
    try:
        rds = boto3.client(
            "rds",
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name=region,
        )
        response = rds.describe_db_instances()

        for db in response["DBInstances"]:
            DBInstanceId = db["DBInstanceIdentifier"]
            rds_dict_temp = {DBInstanceId: {}}
            rds_dict_temp[DBInstanceId]["name"] = db["DBInstanceIdentifier"]
            rds_dict_temp[DBInstanceId]["domain"] = db["Endpoint"]["Address"]
            rds_dict_temp[DBInstanceId]["ip"] = db["Endpoint"]["Address"]
            rds_dict_temp[DBInstanceId]["port"] = db["Endpoint"]["Port"]
            rds_dict_temp[DBInstanceId]["region"] = region
            rds_dict_temp[DBInstanceId]["group"] = db["DBClusterIdentifier"]
            rds_dict_temp[DBInstanceId]["status"] = db["DBInstanceStatus"]
            rds_dict_temp[DBInstanceId]["itype"] = db["Engine"]
            rds_dict_temp[DBInstanceId]["ver"] = db["EngineVersion"]
            rds_dict_temp[DBInstanceId]["exp"] = "按量"
            rds_dict_temp[DBInstanceId]["cpu"] = "无"
            rds_dict_temp[DBInstanceId]["mem"] = "无"
            rds_dict_temp[DBInstanceId]["disk"] = "无"
            rds_dict.update(rds_dict_temp)
 
        count = len(rds_dict)
        off,on = sync_rds.w2consul('awscloud',account,region,rds_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'rds同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/rds/{region}', data)
        logger.info(f'【JOB】===>awscloud_rds {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/awscloud/{account}/rds/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/rds/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/awscloud/{account}/rds/{region}', data)
