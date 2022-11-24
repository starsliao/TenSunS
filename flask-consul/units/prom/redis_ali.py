from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricLastRequest import DescribeMetricLastRequest
from datetime import datetime
from units import consul_kv
import json

def exporter(vendor,account,region):
    ak,sk = consul_kv.get_aksk(vendor,account)
    client_redismonit = AcsClient(ak, sk, region)
    request_redismonit = DescribeMetricLastRequest()
    request_redismonit.set_accept_format('json')
    request_redismonit.set_Namespace("acs_kvstore")
    metric_name_dict = {"CpuUsage":["# HELP redis_cpu_util CPU使用率","# TYPE redis_cpu_util gauge"],
                        "MemoryUsage":["# HELP redis_mem_util 内存使用率","# TYPE redis_mem_util gauge"],
                        "ConnectionUsage":["# HELP redis_conn_util 连接数使用率","# TYPE redis_conn_util gauge"],
                        "IntranetInRatio":["# HELP redis_netin_util 写入带宽使用率","# TYPE redis_netin_util gauge"],
                        "IntranetOutRatio":["# HELP redis_netout_util 读取带宽使用率","# TYPE redis_netout_util gauge"]
                       }
    for i in metric_name_dict.keys():
        request_redismonit.set_MetricName(i)
        response_redismonit = json.loads(client_redismonit.do_action_with_exception(request_redismonit))
        instance = json.loads(response_redismonit["Datapoints"])
        prom_metric_name = metric_name_dict[i][0].split()[2]
        for j in instance:
            iid,max,ts = j["instanceId"],j["Maximum"],j["timestamp"]
            metric_name_dict[i].append(f'{prom_metric_name}{{iid="{iid}"}} {float(max)} {ts}')
    prom_metric_list = []
    for x in metric_name_dict.values():
        prom_metric_list = prom_metric_list + x
    return prom_metric_list
