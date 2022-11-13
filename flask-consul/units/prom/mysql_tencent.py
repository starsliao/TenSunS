import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.monitor.v20180724 import monitor_client, models
from datetime import datetime,timedelta
from units import consul_kv

def exporter(vendor,account,region):
    ak,sk = consul_kv.get_aksk(vendor,account)
    cred = credential.Credential(ak,sk)
    client = monitor_client.MonitorClient(cred, region)
    req = models.GetMonitorDataRequest()
    metric_name_dict = {"CpuUseRate":["# HELP mysql_cpu_util CPU使用率","# TYPE mysql_cpu_util gauge"],
                        "MemoryUseRate":["# HELP mysql_mem_util 内存使用率","# TYPE mysql_mem_util gauge"],
                        "IOPS":["# HELP mysql_iops_count 每秒I/O请求数","# TYPE mysql_iops_count gauge"],
                        "VolumeRate":["# HELP mysql_disk_util 磁盘使用率","# TYPE mysql_disk_util gauge"],
                        "IopsUseRate":["# HELP mysql_io_util 磁盘I/O使用率","# TYPE mysql_io_util gauge"]
                       }
    rds_list = consul_kv.get_services_list_by_region(f'{vendor}_{account}_rds',region)
    rds_list = list(rds_list)
    rds_list_10 = [rds_list[i:i + 10] for i in range(0, len(rds_list), 10)]
    try:
        for i in metric_name_dict.keys():
            for rdss in rds_list_10:
                starttime = (datetime.now() + timedelta(minutes=-1)).strftime('%Y-%m-%dT%H:%M:%S+08:00')
                ins_list = [{"Dimensions":[{"Name":"InstanceId","Value":x}]} for x in rdss]
                params = {"Namespace":"QCE/CDB","MetricName":i,"Period":60,"StartTime":starttime,"Instances":ins_list}
                req.from_json_string(json.dumps(params))
                resp = client.GetMonitorData(req)
                metric_list = resp.DataPoints
                for metrics in metric_list:
                    iid = metrics.Dimensions[0].Value
                    value = metrics.Values[-1]
                    ts = metrics.Timestamps[-1]*1000
                    prom_metric_name = metric_name_dict[i][0].split()[2]
                    metric_name_dict[i].append(f'{prom_metric_name}{{iid="{iid}"}} {float(value)} {ts}') 
        prom_metric_list = []
        for x in metric_name_dict.values():
            prom_metric_list = prom_metric_list + x
        return prom_metric_list
    except TencentCloudSDKException as err:
        print(err)
