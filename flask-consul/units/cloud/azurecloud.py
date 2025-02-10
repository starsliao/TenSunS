from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.rdbms import MySQLManagementClient
from azure.mgmt.redis import RedisManagementClient
from azure.core.exceptions import AzureError

import sys, datetime, hashlib, math, traceback
from units import consul_kv, consul_svc
from units.cloud import sync_ecs, sync_rds, sync_redis, notify
from units.config_log import *

def exp(account,collect_days,notify_days,notify_amount):
    pass

def group(account):
    """同步Azure资源组信息"""
    try:
        now = datetime.datetime.now().strftime('%m.%d/%H:%M')
        # 获取Azure认证信息
        tenant_id, client_id, client_secret = consul_kv.get_azure_credentials(account)
        
        # 创建认证客户端
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # 获取资源组信息
        from azure.mgmt.resource import ResourceManagementClient
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        group_dict = {}
        for group in resource_client.resource_groups.list():
            group_dict[group.name] = {
                'name': group.name,
                'location': group.location,
                'tags': group.tags or {}
            }
            
        # 保存到consul
        consul_kv.put_kv(f'ConsulManager/assets/azure/group/{account}', group_dict)
        count = len(group_dict)
        data = {
            'count': count,
            'update': now,
            'status': 20000,
            'msg': f'同步资源组成功！总数：{count}'
        }
        consul_kv.put_kv(f'ConsulManager/record/jobs/azure/{account}/group', data)
        logger.info(f'【JOB】===>azure_group {account} {data}')
        
    except AzureError as e:
        handle_azure_error(e, account, 'group')
    except Exception as e:
        handle_general_error(e, account, 'group')

def vm(account, region, isextip=False):
    """同步Azure虚拟机信息"""
    try:
        now = datetime.datetime.now().strftime('%m.%d/%H:%M')
        # 获取认证信息
        tenant_id, client_id, client_secret = consul_kv.get_azure_credentials(account)
        subscription_id = consul_kv.get_azure_subscription(account)
        
        # 创建认证客户端
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # 创建计算管理客户端
        compute_client = ComputeManagementClient(credential, subscription_id)
        
        ecs_dict = {}
        # 获取虚拟机列表
        for vm in compute_client.virtual_machines.list_all():
            vm_id = vm.id.split('/')[-1]
            vm_info = compute_client.virtual_machines.get(
                vm.id.split('/')[4],  # 资源组名称
                vm.name,
                expand='instanceView'
            )
            
            ecs_dict_temp = {vm_id: {}}
            ecs_dict_temp[vm_id].update({
                'name': vm.name,
                'group': vm.id.split('/')[4],  # 资源组名称
                'ostype': 'windows' if vm.os_profile.windows_configuration else 'linux',
                'status': vm_info.instance_view.statuses[-1].display_status,
                'region': vm.location,
                'ip': get_vm_ip(vm, isextip),
                'cpu': f"{vm.hardware_profile.vm_size.split('_')[1]}核",
                'mem': get_vm_memory(vm.hardware_profile.vm_size),
                'exp': get_vm_billing_type(vm)
            })
            ecs_dict.update(ecs_dict_temp)
            
        # 同步到consul
        count = len(ecs_dict)
        off, on = sync_ecs.w2consul('azure', account, region, ecs_dict)
        data = {
            'count': count,
            'update': now,
            'status': 20000,
            'on': on,
            'off': off,
            'msg': f'VM同步成功！总数：{count}，开机：{on}，关机：{off}'
        }
        consul_kv.put_kv(f'ConsulManager/record/jobs/azure/{account}/vm/{region}', data)
        logger.info(f'【JOB】===>azure_vm {account} {region} {data}')
        
    except AzureError as e:
        handle_azure_error(e, account, 'vm', region)
    except Exception as e:
        handle_general_error(e, account, 'vm', region)

def redis(account, region):
    """同步Azure Redis缓存信息"""
    try:
        now = datetime.datetime.now().strftime('%m.%d/%H:%M')
        # 获取认证信息
        tenant_id, client_id, client_secret = consul_kv.get_azure_credentials(account)
        subscription_id = consul_kv.get_azure_subscription(account)
        
        # 创建Redis管理客户端
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        redis_client = RedisManagementClient(credential, subscription_id)
        
        redis_dict = {}
        # 获取Redis实例列表
        for redis_cache in redis_client.redis.list():
            cache_id = redis_cache.id.split('/')[-1]
            redis_dict_temp = {cache_id: {}}
            redis_dict_temp[cache_id].update({
                'name': redis_cache.name,
                'domain': redis_cache.host_name,
                'ip': redis_cache.host_name,
                'port': redis_cache.port,
                'region': redis_cache.location,
                'group': redis_cache.id.split('/')[4],  # 资源组名称
                'status': redis_cache.provisioning_state,
                'itype': 'redis',
                'ver': redis_cache.redis_version,
                'mem': f"{redis_cache.sku.capacity}GB",
                'exp': get_redis_billing_type(redis_cache)
            })
            redis_dict.update(redis_dict_temp)
            
        # 同步到consul
        count = len(redis_dict)
        off, on = sync_redis.w2consul('azure', account, region, redis_dict)
        data = {
            'count': count,
            'update': now,
            'status': 20000,
            'on': on,
            'off': off,
            'msg': f'Redis同步成功！总数：{count}，开机：{on}，关机：{off}'
        }
        consul_kv.put_kv(f'ConsulManager/record/jobs/azure/{account}/redis/{region}', data)
        logger.info(f'【JOB】===>azure_redis {account} {region} {data}')
        
    except AzureError as e:
        handle_azure_error(e, account, 'redis', region)
    except Exception as e:
        handle_general_error(e, account, 'redis', region)

# 辅助函数
def handle_azure_error(e: AzureError, account: str, resource_type: str, region: str = None):
    """处理Azure API错误"""
    emsg = str(e)
    logger.error(f"【Azure Error】\n【message:】{emsg}\n{traceback.format_exc()}")
    
    # 构建错误路径
    error_path = f'ConsulManager/record/jobs/azure/{account}/{resource_type}'
    if region:
        error_path = f'{error_path}/{region}'
    
    # 获取现有数据
    data = consul_kv.get_value(error_path)
    if data == {}:
        data = {'count': '无', 'update': '失败', 'status': 50000, 'msg': emsg}
    else:
        data['update'] = '失败'
        data['msg'] = emsg
    
    consul_kv.put_kv(error_path, data)

def handle_general_error(e: Exception, account: str, resource_type: str, region: str = None):
    """处理一般错误"""
    logger.error(f'{e}\n{traceback.format_exc()}')
    
    # 构建错误路径
    error_path = f'ConsulManager/record/jobs/azure/{account}/{resource_type}'
    if region:
        error_path = f'{error_path}/{region}'
    
    data = {'count': '无', 'update': '失败', 'status': 50000, 'msg': str(e)}
    consul_kv.put_kv(error_path, data)

def get_vm_ip(vm, isextip=False):
    """获取虚拟机IP地址"""
    if isextip:
        # 获取公网IP
        return vm.network_profile.network_interfaces[0].ip_configurations[0].public_ip_address.ip_address
    else:
        # 获取私网IP
        return vm.network_profile.network_interfaces[0].ip_configurations[0].private_ip_address

def get_vm_memory(vm_size):
    """根据VM规格获取内存大小"""
    # 这里需要实现VM规格到内存大小的映射
    size_memory_map = {
        'Standard_DS1_v2': '3.5GB',
        'Standard_DS2_v2': '7GB',
        # ... 其他规格映射
    }
    return size_memory_map.get(vm_size, '0')

def get_vm_billing_type(vm):
    """获取虚拟机计费类型"""
    # 根据Azure虚拟机的计费属性判断
    return '按量' if vm.billing_profile.max_price is None else '包年包月'

def get_redis_billing_type(redis_cache):
    """获取Redis实例计费类型"""
    # 根据Redis实例的计费属性判断
    return '按量'  # 或根据实际情况判断