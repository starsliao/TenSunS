# 概述
- ConsulManager是一个使用Flask+Vue开发的Consul WEB管理工具，比官方自带的WEB UI实现了更多的功能，可以方便的对Consul Services进行增删改查，支持批量操作；并优化了对Tags、Meta、健康检查的配置管理与查询展示。
- 本工具还针对使用Consul+Prometheus+Blackbox_Exporter实现站点与接口监控的应用场景，制作了一个单独的管理页面，并提供了站点与接口监控的完整方案。
- 本工具支持使用docker-compose快速部署，并提供批量导入服务到Consul的脚本。
### 关注公众号【**云原生DevOps**】加入运维群交流，获取更多...
![](https://github.com/starsliao/Prometheus/blob/master/qr.jpg)
## 实现功能
### Consul Manager
- 更名Consul Manager
- 增加Consul Web管理功能
- 增加Consul服务器的状态查看
- 支持Consul Services的增删改查
- 支持批量删除Service功能
- 优化了对Tags、Meta、健康检查的配置管理
### Blackbox Manager 
- 基于Prometheus + Blackbox_Exporter实现站点与接口监控。
- 基于Consul实现Prometheus监控目标的自动发现。
- Blackbox Manager：基于Flask + Vue实现的Web管理平台，可以简单的对监控目标增删改查，便于分类维护管理。
- 实现了一个脚本可批量导入监控目标到Consul。
- 更新了一个Blackbox Exporter的Grafana展示看板。
- 提供了Prometheus站点监控的参考告警规则。
## [更新记录](https://github.com/starsliao/ConsulManager/releases)

## 截图
### Consul Manager 界面
![c1](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul1.png)![c2](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul2.png)![c3](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul3.png)
![c4](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul4.png)
### Blackbox Manager 界面
![0](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/0.png)

### Blackbox Exporter Dashboard 截图
![1](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/1.png)![2](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/2.png)

## 部署说明

### 1. 部署Consul

##### 安装

```bash
# 使用yum部署consul
yum install -y yum-utils
yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
yum -y install consul
# 或者直接下RPM包安装
wget https://rpm.releases.hashicorp.com/RHEL/7/x86_64/stable/consul-1.11.1-1.x86_64.rpm
rpm -ivh ./consul-1.11.1-1.x86_64.rpm
```

##### 配置

```bash
vi /etc/consul.d/consul.hcl
advertise_addr = "10.5.148.67" #如果有多网卡需要配置这行，填写你的网卡IP
data_dir = "/opt/consul"
client_addr = "0.0.0.0"
ui_config{
  enabled = true
}
server = true
bootstrap = true
acl = {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
}
```

##### 启动与鉴权配置

```bash
systemctl enable consul.service
systemctl start consul.service
# 获取登录密码
consul acl bootstrap
# 记录 SecretID
```

### 2. 部署Consul Manager

##### 使用docker-compose来部署
编辑docker-compose.yaml文件，修改传入的3个环境变量：
- **consul的`token`，consul的`URL`(/v1要保留)，登录Consul Manager的`密码`**

- 启动：`docker-compose pull && docker-compose up -d`
- 访问：`http://{IP}:1026`
---

# 应用场景：如何优雅的使用Consul管理Blackbox站点监控
##### Consul字段设计说明

- 所有数据存在一个名为`blackbox_exporter`的Services项中，每个监控目标为一个子Service。
- 每个Service包含一个Tag，会自动配置为meta中的`module`的值，作为Prometheus自动发现的tags。
- 每个Service使用Meta的kv保存监控目标的明细：`module`，`company`，`project`，`env`，`name`，`instance`，分别表示：监控类型，公司部门，项目，环境，名称，实例url
- **前5个字段合并即为consul的serviceID，作为唯一监控项标识**
- **建议监控类型字段：`meta内的module`，`blackbox-exporter配置中的module`及`Prometheus的job名`使用同一命名。**

### 配置Prometheus

##### 基于Consul实现Prometheus的自动发现功能配置

- 根据Consul每个service的tag来把监控目标关联到Prometheus的JOB。
- 把Consul每个service的Meta的KV关联到Prometheus每个指标的标签。
- 根据每个指标的标签来对监控目标分类，分组，方便管理维护。

**以下配置的同一个job的`job_name`，`module`，`tags`使用同一命名，关联job，module与consul的tags**

参考配置：2XX，4XX，TCP类型的监控，注意JOB名称不要与已有的重复。
```yaml
vi prometheus.yml
#####blackbox_exporter#####
  - job_name: 'http_2xx'
    metrics_path: /probe
    params:
      module: [http_2xx]
    consul_sd_configs:
      - server: 'x.x.x.x:8500'
        token: 'xxx-xxx-xxx-xxx'
        services: ['blackbox_exporter']
        tags: ['http_2xx']
    relabel_configs:
      - source_labels: ["__meta_consul_service_metadata_instance"]
        target_label: __param_target
      - source_labels: ["__meta_consul_service_metadata_company"]
        target_label: company
      - source_labels: ["__meta_consul_service_metadata_env"]
        target_label: env
      - source_labels: ["__meta_consul_service_metadata_name"]
        target_label: name
      - source_labels: ["__meta_consul_service_metadata_project"]
        target_label: project
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115
  - job_name: 'http_4xx'
    metrics_path: /probe
    params:
      module: [http_4xx]
    consul_sd_configs:
      - server: 'x.x.x.x:8500'
        token: 'xxx-xxx-xxx-xxx'
        services: ['blackbox_exporter']
        tags: ['http_4xx']
    relabel_configs:
      - source_labels: ["__meta_consul_service_metadata_instance"]
        target_label: __param_target
      - source_labels: ["__meta_consul_service_metadata_company"]
        target_label: company
      - source_labels: ["__meta_consul_service_metadata_env"]
        target_label: env
      - source_labels: ["__meta_consul_service_metadata_name"]
        target_label: name
      - source_labels: ["__meta_consul_service_metadata_project"]
        target_label: project
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115
  - job_name: 'tcp_connect'
    metrics_path: /probe
    params:
      module: [tcp_connect]
    consul_sd_configs:
      - server: 'x.x.x.x:8500'
        token: 'xxx-xxx-xxx-xxx'
        services: ['blackbox_exporter']
        tags: ['tcp_connect']
    relabel_configs:
      - source_labels: ["__meta_consul_service_metadata_instance"]
        target_label: __param_target
      - source_labels: ["__meta_consul_service_metadata_company"]
        target_label: company
      - source_labels: ["__meta_consul_service_metadata_env"]
        target_label: env
      - source_labels: ["__meta_consul_service_metadata_name"]
        target_label: name
      - source_labels: ["__meta_consul_service_metadata_project"]
        target_label: project
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115
```

### 配置Blackbox_Exporter

参考配置：2XX，4XX，TCP类型的监控，注意模块名称不要与已有的重复。

```
cat blackbox.yml
modules:
  http_2xx:
    prober: http
    http:
      valid_status_codes:
      - 200
      - 301
      - 302
      - 303
      no_follow_redirects: true
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  http_4xx:
    prober: http
    http:
      valid_status_codes:
      - 401
      - 403
      - 404
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  tcp_connect:
    prober: tcp
```

### 批量导入脚本

在units目录下`instance.list`中写入监控目标的信息：JOB名称，公司/部门，项目，环境，名称，实例url，每行一个，空格分隔。
**注意：前5个字段组合起来必须唯一，作为一个监控项的ID。**
修改units目录下导入脚本中的consul_token和consul_url，保存后执行input.py，即可导入所有监控目标到Consul，并符合Prometheus的自动发现配置。

### 导入Blackbox Exporter Dashboard

- 支持Grafana 8，基于blackbox_exporter 0.19.0设计
- 采用图表+曲线图方式展示TCP，ICMP，HTTPS的服务状态，各阶段请求延时，HTTPS证书信息等
- 优化展示效果，支持监控目标的分组、分类级联展示，多服务同时对比展示。

```
导入ID：9965
详细URL：https://grafana.com/grafana/dashboards/9965
```
### Prometheus 站点监控告警规则
```
- name: Domain
  rules:
  - alert: 站点可用性
    expr: probe_success == 0
    for: 1m
    labels:
      alertype: domain
      severity: critical
    annotations:
      description: "{{$labels.env}}_{{ $labels.name }}({{ $labels.project }})：站点无法访问\n> {{ $labels.instance }}"

  - alert: 站点1h可用性低于80%
    expr: sum_over_time(probe_success[1h])/count_over_time(probe_success[1h]) * 100 < 80
    for: 3m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{$labels.env}}_{{ $labels.name }}({{ $labels.project }})：站点1h可用性：{{ $value | humanize }}%\n> {{ $labels.instance }}"

  - alert: 站点状态异常
    expr: (probe_success == 0 and probe_http_status_code > 499) or probe_http_status_code == 0
    for: 1m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{$labels.env}}_{{ $labels.name }}({{ $labels.project }})：站点状态异常：{{$value}}\n> {{ $labels.instance }}"

  - alert: 站点耗时过高
    expr: probe_duration_seconds > 0.5
    for: 2m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{$labels.env}}_{{ $labels.name }}({{ $labels.project }})：当前站点耗时：{{$value | humanize}}s\n> {{ $labels.instance }}"

  - alert: SSL证书有效期
    expr: (probe_ssl_earliest_cert_expiry-time()) / 3600 / 24 < 15
    for: 2m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{$labels.env}}_{{ $labels.name }}({{ $labels.project }})：证书有效期剩余{{ $value | humanize }}天\n> {{ $labels.instance }}"
```
### GitHub

所有代码都在里面，抛砖引玉。

```
https://github.com/starsliao/ConsulManager
```
