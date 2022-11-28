from config import consul_token,consul_url

def redis_config(region_list,cm_exporter,services_list,exporter):
    region_str = '\n      - '.join([i.replace('/redis','') for i in region_list])
    consul_server = consul_url.split("/")[2]
    exporter_config = f"""
  - job_name: 'ConsulManager-REDIS'
    scrape_interval: 30s
    scrape_timeout: 15s
    static_configs:
    - targets:
      - {region_str}
    relabel_configs:
      - source_labels: [__address__]
        target_label: __metrics_path__
        regex: (.*)
        replacement: /api/cloud_redis_metrics/${{1}}
      - target_label: __address__
        replacement: {cm_exporter}
"""
    configs = f"""
  - job_name: redis_exporter
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /scrape
    consul_sd_configs:
      - server: '{consul_server}'
        token: '{consul_token}'
        refresh_interval: 30s
        services: {services_list}
    relabel_configs:
      - source_labels: [__meta_consul_tags]
        regex: .*OFF.*
        action: drop
      - source_labels: [__meta_consul_service_address,__meta_consul_service_port]
        regex: ([^:]+)(?::\d+)?;(\d+)
        target_label: __param_target
        replacement: $1:$2
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: {exporter}
      - source_labels: ['__meta_consul_service_metadata_vendor']
        target_label: vendor
      - source_labels: ['__meta_consul_service_metadata_region']
        target_label: region
      - source_labels: ['__meta_consul_service_metadata_group']
        target_label: group
      - source_labels: ['__meta_consul_service_metadata_account']
        target_label: account
      - source_labels: ['__meta_consul_service_metadata_name']
        target_label: name
      - source_labels: ['__meta_consul_service_metadata_iid']
        target_label: iid
      - source_labels: ['__meta_consul_service_metadata_mem']
        target_label: mem
      - source_labels: ['__meta_consul_service_metadata_itype']
        target_label: itype
      - source_labels: ['__meta_consul_service_metadata_ver']
        target_label: ver
"""
    if not services_list:
        return {'code': 20000,'configs': '请选择需要Prometheus从Conusl自动发现的MySQL组' }
    if services_list and exporter == '':
        return {'code': 20000,'configs': '您已经选择了需要Prometheus从Conusl自动发现MySQL组，\n请输入Redis_Exporter的地址和端口，例如：10.0.0.26:9121' }
    if region_list and cm_exporter == '':
        return {'code': 20000,'configs': '您已经选择了需要从云监控采集基础指标(CPU、内存、磁盘、IO)的MySQL组，\n请输入ConsulManager地址和端口，例如：10.0.0.26:1026' }

    if region_list:
        return {'code': 20000,'configs': exporter_config + configs }
    else:
        return {'code': 20000,'configs': configs }

def rds_config(region_list,cm_exporter,services_list,exporter):
    region_str = '\n      - '.join([i.replace('/rds','') for i in region_list])
    consul_server = consul_url.split("/")[2]
    exporter_config = f"""
  - job_name: 'ConsulManager-MySQL'
    scrape_interval: 30s
    scrape_timeout: 15s
    static_configs:
    - targets:
      - {region_str}
    relabel_configs:
      - source_labels: [__address__]
        target_label: __metrics_path__
        regex: (.*)
        replacement: /api/cloud_mysql_metrics/${{1}}
      - target_label: __address__
        replacement: {cm_exporter}
"""
    configs = f"""
  - job_name: multi_mysqld_exporter
    scrape_interval: 15s
    scrape_timeout: 5s
    metrics_path: /probe
    consul_sd_configs:
      - server: '{consul_server}'
        token: '{consul_token}'
        refresh_interval: 30s
        services: {services_list}
    relabel_configs:
      - source_labels: [__meta_consul_tags]
        regex: .*OFF.*
        action: drop
      - source_labels: [__meta_consul_service_address,__meta_consul_service_port]
        regex: ([^:]+)(?::\d+)?;(\d+)
        target_label: __param_target
        replacement: $1:$2
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: {exporter}
      - source_labels: ['__meta_consul_service_metadata_vendor']
        target_label: vendor
      - source_labels: ['__meta_consul_service_metadata_region']
        target_label: region
      - source_labels: ['__meta_consul_service_metadata_group']
        target_label: group
      - source_labels: ['__meta_consul_service_metadata_account']
        target_label: account
      - source_labels: ['__meta_consul_service_metadata_name']
        target_label: name
      - source_labels: ['__meta_consul_service_metadata_iid']
        target_label: iid
      - source_labels: ['__meta_consul_service_metadata_exp']
        target_label: exp
      - source_labels: ['__meta_consul_service_metadata_cpu']
        target_label: cpu
      - source_labels: ['__meta_consul_service_metadata_mem']
        target_label: mem
      - source_labels: ['__meta_consul_service_metadata_disk']
        target_label: disk
      - source_labels: ['__meta_consul_service_metadata_itype']
        target_label: itype
"""
    if not services_list:
        return {'code': 20000,'configs': '请选择需要Prometheus从Conusl自动发现的MySQL组' }
    if services_list and exporter == '':
        return {'code': 20000,'configs': '您已经选择了需要Prometheus从Conusl自动发现MySQL组，\n请输入Mysql_Exporter的地址和端口，例如：10.0.0.26:9104' }
    if region_list and cm_exporter == '':
        return {'code': 20000,'configs': '您已经选择了需要从云监控采集基础指标(CPU、内存、磁盘、IO)的MySQL组，\n请输入ConsulManager地址和端口，例如：10.0.0.26:1026' }

    if region_list:
        return {'code': 20000,'configs': exporter_config + configs }
    else:
        return {'code': 20000,'configs': configs }

def ecs_config(services_list,ostype_list):
    consul_server = consul_url.split("/")[2]
    job_dict = {'linux':'node_exporter','windows':'windows_exporter'}
    configs = ''
    for ostype in ostype_list:
        job_name = job_dict[ostype]
        config_str = f"""
  - job_name: {job_name}
    scrape_interval: 15s
    scrape_timeout: 5s
    consul_sd_configs:
      - server: '{consul_server}'
        token: '{consul_token}'
        refresh_interval: 30s
        services: {services_list}
        tags: ['{ostype}']
    relabel_configs:
      - source_labels: [__meta_consul_tags]
        regex: .*OFF.*
        action: drop
      - source_labels: ['__meta_consul_service']
        target_label: cservice
      - source_labels: ['__meta_consul_service_metadata_vendor']
        target_label: vendor
      - source_labels: ['__meta_consul_service_metadata_region']
        target_label: region
      - source_labels: ['__meta_consul_service_metadata_group']
        target_label: group
      - source_labels: ['__meta_consul_service_metadata_account']
        target_label: account
      - source_labels: ['__meta_consul_service_metadata_name']
        target_label: name
      - source_labels: ['__meta_consul_service_metadata_iid']
        target_label: iid
      - source_labels: ['__meta_consul_service_metadata_exp']
        target_label: exp
      - source_labels: ['__meta_consul_service_metadata_instance']
        target_label: instance
      - source_labels: [instance]
        target_label: __address__
"""
        configs = configs + config_str
    return {'code': 20000,'configs': configs }

def get_rdsrules():
    rules = """
groups:
- name: MySQL-Alert
  rules:
  - alert: MySQL_CPU使用率过高
    expr: mysql_cpu_util * on (iid) group_right mysql_up > 70
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL当前CPU使用率:{{ $value }}% \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_内存使用率过高
    expr: mysql_mem_util * on (iid) group_right mysql_up > 85
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL当前内存使用率:{{ $value }}% \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_磁盘使用率过高
    expr: mysql_disk_util * on (iid) group_right mysql_up > 90
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL当前磁盘使用率:{{ $value }}% \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_IO使用率过高
    expr: mysql_io_util * on (iid) group_right mysql_up > 90
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL当前IO使用率:{{ $value }}% \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_is_down
    expr: mysql_up == 0
    for: 3m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL database is down. \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_慢查询过多
    expr: delta(mysql_global_status_slow_queries[1m]) > 60
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：每分钟慢查询:{{ $value }} \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_当前活跃的连接数过多
    expr: mysql_global_status_threads_running > 100
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：当前活跃的连接数:{{ $value }} \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_当前updating状态的线程过多
    expr: mysql_info_schema_processlist_threads{state=~"updating"} > 100
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：当前updating状态的线程:{{ $value }} \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_High_QPS
    expr: irate(mysql_global_status_questions[3m]) > 30000
    for: 2m
    labels:
      severity: warning
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：Mysql QPS:{{ $value | humanize }} \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_Too_Many_Connections
    expr: irate(mysql_global_status_threads_connected[3m]) > 1000
    for: 2m
    labels:
      severity: warning
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：Mysql Connections:{{ $value | humanize }} \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_主从IO线程运行状态异常
    expr: mysql_slave_status_master_server_id > 0 and ON (instance) mysql_slave_status_slave_io_running == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL Slave IO thread not running \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"
  
  - alert: MySQL_主从SQL线程运行状态异常
    expr: mysql_slave_status_master_server_id > 0 and ON (instance) mysql_slave_status_slave_sql_running == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL Slave SQL thread not running \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_主从复制延迟过高
    expr: mysql_slave_status_seconds_behind_master > 3
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：主从复制延迟当前:{{ $value | humanize }}s \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"

  - alert: MySQL_is_Restart
    expr: mysql_global_status_uptime <600
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL database is Restart. \\n> {{ $labels.instance }}\\n> {{ $labels.iid }}"
"""
    return {"code": 20000, "rules": rules}

def get_redisrules():
    rules = """
groups:
- name: REDIS-Alert
  rules:
  - alert: RedisDown
    expr: redis_up == 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis down (instance {{ $labels.instance }})
      description: "Redis instance is down\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisMissingMaster
    expr: (count(redis_instance_info{role="master"}) or vector(0)) < 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis missing master (instance {{ $labels.instance }})
      description: "Redis cluster has no node marked as master.\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisTooManyMasters
    expr: count(redis_instance_info{role="master"}) > 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis too many masters (instance {{ $labels.instance }})
      description: "Redis cluster has too many nodes marked as master.\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisDisconnectedSlaves
    expr: count without (instance, job) (redis_connected_slaves) - sum without (instance, job) (redis_connected_slaves) - 1 > 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis disconnected slaves (instance {{ $labels.instance }})
      description: "Redis not replicating for all slaves. Consider reviewing the redis replication status.\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisReplicationBroken
    expr: delta(redis_connected_slaves[1m]) < 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis replication broken (instance {{ $labels.instance }})
      description: "Redis instance lost a slave\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisClusterFlapping
    expr: changes(redis_connected_slaves[1m]) > 1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: Redis cluster flapping (instance {{ $labels.instance }})
      description: "Changes have been detected in Redis replica connection. This can occur when replica nodes lose connection to the master and reconnect (a.k.a flapping).\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisMissingBackup
    expr: time() - redis_rdb_last_save_timestamp_seconds > 60 * 60 * 24
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis missing backup (instance {{ $labels.instance }})
      description: "Redis has not been backuped for 24 hours\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  # The exporter must be started with --include-system-metrics flag or REDIS_EXPORTER_INCL_SYSTEM_METRICS=true environment variable.
  - alert: RedisOutOfSystemMemory
    expr: redis_memory_used_bytes / redis_total_system_memory_bytes * 100 > 90
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: Redis out of system memory (instance {{ $labels.instance }})
      description: "Redis is running out of system memory (> 90%)\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisOutOfConfiguredMaxmemory
    expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: Redis out of configured maxmemory (instance {{ $labels.instance }})
      description: "Redis is running out of configured maxmemory (> 90%)\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisTooManyConnections
    expr: redis_connected_clients > 100
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: Redis too many connections (instance {{ $labels.instance }})
      description: "Redis instance has too many connections\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisNotEnoughConnections
    expr: redis_connected_clients < 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: Redis not enough connections (instance {{ $labels.instance }})
      description: "Redis instance should have more connections (> 5)\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"

  - alert: RedisRejectedConnections
    expr: increase(redis_rejected_connections_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: Redis rejected connections (instance {{ $labels.instance }})
      description: "Some connections to Redis has been rejected\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"
"""
    return {"code": 20000, "rules": rules}


def get_rules():
    rules = """
groups:
- name: node_usage_record_rules
  interval: 1m
  rules:
  - record: cpu:usage:rate1m
    expr: (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance,vendor,account,group,name)) * 100
  - record: mem:usage:rate1m
    expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

- name: node-exporter
  rules:
  - alert: ECS内存使用率
    expr: 100 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：内存使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS_CPU使用率
    expr: 100 - (avg by(instance,name,group,account) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：CPU使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS系统负载
    expr: node_load5 / on (instance,name,group,account) sum(count(node_cpu_seconds_total{mode='system'}) by (cpu,instance,name,group,account)) by(instance,name,group,account) > 1.7
    for: 10m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：系统负载{{ $value | humanize }}倍\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS磁盘使用率
    expr: |
      100 - (node_filesystem_avail_bytes/node_filesystem_size_bytes{fstype=~"ext.?|xfs",mountpoint!~".*pods.*|/var/lib/docker/devicemapper/mnt/.*"} * 100) > 85
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.mountpoint }}：磁盘使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS主机重启
    expr: node_time_seconds - node_boot_time_seconds < 600
    for: 1m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：主机重启\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS文件系统只读
    expr: node_filesystem_readonly == 1
    for: 1m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}-{{ $labels.mountpoint }}：文件系统只读\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: K8S节点POD磁盘使用率
    expr: 100 - (node_filesystem_avail_bytes/node_filesystem_size_bytes{mountpoint=~"/var/lib/docker/devicemapper/mnt/.*"} * 100) > 85
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.mountpoint }}：磁盘使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: NFS磁盘使用率
    expr: 100 - (node_filesystem_avail_bytes/node_filesystem_size_bytes{fstype="nfs"} * 100) > 90
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.mountpoint }}：磁盘使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS磁盘读写容量
    expr: (irate(node_disk_read_bytes_total[5m]) ) /1024 /1024  > 80 or (irate(node_disk_written_bytes_total[5m]) ) /1024 /1024 > 80
    for: 8m
    labels:
      alertype: disk
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.device }}：当前IO为{{ $value | humanize }}MB/s\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS网络流入（下载）数据过多
    expr: sum by(device,instance, name, group, account) (irate(node_network_receive_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr.*|lo.*|cni.*'}[5m])) / 1024 / 1024 > 70
    for: 5m
    labels:
      alertype: network
      severity: warning
    annotations:
      description: "{{ $labels.name }}：流入数据为{{ $value | humanize }}MB/s\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: ECS网络流出（上传）数据过多
    expr: sum by(device,instance, name, group, account) (irate(node_network_transmit_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr.*|lo.*|cni.*'}[5m])) / 1024 / 1024 > 70
    for: 5m
    labels:
      alertype: network
      severity: warning
    annotations:
      description: "{{ $labels.name }}：流出数据为{{ $value | humanize }}MB/s\\n> {{ $labels.group }}-{{ $labels.instance }}"

- name: Itself
  rules:
  - alert: Exporter状态
    expr: up == 0
    for: 3m
    labels:
      alertype: itself
      severity: critical
    annotations:
      description: "{{ $labels.job }}：异常\\n> {{ $labels.group }}-{{ $labels.name }}-{{ $labels.instance }}"
"""
    return {"code": 20000, "rules": rules}
