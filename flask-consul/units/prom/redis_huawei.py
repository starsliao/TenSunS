from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkces.v1.region.ces_region import CesRegion
from huaweicloudsdkces.v1 import *
from datetime import datetime
from units import consul_kv

def exporter(vendor,account,region):
    ak,sk = consul_kv.get_aksk(vendor,account)
    credentials = BasicCredentials(ak, sk)
    client = CesClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(CesRegion.value_of(region)) \
        .build()
    metric_name_dict = {"cpu_usage":["# HELP redis_cpu_util CPU使用率","# TYPE redis_cpu_util gauge"],
                        "memory_usage":["# HELP redis_mem_util 内存使用率","# TYPE redis_mem_util gauge"],
                        "keyspace_hits_perc":["# HELP redis_hits_util 缓存命中率","# TYPE redis_hits_util gauge"],
                        "total_connections_received":["# HELP redis_newconn_count 每分钟新建的连接数","# TYPE redis_newconn_count gauge"],
                        "rx_controlled":["# HELP redis_rx_controlled 每分钟被流控的次数","# TYPE redis_rx_controlled gauge"],
                        "is_slow_log_exist":["# HELP redis_slow_log 慢日志情况","# TYPE redis_slow_log gauge"],
                       }
    metric_body_list = []
    now = int(datetime.now().timestamp()*1000)
    redis_list = consul_kv.get_services_list_by_region(f'{vendor}_{account}_redis',region)
    for i in metric_name_dict.keys():
        for id in redis_list:
            metric_body_list.append(MetricInfo(namespace="SYS.DCS",metric_name=i,dimensions=[MetricsDimension(name="dcs_instance_id",value=id)]))

    request = BatchListMetricDataRequest()
    request.body = BatchListMetricDataRequestBody(to=now,_from=now-180000,filter="max",period="1",metrics=metric_body_list)
    response = client.batch_list_metric_data(request).to_dict()
    for i in response['metrics']:
        id= i['dimensions'][0]['value']
        try:
            value = i['datapoints'][-1]['max']
            ts = i['datapoints'][-1]['timestamp']
        except:
            value = -1
            ts = now
        metric = i['metric_name']
        prom_metric_name = metric_name_dict[metric][0].split()[2]
        metric_name_dict[metric].append(f'{prom_metric_name}{{iid="{id}"}} {float(value)} {ts}')
    prom_metric_list = []
    for x in metric_name_dict.values():
        prom_metric_list = prom_metric_list + x
    return prom_metric_list
