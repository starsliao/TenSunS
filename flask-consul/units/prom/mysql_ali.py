from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricLastRequest import DescribeMetricLastRequest
from datetime import datetime
from units import consul_kv
import json

def exporter(vendor,account,region):
    ak,sk = consul_kv.get_aksk(vendor,account)
    client_rdsmonit = AcsClient(ak, sk, region)
    request_rdsmonit = DescribeMetricLastRequest()
    request_rdsmonit.set_accept_format('json')
    request_rdsmonit.set_Namespace("acs_rds_dashboard")
    metric_name_dict = {"CpuUsage":["# HELP mysql_cpu_util CPU使用率","# TYPE mysql_cpu_util gauge"],
                        "MemoryUsage":["# HELP mysql_mem_util 内存使用率","# TYPE mysql_mem_util gauge"],
                        "DiskUsage":["# HELP mysql_disk_util 磁盘使用率","# TYPE mysql_disk_util gauge"],
                        "IOPSUsage":["# HELP mysql_io_util 磁盘I/O使用率","# TYPE mysql_io_util gauge"],
                        "ConnectionUsage":["# HELP mysql_conn_util 连接数使用率","# TYPE mysql_conn_util gauge"]
                       }
    for i in metric_name_dict.keys():
        request_rdsmonit.set_MetricName(i)
        response_rdsmonit = json.loads(client_rdsmonit.do_action_with_exception(request_rdsmonit))
        instance = json.loads(response_rdsmonit["Datapoints"])
        prom_metric_name = metric_name_dict[i][0].split()[2]
        for j in instance:
            iid,max,ts = j["instanceId"],j["Maximum"],j["timestamp"]
            metric_name_dict[i].append(f'{prom_metric_name}{{iid="{iid}"}} {float(max)} {ts}')
    prom_metric_list = []
    for x in metric_name_dict.values():
        prom_metric_list = prom_metric_list + x
    return prom_metric_list
