import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.monitor.v20180724 import monitor_client, models
from datetime import datetime,timedelta
from units import consul_kv
from units.config_log import *

def exporter(vendor,account,region):
    ak,sk = consul_kv.get_aksk(vendor,account)
    cred = credential.Credential(ak,sk)
    client = monitor_client.MonitorClient(cred, region)
    req = models.GetMonitorDataRequest()
    metric_name_dict = {"CpuMaxUtil":["# HELP redis_cpu_util 实例中节点最大CPU使用率","# TYPE redis_cpu_util gauge"],
                        "MemMaxUtil":["# HELP redis_mem_util 实例中节点最大内存使用率","# TYPE redis_mem_util gauge"],
                        "ConnectionsUtil":["# HELP redis_conn_util 连接使用率","# TYPE redis_conn_util gauge"],
                        "CmdBigValue":["# HELP redis_big_count 每秒请求命令大小超过32KB的执行次数","# TYPE redis_big_count gauge"],
                        "CmdSlow":["# HELP redis_slow_count 执行时延大于slowlog-log-slower-than配置的命令次数","# TYPE redis_slow_count gauge"],
                        "InFlowLimit":["# HELP redis_inlimit_count 入流量触发限流的次数","# TYPE redis_inlimit_count gauge"],
                        "OutFlowLimit":["# HELP redis_outlimit_count 出流量触发限流的次数","# TYPE redis_outlimit_count gauge"]
                       }
    redis_list = consul_kv.get_services_list_by_region(f'{vendor}_{account}_redis',region)
    redis_list = list(redis_list)
    redis_list_10 = [redis_list[i:i + 10] for i in range(0, len(redis_list), 10)]
    for i in metric_name_dict.keys():
        for rediss in redis_list_10:
            starttime = (datetime.now() + timedelta(minutes=-1)).strftime('%Y-%m-%dT%H:%M:%S+08:00')
            ins_list = [{"Dimensions":[{"Name":"instanceid","Value":x}]} for x in rediss]
            params = {"Namespace":"QCE/REDIS_MEM","MetricName":i,"Period":60,"StartTime":starttime,"Instances":ins_list}
            req.from_json_string(json.dumps(params))
            resp = client.GetMonitorData(req)
            metric_list = resp.DataPoints
            for metrics in metric_list:
                try:
                    iid = metrics.Dimensions[0].Value
                    value = metrics.Values[-1]
                    ts = metrics.Timestamps[-1]*1000
                    prom_metric_name = metric_name_dict[i][0].split()[2]
                    metric_name_dict[i].append(f'{prom_metric_name}{{iid="{iid}"}} {float(value)} {ts}')
                except Exception as e:
                    logger.error(f"【redis_tencent：prom-metrics-ERROR】{e}")
    prom_metric_list = []
    for x in metric_name_dict.values():
        prom_metric_list = prom_metric_list + x
    return prom_metric_list
