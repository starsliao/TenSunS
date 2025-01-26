from Tea.exceptions import TeaException
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from alibabacloud_resourcemanager20200331.client import Client as ResourceManager20200331Client
from alibabacloud_resourcemanager20200331 import models as resource_manager_20200331_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_bssopenapi20171214.client import Client as BssOpenApi20171214Client
from alibabacloud_bssopenapi20171214 import models as bss_open_api_20171214_models
from alibabacloud_rds20140815.client import Client as Rds20140815Client
from alibabacloud_rds20140815 import models as rds_20140815_models
from alibabacloud_r_kvstore20150101 import models as r_kvstore_20150101_models
from alibabacloud_r_kvstore20150101.client import Client as R_kvstore20150101Client
from alibabacloud_polardb20170801.client import Client as polardb20170801Client
from alibabacloud_polardb20170801 import models as polardb_20170801_models
from alibabacloud_dds20151201.client import Client as Dds20151201Client
from alibabacloud_dds20151201 import models as dds_20151201_models
from alibabacloud_clickhouse20191111.client import Client as clickhouse20191111Client
from alibabacloud_clickhouse20191111 import models as clickhouse_20191111_models
from alibabacloud_clickhouse20230522.client import Client as clickhouse20230522Client
from alibabacloud_clickhouse20230522 import models as clickhouse_20230522_models

import sys,datetime,hashlib,math,traceback
from units import consul_kv,consul_svc
from units.cloud import sync_ecs,sync_rds,sync_redis,notify,sync_polardb,sync_mongodb,sync_clickhouse
from units.config_log import *

def exp(account,collect_days,notify_days,notify_amount):
    logger.debug(f"=====【阿里云：余额与到期日统计开始：{account}】")
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT16:00:00Z')
    collect = (datetime.datetime.utcnow() + datetime.timedelta(days=collect_days+1)).strftime('%Y-%m-%dT16:00:00Z')
    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = f'business.aliyuncs.com'
    client = BssOpenApi20171214Client(config)
    exp_config = consul_kv.get_value('ConsulManager/exp/config')
    wecomwh = exp_config.get('wecomwh','')
    dingdingwh = exp_config.get('dingdingwh','')
    feishuwh = exp_config.get('feishuwh','')
    isatall = exp_config.get('isatall', True)
    try:
        amount_response = client.query_account_balance()
        if amount_response.body.success:
            available_amount = amount_response.body.data.available_amount
            amount = float(available_amount.replace(',',''))
            consul_kv.put_kv(f'ConsulManager/exp/lists/alicloud/{account}/amount',{'amount':amount})
            logger.debug(f'alicloud {account} 可用余额:{available_amount}')
            amount_dict = {}
            if amount < notify_amount:
                amount_dict = {'amount':amount}
                content = f'### 阿里云账号 {account}：\n### 可用余额：<font color=\"#ff0000\">{amount}</font> 元'
                if exp_config['switch'] and exp_config.get('wecom',False):
                    notify.wecom(wecomwh,content)
                if exp_config['switch'] and exp_config.get('dingding',False):
                    notify.dingding(dingdingwh,content,isatall)
                if exp_config['switch'] and exp_config.get('feishu',False):
                    title = '阿里云余额不足通知'
                    md = content
                    notify.feishu(feishuwh,title,md,isatall)
        else:
            logger.error(f'查询失败，Code:{amount_response.body.code}, 信息:{amount_response.body.message}, requestId:{amount_response.body.request_id}')
    except Exception as e:
        logger.error(f'==ERROR=={e}\n{traceback.format_exc()}')
        raise
    query_available_instances_request = bss_open_api_20171214_models.QueryAvailableInstancesRequest(renew_status='ManualRenewal',end_time_start=now,end_time_end=collect)
    runtime = util_models.RuntimeOptions()
    try:
        exp = client.query_available_instances_with_options(query_available_instances_request, runtime)
        exp_list = exp.body.to_map()['Data']['InstanceList']
    except Exception as e:
        #exp_list = []
        logger.error(f'==ERROR=={e}\n{traceback.format_exc()}')
        raise
    exp_dict = {}
    isnotify_list = consul_kv.get_keys_list(f'ConsulManager/exp/isnotify/alicloud/{account}')
    isnotify_list = [i.split('/')[-1] for i in isnotify_list]
    notify_dict = {}
    for i in exp_list:
        notify_id = hashlib.md5(str(i).encode(encoding='UTF-8')).hexdigest()
        endtime = datetime.datetime.strptime(i['EndTime'],'%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
        endtime_str = endtime.strftime('%Y-%m-%d')
        logger.debug(f"{i['ProductCode']} {i['InstanceID']}")
        iname = consul_svc.get_sid(i['InstanceID'])['instance']['Meta']['name'] if i['ProductCode'] == 'ecs' else 'Null'
        exp_dict[i['InstanceID']] = {'Region':i.get('Region','Null'),'Product':i['ProductCode'],
            'Name':iname,'EndTime':endtime_str,'notify_id':notify_id,
            'Ptype':i.get('ProductType',i['ProductCode'])}
        if (endtime - datetime.datetime.now()).days < notify_days and notify_id not in isnotify_list:
            notify_dict[i['InstanceID']] = exp_dict[i['InstanceID']]
    consul_kv.put_kv(f'ConsulManager/exp/lists/alicloud/{account}/exp', exp_dict)
    if notify_dict != {}:
        msg = [f'### 阿里云账号 {account}：\n### 以下资源到期日小于 {notify_days} 天：']
        for k,v in notify_dict.items():
            iname = k if v['Name'] == 'Null' else v['Name']
            msg.append(f"- {v['Region']}：{v['Product']}：{iname}：<font color=\"#ff0000\">{v['EndTime']}</font>")
        content = '\n'.join(msg)
        if exp_config['switch'] and exp_config.get('wecom',False):
            notify.wecom(wecomwh,content)
        if exp_config['switch'] and exp_config.get('dingding',False):
            notify.dingding(dingdingwh,content,isatall)
        if exp_config['switch'] and exp_config.get('feishu',False):
            title = '阿里云资源到期通知'
            md = content
            notify.feishu(feishuwh,title,md,isatall)
    logger.debug(f"=====【阿里云：余额与到期日统计结束：{account}】")

def group(account):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
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
        logger.info(f'【JOB】===>alicloud_group {account} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{emsg}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/group', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/group', data)

def ecs(account,region,isextip=False):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
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
                'name':i['InstanceName'],'group':group_dict.get(i['ResourceGroupId'],'无'),'ostype':i['OSType'].lower(),'status':i['Status'],'region':region,
                'ip':i["InnerIpAddress"]["IpAddress"][0] if i["InnerIpAddress"]["IpAddress"] else i['NetworkInterfaces']['NetworkInterface'][0].get('PrimaryIpAddress','NoneInnerIp'),
                'cpu':f"{i['Cpu']}核",'mem':f"{str(round(i['Memory']/1024,1)).rstrip('.0')}GB",'exp':i['ExpiredTime'].split('T')[0],'ecstag': i.get('Tags',{}).get('Tag',[])
                }for i in ecs_list}

            if isextip:
                for i in ecs_list:
                    try:
                        if i['PublicIpAddress']['IpAddress']:
                            ecs_dict_temp[i['InstanceId']]['ip'] = i['PublicIpAddress']['IpAddress'][0]
                        elif i["EipAddress"]["IpAddress"] != '':
                            ecs_dict_temp[i['InstanceId']]['ip'] = i["EipAddress"]["IpAddress"]
                    except:
                        pass
            ecs_dict.update(ecs_dict_temp)
            next_token = ecs.body.next_token

        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('alicloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)
        logger.info(f'【JOB】===>alicloud_ecs {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{emsg}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/ecs/{region}', data)

def redis(account,region):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = 'r-kvstore.aliyuncs.com'
    if region == "ap-southeast-1":
        config.endpoint = f'r-kvstore.{region}.aliyuncs.com'
    elif region == "eu-central-1":
        config.endpoint = f'r-kvstore.{region}.aliyuncs.com'
    elif region == "us-west-1":
        config.endpoint = f'r-kvstore.{region}.aliyuncs.com'
    client = R_kvstore20150101Client(config)
    PageNumber = 1
    nextpage = True
    redis_dict = {}
    runtime = util_models.RuntimeOptions()
    try:
        while nextpage:
            describe_instances_request = r_kvstore_20150101_models.DescribeInstancesRequest(
                page_size=50,
                region_id=region,
                page_number=PageNumber
            )
            redisbaseinfo = client.describe_instances_with_options(describe_instances_request, runtime)
            redisbase_list = redisbaseinfo.body.to_map()['Instances']["KVStoreInstance"]

            redis_dict_temp = {i['InstanceId']:{'name':i.get('InstanceName',f"未命名{i['InstanceId']}"),
                                       'domain':i['ConnectionDomain'],
                                       'ip':i.get('PrivateIp','null'),
                                       'port':i['Port'],
                                       'region':region,
                                       'group':group_dict.get(i['ResourceGroupId'],'无'),
                                       'status':i['InstanceStatus'],
                                       'itype':i['ArchitectureType'],
                                       'ver':i['EngineVersion'],
                                       'mem':f"{i['Capacity']}MB",
                                       'exp': '-' if i.get('EndTime',None) == None else i.get('EndTime','-T').split('T')[0]
                                      } for i in redisbase_list}
            redis_dict.update(redis_dict_temp)
            if PageNumber == 1:
                total = redisbaseinfo.body.to_map()['TotalCount']
                pages = math.ceil(total/50)
            PageNumber += 1
            if PageNumber > pages:
                nextpage = False

        count = len(redis_dict)
        off,on = sync_redis.w2consul('alicloud',account,region,redis_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'redis同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/redis/{region}', data)
        logger.info(f'【JOB】===>alicloud_redis {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/redis/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/redis/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/redis/{region}', data)

def rds(account,region):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = 'rds.aliyuncs.com'
    if region == "ap-southeast-1":
        config.endpoint = f'rds.{region}.aliyuncs.com'
    elif region == "eu-central-1":
        config.endpoint = f'rds.{region}.aliyuncs.com'
    elif region == "us-west-1":
        config.endpoint = f'rds.{region}.aliyuncs.com'
    client = Rds20140815Client(config)

    next_token = '0'
    rds_dict = {}
    runtime = util_models.RuntimeOptions()
    try:
        while next_token != '':
            if next_token == '0':
                describe_dbinstances_request = rds_20140815_models.DescribeDBInstancesRequest(
                    max_results=100,
                    engine='MySQL',
                    region_id=region
                )
            else:
                describe_dbinstances_request = rds_20140815_models.DescribeDBInstancesRequest(
                    max_results=100,
                    engine='MySQL',
                    region_id=region,
                    next_token=next_token
                )
            rdsbaseinfo = client.describe_dbinstances_with_options(describe_dbinstances_request, runtime)
            rdsbase_list = rdsbaseinfo.body.to_map()['Items']["DBInstance"]

            rds_dict_temp = {i['DBInstanceId']:{'name':i.get('DBInstanceDescription',f"未命名{i['DBInstanceId']}"),
                                       'domain':i['ConnectionString'],
                                       'ip':i['ConnectionString'],
                                       'port':3306,
                                       'region':region,
                                       'group':group_dict.get(i['ResourceGroupId'],'无'),
                                       'status':i['DBInstanceStatus'],
                                       'itype':i['DBInstanceType'],
                                       'ver':i['EngineVersion'],
                                       'exp': '-' if i.get('ExpireTime',None) == None else i.get('ExpireTime','-T').split('T')[0],
                                       'cpu':'无','mem':'无','disk':'无'
                                      } for i in rdsbase_list}
            rds_dict.update(rds_dict_temp)
            next_token = rdsbaseinfo.body.next_token

        try:
            for iid in rds_dict.keys():
                logger.info(f'【ali_DRS】===> {iid}')
                describe_dbinstance_attribute_request = rds_20140815_models.DescribeDBInstanceAttributeRequest(dbinstance_id=iid)
                rdsplusinfo = client.describe_dbinstance_attribute_with_options(describe_dbinstance_attribute_request, runtime)
                rdsplus_list = rdsplusinfo.body.to_map()['Items']["DBInstanceAttribute"]
                rds_plus = {i['DBInstanceId']:{'port':int(i['Port']),
                                        'cpu':f"{i['DBInstanceCPU']}核",
                                        'mem':f"{round(i['DBInstanceMemory']/1024)}GB",
                                        'disk':f"{i['DBInstanceStorage']}GB"
                                        } for i in rdsplus_list}
                for k,v in rds_plus.items():
                    if k in rds_dict:
                        rds_dict[k].update(v)
        except Exception as e:
            logger.error('DescribeDBInstancesAsCsvRequest ERROR' + f'{e}\n{traceback.format_exc()}')
            
        count = len(rds_dict)
        off,on = sync_rds.w2consul('alicloud',account,region,rds_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'rds同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)
        logger.info(f'【JOB】===>alicloud_rds {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)


def polardb(account, region):
    ak, sk = consul_kv.get_aksk('alicloud', account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak, access_key_secret=sk)
    config.endpoint = 'polardb.aliyuncs.com'
    if region == "ap-southeast-1":
        config.endpoint = f'polardb.{region}.aliyuncs.com'
    elif region == "eu-central-1":
        config.endpoint = f'polardb.{region}.aliyuncs.com'
    elif region == "us-west-1":
        config.endpoint = f'polardb.{region}.aliyuncs.com'
    client = polardb20170801Client(config)  # 使用PolarDB客户端

    page_number = 1
    polardb_dict = {}
    runtime = util_models.RuntimeOptions()
    try:
        while True:
            describe_dbclusters_request = polardb_20170801_models.DescribeDBClustersRequest(
                page_size=100,
                dbtype="MySQL",
                region_id=region,
                page_number=page_number,
            )

            cluster_info = client.describe_dbclusters_with_options(describe_dbclusters_request, runtime)
            cluster_list = cluster_info.body.to_map()['Items']['DBCluster']

            polardb_dict_temp = {i['DBClusterId']: {
                'name': i.get('DBClusterDescription', f"未命名{i['DBClusterId']}"),
                'domain': '无', # todo
                'ip': '无', # todo
                'port': 3306, # todo
                'region': region,
                'group': group_dict.get(i['ResourceGroupId'], '无'),
                'status': i['DBClusterStatus'],
                'itype': '无', # todo
                'ver': i['DBVersion'],
                'exp': '-' if i.get('ExpireTime', None) == None else i.get('ExpireTime', '-T').split('T')[0],
                'cpu': '无', 'mem': '无', 'disk': '无'
            } for i in cluster_list}
            polardb_dict.update(polardb_dict_temp)
            if len(cluster_list) < 100:
                break
            else:
                page_number += 1
        try:
            for iid in polardb_dict.keys():
                logger.info(f'【ali_PolarDB】===> {iid}')
                describe_dbcluster_attribute_request = polardb_20170801_models.DescribeDBClusterEndpointsRequest(
                    dbcluster_id=iid)
                cluster_plus_info = client.describe_dbcluster_endpoints_with_options(
                    describe_dbcluster_attribute_request, runtime)
                cluster_plus_list = cluster_plus_info.body.to_map()['Items']
                polardb_plus = {}
                for i in cluster_plus_list:
                    if i['EndpointType'] == 'Cluster':
                        for address_item in i['AddressItems']:
                            if address_item['NetType'] == 'Private':
                                # 获取 DBClusterId 作为键
                                db_cluster_id = iid
                                # 构建子字典并将其赋值给 polardb_plus
                                polardb_plus[db_cluster_id] = {
                                    'port': int(address_item['Port']),
                                    'domain': address_item['ConnectionString'],
                                    'ip': address_item['IPAddress'],
                                    'itype': i['EndpointType'],
                                }
                                break
                for k, v in polardb_plus.items():
                    if k in polardb_dict:
                        polardb_dict[k].update(v)
        except Exception as e:
            logger.error('DescribeDBClustersAsCsvRequest ERROR' + f'{e}\n{traceback.format_exc()}')

        count = len(polardb_dict)
        off, on = sync_polardb.w2consul('alicloud', account, region, polardb_dict)
        data = {'count': count, 'update': now, 'status': 20000, 'on': on, 'off': off,
                'msg': f'polardb同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/polardb/{region}', data)
        logger.info(f'【JOB】===>alicloud_polardb {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ', 1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/polardb/{region}')
        if data == {}:
            data = {'count': '无', 'update': f'失败{e.code}', 'status': 50000, 'msg': emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/polardb/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count': '无', 'update': f'失败', 'status': 50000, 'msg': str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/polardb/{region}', data)


def mongodb(account, region):
    ak, sk = consul_kv.get_aksk('alicloud', account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak, access_key_secret=sk)
    config.endpoint = 'mongodb.aliyuncs.com'
    if region == "ap-southeast-1":
        config.endpoint = f'mongodb.{region}.aliyuncs.com'
    elif region == "eu-central-1":
        config.endpoint = f'mongodb.{region}.aliyuncs.com'
    elif region == "us-west-1":
        config.endpoint = f'mongodb.{region}.aliyuncs.com'
    client = Dds20151201Client(config)  # 使用MongoDB客户端

    page_number = 1
    mongodb_dict = {}
    runtime = util_models.RuntimeOptions()
    try:
        while True:
            describe_dbinstances_request = dds_20151201_models.DescribeDBInstancesRequest(
                page_size=100,
                page_number=page_number,
                region_id=region
            )
            mongodb_info = client.describe_dbinstances_with_options(describe_dbinstances_request, runtime)
            mongodb_list = mongodb_info.body.to_map()['DBInstances']["DBInstance"]

            mongodb_dict_temp = {i['DBInstanceId']: {
                'name': i.get('DBInstanceDescription', f"未命名{i['DBInstanceId']}"),
                'domain': '无',  # todo
                'ip': '无', # todo
                'port': '无',  # todo
                'region': region,
                'group': group_dict.get(i['ResourceGroupId'], '无'),
                'status': i['DBInstanceStatus'],  # 假设MongoDB的实例有类似的status字段
                'itype': i['DBInstanceType'],  # 替换为MongoDB的实例类型
                'ver': i['EngineVersion'],
                'exp': '-' if i.get('ExpireTime', None) is None else i.get('ExpireTime', '-T').split('T')[0],
                'cpu': '无', 'mem': '无', 'disk': '无'
            } for i in mongodb_list}
            mongodb_dict.update(mongodb_dict_temp)
            if len(mongodb_list) < 100:
                break
            else:
                page_number += 1
        try:
            for iid in mongodb_dict.keys():
                logger.info(f'【ali_MongoDB】===> {iid}')
                describe_dbinstance_attribute_request = dds_20151201_models.DescribeDBInstanceAttributeRequest(dbinstance_id=iid)
                mongodb_plus_info = client.describe_dbinstance_attribute_with_options(describe_dbinstance_attribute_request, runtime)
                mongodb_plus_list = mongodb_plus_info.body.to_map()['DBInstances']["DBInstance"]
                mongodb_plus= {}
                for i in mongodb_plus_list:
                    for replica_set in i['ReplicaSets']['ReplicaSet']:
                        if replica_set['ReplicaSetRole'] == 'Primary':
                            iid = i['DBInstanceId']
                            mongodb_plus[iid] = {
                                'port': int(replica_set['ConnectionPort']),
                                'domain': replica_set['ConnectionDomain'],
                                'ip': replica_set['ConnectionDomain'],
                                'itype': i['DBInstanceType'],
                            }
                            break
                for k, v in mongodb_plus.items():
                    if k in mongodb_dict:
                        mongodb_dict[k].update(v)
        except Exception as e:
            logger.error('DescribeDBInstancesAsCsvRequest ERROR' + f'{e}\n{traceback.format_exc()}')
        count = len(mongodb_dict)
        off, on = sync_mongodb.w2consul('alicloud', account, region, mongodb_dict)
        data = {'count': count, 'update': now, 'status': 20000, 'on': on, 'off': off,
                'msg': f'mongodb同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/mongodb/{region}', data)
        logger.info(f'【JOB】===>alicloud_mongodb {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ', 1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/mongodb/{region}')
        if data == {}:
            data = {'count': '无', 'update': f'失败{e.code}', 'status': 50000, 'msg': emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/mongodb/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count': '无', 'update': '失败', 'status': 50000, 'msg': str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/mongodb/{region}', data)


def clickhouse(account, region):
    ak, sk = consul_kv.get_aksk('alicloud', account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak, access_key_secret=sk)
    config.endpoint = 'clickhouse.aliyuncs.com'
    if region == "ap-southeast-1":
        config.endpoint = f'clickhouse.{region}.aliyuncs.com'
    elif region == "eu-central-1":
        config.endpoint = f'clickhouse.{region}.aliyuncs.com'
    elif region == "us-west-1":
        config.endpoint = f'clickhouse.{region}.aliyuncs.com'
    client = clickhouse20191111Client(config)
    page_number = 1
    clickhouse_dict = {}
    runtime = util_models.RuntimeOptions()
    try:
        while True:
            describe_dbinstances_request = clickhouse_20191111_models.DescribeDBClustersRequest(
                page_size=100,
                page_number=page_number,
                region_id=region
            )
            clickhouse_info = client.describe_dbclusters_with_options(describe_dbinstances_request, runtime)
            clickhouse_list = clickhouse_info.body.to_map()['DBClusters']["DBCluster"]

            clickhouse_dict_temp = {i['DBClusterId']: {
                'name': i.get('DBClusterDescription', f"未命名{i['DBClusterId']}"),
                'domain': i['ConnectionString'],
                'ip': '无',
                'port': '9000',
                'region': region,
                'group': group_dict.get(i['ResourceGroupId'], '无'),
                'status': i['DBClusterStatus'],
                'itype': '社区版',
                'ver': i['DbVersion'],
                'exp': '-' if i.get('ExpireTime', None) is None else i.get('ExpireTime', '-T').split('T')[0],
                'cpu': '无', 'mem': '无', 'disk': '无'
            } for i in clickhouse_list}
            clickhouse_dict.update(clickhouse_dict_temp)
            if len(clickhouse_list) < 100:
                break
            else:
                page_number += 1

        client = clickhouse20230522Client(config)
        page_number = 1
        while True:
            describe_dbinstances_request = clickhouse_20230522_models.DescribeDBInstancesRequest(
                page_size=100,
                page_number=page_number,
                region_id=region
            )
            clickhouse_info = client.describe_dbinstances_with_options(describe_dbinstances_request, runtime)
            clickhouse_list = clickhouse_info.body.to_map()['Data']["DBInstances"]

            clickhouse_dict_temp = {i['DBInstanceId']: {
                'name': i.get('Description', f"未命名{i['DBInstanceId']}"),
                'domain': '无',
                'ip': '无',
                'port': '9000',
                'region': region,
                'group': group_dict.get(i['ResourceGroupId'], '无'),
                'status': i['Status'],
                'itype': '企业版',
                'ver': i['EngineVersion'],
                'exp': '-' if i.get('ExpireTime', None) is None else i.get('ExpireTime', '-T').split('T')[0],
                'cpu': '无', 'mem': '无', 'disk': '无'
            } for i in clickhouse_list}
            clickhouse_dict.update(clickhouse_dict_temp)
            if len(clickhouse_list) < 100:
                break
            else:
                page_number += 1
        try:
            for iid in clickhouse_dict.keys():
                logger.info(f'【ali_Clickhouse】===> {iid}')
                if clickhouse_dict[iid].get('domain') == '无':
                    describe_dbinstance_attribute_request = clickhouse_20230522_models.DescribeEndpointsRequest(region_id=region, dbinstance_id=iid)
                    clickhouse_plus_info = client.describe_endpoints_with_options(describe_dbinstance_attribute_request, runtime)
                    clickhouse_plus_list = clickhouse_plus_info.body.to_map()['Data']["Endpoints"]
                    clickhouse_plus= {}
                    for i in clickhouse_plus_list:
                        if i['NetType'] == 'VPC':
                            clickhouse_plus[iid] = {
                                'domain': i['VpcInstanceId'],
                                'ip': i['IPAddress'],
                            }
                            break
                    for k, v in clickhouse_plus.items():
                        if k in clickhouse_dict:
                            clickhouse_dict[k].update(v)
        except Exception as e:
            logger.error('DescribeDBInstancesAsCsvRequest ERROR' + f'{e}\n{traceback.format_exc()}')
        count = len(clickhouse_dict)
        off, on = sync_clickhouse.w2consul('alicloud', account, region, clickhouse_dict)
        data = {'count': count, 'update': now, 'status': 20000, 'on': on, 'off': off,
                'msg': f'clickhouse同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/clickhouse/{region}', data)
        logger.info(f'【JOB】===>alicloud_clickhouse {account} {region} {data}')
    except TeaException as e:
        emsg = e.message.split('. ', 1)[0]
        logger.error(f"【code:】{e.code}\n【message:】{e.message}\n{traceback.format_exc()}")
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/clickhouse/{region}')
        if data == {}:
            data = {'count': '无', 'update': f'失败{e.code}', 'status': 50000, 'msg': emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/clickhouse/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count': '无', 'update': '失败', 'status': 50000, 'msg': str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/clickhouse/{region}', data)