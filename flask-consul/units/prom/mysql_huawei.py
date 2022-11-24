from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkces.v1.region.ces_region import CesRegion
from huaweicloudsdkcore.exceptions import exceptions
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
    metric_name_dict = {"rds001_cpu_util":["# HELP mysql_cpu_util CPU使用率","# TYPE mysql_cpu_util gauge"],
                        "rds002_mem_util":["# HELP mysql_mem_util 内存使用率","# TYPE mysql_mem_util gauge"],
                        "rds039_disk_util":["# HELP mysql_disk_util 磁盘使用率","# TYPE mysql_disk_util gauge"],
                        "rds074_slow_queries":["# HELP mysql_slow_queries 每分钟慢SQL","# TYPE mysql_slow_queries gauge"],
                        "rds081_vm_ioutils":["# HELP mysql_io_util 磁盘I/O使用率","# TYPE mysql_io_util gauge"],
                        "rds072_conn_usage":["# HELP mysql_conn_util 连接数使用率","# TYPE mysql_conn_util gauge"]
                       }
    metric_body_list = []
    now = int(datetime.now().timestamp()*1000)
    rds_list = consul_kv.get_services_list_by_region(f'{vendor}_{account}_rds',region)
    try:
        for i in metric_name_dict.keys():
            for rdsid in rds_list:
                metric_body_list.append(MetricInfo(namespace="SYS.RDS",metric_name=i,dimensions=[MetricsDimension(name="rds_cluster_id",value=rdsid)]))

        request = BatchListMetricDataRequest()
        request.body = BatchListMetricDataRequestBody(to=now,_from=now-180000,filter="max",period="1",metrics=metric_body_list)
        response = client.batch_list_metric_data(request).to_dict()
        for i in response['metrics']:
            rdsid= i['dimensions'][0]['value']
            try:
                value = i['datapoints'][-1]['max']
                ts = i['datapoints'][-1]['timestamp']
            except:
                value = -1
                ts = now
            metric = i['metric_name']
            prom_metric_name = metric_name_dict[metric][0].split()[2]
            metric_name_dict[metric].append(f'{prom_metric_name}{{iid="{rdsid}"}} {float(value)} {ts}')
        prom_metric_list = []
        for x in metric_name_dict.values():
            prom_metric_list = prom_metric_list + x
        return prom_metric_list
    except exceptions.ClientRequestException as e:
        print(e.status_code,flush=True)
        print(e.request_id,flush=True)
        print(e.error_code,flush=True)
        print(e.error_msg,flush=True)

