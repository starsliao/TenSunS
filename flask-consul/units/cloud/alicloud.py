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

import sys,datetime,hashlib
from units import consul_kv,consul_svc
from units.cloud import sync_ecs
from units.cloud import sync_rds
from units.cloud import notify

def exp(account,collect_days,notify_days,notify_amount):
    print(f"=====【阿里云：余额与到期日统计开始：{account}】", flush=True)
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT16:00:00Z')
    collect = (datetime.datetime.utcnow() + datetime.timedelta(days=collect_days+1)).strftime('%Y-%m-%dT16:00:00Z')
    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = f'business.aliyuncs.com'
    client = BssOpenApi20171214Client(config)
    try:
        amount_response = client.query_account_balance()
        if amount_response.body.success:
            available_amount = amount_response.body.data.available_amount
            amount = float(available_amount.replace(',',''))
            consul_kv.put_kv(f'ConsulManager/exp/lists/alicloud/{account}/amount',{'amount':amount})
            print('alicloud',account,f'可用余额:{available_amount}', flush=True)
            amount_dict = {}
            if amount < notify_amount:
                amount_dict = {'amount':amount}
                content = f'### 阿里云账号 {account}：\n### 可用余额：<font color=\"#ff0000\">{amount}</font> 元'
                if exp_config['switch'] and exp_config.get('wecom',False):
                    notify.wecom(wecomwh,content)
                if exp_config['switch'] and exp_config.get('dingding',False):
                    notify.dingding(dingdingwh,content)
                if exp_config['switch'] and exp_config.get('feishu',False):
                    title = '阿里云余额不足通知'
                    md = content
                    notify.feishu(feishuwh,title,md)
        else:
            print(f'查询失败，Code:{amount_response.body.code}, 信息:{amount_response.body.message}, requestId:{amount_response.body.request_id}', flush=True)
    except Exception as e:
        print('==ERROR==',e,flush=True)
        raise
    query_available_instances_request = bss_open_api_20171214_models.QueryAvailableInstancesRequest(
        renew_status='ManualRenewal',end_time_start=now,end_time_end=collect)
    runtime = util_models.RuntimeOptions()
    try:
        exp = client.query_available_instances_with_options(query_available_instances_request, runtime)
        exp_list = exp.body.to_map()['Data']['InstanceList']
    except Exception as e:
        #exp_list = []
        print('==ERROR==',e,flush=True)
        raise
    exp_dict = {}
    isnotify_list = consul_kv.get_keys_list(f'ConsulManager/exp/isnotify/alicloud/{account}')
    isnotify_list = [i.split('/')[-1] for i in isnotify_list]
    notify_dict = {}
    for i in exp_list:
        notify_id = hashlib.md5(str(i).encode(encoding='UTF-8')).hexdigest()
        endtime = datetime.datetime.strptime(i['EndTime'],'%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
        endtime_str = endtime.strftime('%Y-%m-%d')
        iname = consul_svc.get_sid(i['InstanceID'])['instance']['Meta']['name'] if i['ProductCode'] == 'ecs' else 'Null'
        exp_dict[i['InstanceID']] = {'Region':i.get('Region','Null'),'Product':i['ProductCode'],
            'Name':iname,'EndTime':endtime_str,'notify_id':notify_id,
            'Ptype':i.get('ProductType',i['ProductCode'])}
        if (endtime - datetime.datetime.now()).days < notify_days and notify_id not in isnotify_list:
            notify_dict[i['InstanceID']] = exp_dict[i['InstanceID']]
    consul_kv.put_kv(f'ConsulManager/exp/lists/alicloud/{account}/exp', exp_dict)
    exp_config = consul_kv.get_value('ConsulManager/exp/config')
    wecomwh = exp_config.get('wecomwh','')
    dingdingwh = exp_config.get('dingdingwh','')
    feishuwh = exp_config.get('feishuwh','')
    if notify_dict != {}:
        msg = [f'### 阿里云账号 {account}：\n### 以下资源到期日小于 {notify_days} 天：']
        for k,v in notify_dict.items():
            iname = k if v['Name'] == 'Null' else v['Name']
            msg.append(f"- {v['Region']}：{v['Product']}：{iname}：<font color=\"#ff0000\">{v['EndTime']}</font>")
        content = '\n'.join(msg)
        if exp_config['switch'] and exp_config.get('wecom',False):
            notify.wecom(wecomwh,content)
        if exp_config['switch'] and exp_config.get('dingding',False):
            notify.dingding(dingdingwh,content)
        if exp_config['switch'] and exp_config.get('feishu',False):
            title = '阿里云资源到期通知'
            md = content
            notify.feishu(feishuwh,title,md)
    print(f"=====【阿里云：余额与到期日统计结束：{account}】", flush=True)

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

def rds(account,region):
    ak,sk = consul_kv.get_aksk('alicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/alicloud/group/{account}')

    config = open_api_models.Config(access_key_id=ak,access_key_secret=sk)
    config.endpoint = 'rds.aliyuncs.com'
    client = Rds20140815Client(config)

    try:
        runtime = util_models.RuntimeOptions()
        describe_dbinstances_request = rds_20140815_models.DescribeDBInstancesRequest(
            max_results=100,
            region_id=region
        )
        rdsbaseinfo = client.describe_dbinstances_with_options(describe_dbinstances_request, runtime)
        rdsbase_list = rdsbaseinfo.body.to_map()['Items']["DBInstance"]


        describe_dbinstances_as_csv_request = rds_20140815_models.DescribeDBInstancesAsCsvRequest(region_id=region)
        rdsplusinfo = client.describe_dbinstances_as_csv_with_options(describe_dbinstances_as_csv_request, runtime)
        rdsplus_list = rdsplusinfo.body.to_map()['Items']["DBInstanceAttribute"]

        rds_dict = {i['DBInstanceId']:{'name':i.get('DBInstanceDescription',f"未命名{i['DBInstanceId']}"),
                                       'domain':i['ConnectionString'],
                                       'ip':i['ConnectionString'],
                                       'port':3306,
                                       'region':region,
                                       'group':group_dict.get(i['ResourceGroupId'],'无'),
                                       'status':i['DBInstanceStatus'],
                                       'itype':i['DBInstanceType'],
                                       'ver':i['EngineVersion'],
                                       'exp': '-' if i['ExpireTime'] == None else i['ExpireTime'].split('T')[0]
                                      } for i in rdsbase_list}

        rds_plus = {i['DBInstanceId']:{'port':int(i['Port']),
                                       'cpu':f"{i['DBInstanceCPU']}核",
                                       'mem':f"{round(i['DBInstanceMemory']/1024)}GB",
                                       'disk':f"{i['DBInstanceStorage']}GB"
                                      } for i in rdsplus_list}
        for k,v in rds_plus.items():
            rds_dict[k].update(v)

        count = len(rds_dict)
        off,on = sync_rds.w2consul('alicloud',account,region,rds_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'rds同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)
        print('【JOB】===>', 'alicloud_rds', account,region, data, flush=True)
    except TeaException as e:
        emsg = e.message.split('. ',1)[0]
        print("【code:】",e.code,"\n【message:】",emsg, flush=True)
        data = consul_kv.get_value(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.code}','status':50000,'msg':emsg}
        else:
            data['update'] = f'失败{e.code}'
            data['msg'] = emsg
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)
    except Exception as e:
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/alicloud/{account}/rds/{region}', data)
