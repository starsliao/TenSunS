from huaweicloudsdkcore.auth.credentials import GlobalCredentials,BasicCredentials
from huaweicloudsdkeps.v1.region.eps_region import EpsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbss.v2.region.bss_region import BssRegion
from huaweicloudsdkeps.v1 import *
from huaweicloudsdkbss.v2 import *
from huaweicloudsdkecs.v2 import *
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkdcs.v2 import *
from huaweicloudsdkdcs.v2.region.dcs_region import DcsRegion
from huaweicloudsdkrds.v3 import *
from huaweicloudsdkrds.v3.region.rds_region import RdsRegion
import sys,datetime,hashlib,traceback
from units.cloud import sync_ecs
from units.cloud import sync_rds
from units.cloud import sync_redis
from units.cloud import notify
from units.config_log import *
from units import consul_kv,consul_svc

def exp(account,collect_days,notify_days,notify_amount):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT16:00:00Z')
    collect = (datetime.datetime.utcnow() + datetime.timedelta(days=collect_days+1)).strftime('%Y-%m-%dT16:00:00Z')
    credentials = GlobalCredentials(ak, sk)
    try:
        client = BssClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()
        request = ListPayPerUseCustomerResourcesRequest()
        listQueryResourcesReqStatusListbody = [2]
        request.body = QueryResourcesReq(
            expire_time_end=collect,
            limit=500,
            status_list=listQueryResourcesReqStatusListbody,
            only_main_resource=1
        )
        exp_list = client.list_pay_per_use_customer_resources(request).to_dict()['data']
        exp_dict = {}
        isnotify_list = consul_kv.get_keys_list(f'ConsulManager/exp/isnotify/huaweicloud/{account}')
        isnotify_list = [i.split('/')[-1] for i in isnotify_list]
        notify_dict = {}
        amount_dict = {}
        for i in exp_list:
            endtime = datetime.datetime.strptime(i['expire_time'],'%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8.1)
            endtime_str = endtime.strftime('%Y-%m-%d')
            i['service_type_code'].replace('hws.service.type.','')
            if i['expire_policy'] not in [1,3,4]:
                notify_id = hashlib.md5(str(i).encode(encoding='UTF-8')).hexdigest()
                exp_dict[i['resource_id']] = {'Region':i['region_code'],'Product':i['resource_spec_code'],
                    'EndTime':endtime_str,'Name':i['resource_name'],'Ptype':i['resource_type_code'],'notify_id':notify_id}
                if (endtime - datetime.datetime.now()).days < notify_days and notify_id not in isnotify_list:
                    notify_dict[i['resource_id']] = exp_dict[i['resource_id']]

        consul_kv.put_kv(f'ConsulManager/exp/lists/huaweicloud/{account}/exp', exp_dict)

        request = ShowCustomerAccountBalancesRequest()
        response = client.show_customer_account_balances(request).to_dict()['account_balances']
        amount = [i['amount'] for i in response if i['account_type'] == 1][0]
        consul_kv.put_kv(f'ConsulManager/exp/lists/huaweicloud/{account}/amount',{'amount':amount})
        if amount < notify_amount:
            amount_dict = {'amount':amount}
        exp_config = consul_kv.get_value('ConsulManager/exp/config')
        wecomwh = exp_config.get('wecomwh','')
        dingdingwh = exp_config.get('dingdingwh','')
        feishuwh = exp_config.get('feishuwh','')
        isatall = exp_config.get('isatall', True)
        if notify_dict != {}:
            msg = [f'### 华为云账号 {account}：\n### 以下资源到期日小于 {notify_days} 天：']
            for k,v in notify_dict.items():
                msg.append(f"- {v['Region']}：{v['Product']}：{v['Name']}：<font color=\"#ff0000\">{v['EndTime']}</font>")
            content = '\n'.join(msg)
            if exp_config['switch'] and exp_config.get('wecom',False):
                notify.wecom(wecomwh,content)
            if exp_config['switch'] and exp_config.get('dingding',False):
                notify.dingding(dingdingwh,content,isatall)
            if exp_config['switch'] and exp_config.get('feishu',False):
                title = '华为云资源到期通知'
                md = content
                notify.feishu(feishuwh,title,md,isatall)
        if amount_dict != {}:
            content = f'### 华为云账号 {account}：\n### 可用余额：<font color=\"#ff0000\">{amount}</font> 元'
            if exp_config['switch'] and exp_config.get('wecom',False):
                notify.wecom(wecomwh,content)
            if exp_config['switch'] and exp_config.get('dingding',False):
                notify.dingding(dingdingwh,content,isatall)
            if exp_config['switch'] and exp_config.get('feishu',False):
                title = '华为云余额不足通知'
                md = content
                notify.feishu(feishuwh,title,md,isatall)

    except exceptions.ClientRequestException as e:
        logger.error(e.status_code)
        logger.error(e.request_id)
        logger.error(e.error_code)
        logger.error(f'{e.error_msg}\n{traceback.format_exc()}')

def group(account):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
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
        logger.info(f'【JOB】===>huaweicloud_group {account} {data}')
    except exceptions.ClientRequestException as e:
        logger.error(e.status_code)
        logger.error(e.request_id)
        logger.error(e.error_code)
        logger.error(f'{e.error_msg}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/group')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/group', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/group', data)

def ecs(account,region,isextip=False):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/huaweicloud/group/{account}')
    credentials = BasicCredentials(ak, sk)
    try:
        paycredentials = GlobalCredentials(ak, sk)
        payclient = BssClient.new_builder() \
            .with_credentials(paycredentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()
        payrequest = ListPayPerUseCustomerResourcesRequest()
        listQueryResourcesReqStatusListbody = [2]
        payrequest.body = QueryResourcesReq(
            limit=500,
            status_list=listQueryResourcesReqStatusListbody,
            only_main_resource=1
        )
        exp_list = payclient.list_pay_per_use_customer_resources(payrequest).to_dict()['data']
        #logger.info(exp_list)
        exp_dict = {}
        for i in exp_list:
            if i['service_type_code'].replace('hws.service.type.',''):
               #exp_dict[i['resource_id']] = datetime.datetime.strptime(i['expire_time'],'%Y-%m-%d')
               exp_dict[i['resource_id']] = i['expire_time'].split('T')[0]
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
                             'exp': exp_dict.get(i['id'], '-')
                            } for i in info}

        if isextip:
            for i in info:
                try:
                    pubip_list = [x.addr for x in i['addresses'][i['metadata']['vpc_id']] if 'floating' in str(x)]
                    if pubip_list:
                        ecs_dict[i['id']]['ip'] = pubip_list[0]
                    else:
                        pass
                except:
                    pass
        count = len(ecs_dict)
        off,on = sync_ecs.w2consul('huaweicloud',account,region,ecs_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'ECS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)
        logger.info(f'【JOB】===>huaweicloud_ecs {account} {region} {data}')
    except exceptions.ClientRequestException as e:
        logger.error(e.status_code)
        logger.error(e.request_id)
        logger.error(e.error_code)
        logger.error(f'{e.error_msg}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'on':0,'off':0,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/ecs/{region}', data)


def rds(account,region):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/huaweicloud/group/{account}')
    credentials = BasicCredentials(ak, sk)
    try:
        client = RdsClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(RdsRegion.value_of(region)) \
            .build()
        request = ListInstancesRequest()
        request.datastore_type = "MySQL"
        request.limit = 100
        info = client.list_instances(request).to_dict()['instances']

        rds_dict = {i['id']:{'name':i['name'],
                             'domain':i['private_dns_names'][0],
                             'ip':i['private_ips'][0],
                             'port':i['port'],
                             'region':region,
                             'group':group_dict[i['enterprise_project_id']],
                             'status':i['status'],
                             'itype':i['type'],
                             'ver':i['datastore']['version'],
                             'cpu':f"{i['cpu']}核",
                             'mem':f"{i['mem']}GB",
                             'disk':f"{i['volume']['size']}GB",
                             'exp': '-' if i['expiration_time'] == None else i['expiration_time'].split('T')[0]
                            } for i in info if i['datastore']['type'] == 'MySQL'}
        count = len(rds_dict)
        off,on = sync_rds.w2consul('huaweicloud',account,region,rds_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'RDS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/rds/{region}', data)
        logger.info(f'【JOB】===>huaweicloud_rds {account} {region} {data}')
    except exceptions.ClientRequestException as e:
        logger.error(e.status_code)
        logger.error(e.request_id)
        logger.error(e.error_code)
        logger.error(f'{e.error_msg}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/rds/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'on':0,'off':0,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/rds/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/rds/{region}', data)

def redis(account,region):
    ak,sk = consul_kv.get_aksk('huaweicloud',account)
    now = datetime.datetime.now().strftime('%m.%d/%H:%M')
    group_dict = consul_kv.get_value(f'ConsulManager/assets/huaweicloud/group/{account}')
    credentials = BasicCredentials(ak, sk)
    try:
        client = DcsClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(DcsRegion.value_of(region)) \
            .build()
        request = ListInstancesRequest()
        request.include_failure = "false"
        request.include_delete = "false"
        request.limit = 1000
        info = client.list_instances(request).to_dict()['instances']

        redis_dict = {i['instance_id']:{'name':i['name'],
                             'domain':i['domain_name'],
                             'ip':i['ip'],
                             'port':i['port'],
                             'region':region,
                             'group':group_dict[i['enterprise_project_id']],
                             'status':i['status'],
                             'itype':i['spec_code'],
                             'ver':i['engine_version'],
                             'mem':f"{i['max_memory']}MB",
                             'exp': '-'
                            } for i in info}
        count = len(redis_dict)
        off,on = sync_redis.w2consul('huaweicloud',account,region,redis_dict)
        data = {'count':count,'update':now,'status':20000,'on':on,'off':off,'msg':f'REDIS同步成功！总数：{count}，开机：{on}，关机：{off}'}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/redis/{region}', data)
        logger.info(f'【JOB】===>huaweicloud_redis {account} {region} {data}')
    except exceptions.ClientRequestException as e:
        logger.error(e.status_code)
        logger.error(e.request_id)
        logger.error(e.error_code)
        logger.error(f'{e.error_msg}\n{traceback.format_exc()}')
        data = consul_kv.get_value(f'ConsulManager/record/jobs/huaweicloud/{account}/redis/{region}')
        if data == {}:
            data = {'count':'无','update':f'失败{e.status_code}','status':50000,'on':0,'off':0,'msg':e.error_msg}
        else:
            data['update'] = f'失败{e.status_code}'
            data['msg'] = e.error_msg
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/redis/{region}', data)
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        data = {'count':'无','update':f'失败','status':50000,'msg':str(e)}
        consul_kv.put_kv(f'ConsulManager/record/jobs/huaweicloud/{account}/redis/{region}', data)

