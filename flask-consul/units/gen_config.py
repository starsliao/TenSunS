from config import consul_token,consul_url

def rds_config(services_list, exporter):
    consul_server = consul_url.split("/")[2]
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
  - alert: MySQL_is_down
    expr: mysql_up == 0
    for: 3m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL database is down. \\n> {{ $labels.iid }}"

  - alert: MySQL_慢查询过多
    expr: delta(mysql_global_status_slow_queries[1m]) > 60
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：每分钟慢查询:{{ $value }} \\n> {{ $labels.iid }}"

  - alert: mysql_当前活跃的连接数过多
    expr: mysql_global_status_threads_running > 100
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：当前活跃的连接数:{{ $value }} \\n> {{ $labels.iid }}"

  - alert: mysql_当前updating状态的线程过多
    expr: mysql_info_schema_processlist_threads{state=~"updating"} > 100
    for: 1m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：当前updating状态的线程:{{ $value }} \\n> {{ $labels.iid }}"

  - alert: MySQL_High_QPS
    expr: irate(mysql_global_status_questions[3m]) > 30000
    for: 2m
    labels:
      severity: warning
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：Mysql QPS:{{ $value | humanize }} \\n> {{ $labels.iid }}"

  - alert: MySQL_Too_Many_Connections
    expr: irate(mysql_global_status_threads_connected[3m]) > 1000
    for: 2m
    labels:
      severity: warning
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：Mysql Connections:{{ $value | humanize }} \\n> {{ $labels.iid }}"

  - alert: MySQL_is_Restart
    expr: mysql_global_status_uptime <600
    for: 2m
    labels:
      severity: critical
    annotations:
      description: "{{ $labels.group }}_{{ $labels.name }}：MySQL database is Restart. \\n> {{ $labels.iid }}"
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
  - alert: 内存使用率
    expr: 100 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：内存使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: CPU使用率
    expr: 100 - (avg by(instance,name,group,account) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：CPU使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: 系统负载
    expr: node_load5 / on (instance,name,group,account) sum(count(node_cpu_seconds_total{mode='system'}) by (cpu,instance,name,group,account)) by(instance,name,group,account) > 1.7
    for: 10m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}：系统负载{{ $value | humanize }}倍\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: 磁盘使用率
    expr: |
      100 - (node_filesystem_avail_bytes/node_filesystem_size_bytes{fstype=~"ext.?|xfs",mountpoint!~".*pods.*|/var/lib/docker/devicemapper/mnt/.*"} * 100) > 85
    for: 5m
    labels:
      alertype: system
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.mountpoint }}：磁盘使用率{{ $value | humanize }}%\\n> {{ $labels.group }}-{{ $labels.instance }}"

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

  - alert: 磁盘读写容量
    expr: (irate(node_disk_read_bytes_total[5m]) ) /1024 /1024  > 80 or (irate(node_disk_written_bytes_total[5m]) ) /1024 /1024 > 80
    for: 8m
    labels:
      alertype: disk
      severity: warning
    annotations:
      description: "{{ $labels.name }}_{{ $labels.device }}：当前IO为{{ $value | humanize }}MB/s\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: 网络流入（下载）数据过多
    expr: sum by(device,instance, name, group, account) (irate(node_network_receive_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr.*|lo.*|cni.*'}[5m])) / 1024 / 1024 > 70
    for: 5m
    labels:
      alertype: network
      severity: warning
    annotations:
      description: "{{ $labels.name }}：流入数据为{{ $value | humanize }}MB/s\\n> {{ $labels.group }}-{{ $labels.instance }}"

  - alert: 网络流出（上传）数据过多
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
