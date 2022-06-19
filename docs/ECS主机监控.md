### Consul字段设计说明
- 服务首次启动时会创建一个随机秘钥，存放到consul_kv的`/ConsulManager/assets/secret/skey`，该秘钥用于对登录Token，各云厂商账号AKSK的加解密使用。
- 云厂商的每个账号下的ECS实例信息：会存储到Consul的对应Services下的实例中，ECS的实例ID会作为ServiceID。
- 云厂商的每个账号下的AKSK和分组信息：存放到consul_kv的`/ConsulManager/assets`下各个云厂商的目录下的`aksk`(加密存储)和`group`目录。
- **分组字段：是采集云厂商用于资源分组的字段，阿里云：资源组，华为云：企业项目，腾讯云：所属项目。请在创建云主机时设置好属组。**
- 新增的各个云厂商的ECS同步任务：会存放到consul_kv的`/ConsulManager/jobs`下，服务启动的时候会加载这些任务。
- 每次同步任务的执行结果:会存储到consul_kv的`/ConsulManager/record/jobs`的各个云厂商目录下。
- 新增云厂商的数据源之后会自动同步一次分组信息，ECS信息则会在设置的时间间隔之后才会同步，可以手动点击同步按钮同步一次。
- Linux默认监控node_exporter的9100端口，Windows默认监控windows_exporter的9128端口。

### 配置说明
##### 1. 新增同步源 
- 在Web页面点击`Node 云主机监控/接入数据源`，点击`新增同步源`，输入各字段：
- `账户`可随意填写，用来区分云厂商不同云账户的标识，支持中文，例如用主账户的名称。
- 填写的`AKSK`需要有获取ECS的权限以及各云厂商分组信息的权限。（注意：腾讯云的分组信息因为在ECS中没有找到对应接口，是从`分布式数据库TDSQL-查询项目列表 (DCDB)`的接口中获取的，AKSK需要有对应权限。）
- 选择好对应的ECS所在区域（暂支持国内），以及分组与ECS的刷新间隔，确认即可，分组信息会自动同步一次，ECS信息则会在设置的时间间隔之后才会同步，可以手动点击同步按钮同步一次。
##### 2. 查看云主机列表
- 可以点击`查看`按钮或者在`云主机列表`中查看同步后的ECS信息。（华为云暂未获取到ECS到期日信息）
##### 3. 管理自建主机
- 在Web页面点击`Node 云主机监控/自建主机管理`，点击`新增`，根据需要即可增加需要监控的自建主机，支持增删改查与批量操作（脚本）。
##### 3. 配置Prometheus
- 点击`ECS 云主机监控/Prometheus 配置`，根据需要来生成各云账号、系统（均支持多选）的Prometheus配置信息（**有自建主机记得复选上`selfnode_exporter`**），复制配置后，追加到`prometheus.yml`的末尾，重启Prometheus即可。
##### 4. 查看Prometheus
- 在Prometheus的Web页面中，点击`Status-Targets`，能看到新增的Job即表示数据同步到Prometheus。
##### 5. 导入Node Exporter Dashboard
- 更新了主机监控的grafana看板，可匹配自动同步方式采集ECS信息字段的展示。
- 优化了大量图表，使用新版表格重建，新增健康评分概念，并新增了整体资源消耗信息的一些图表。
- **导入ID：8919**
- 详细URL：[https://grafana.com/grafana/dashboards/8919](https://grafana.com/grafana/dashboards/8919)

---

### 批量导入自建主机脚本

在项目仓库根目录的`tools`目录下：编辑`selfnode-instance.list`，写入监控目标的信息：机房/公司 租户/部门 区域/项目 分组/环境 名称 实例(ip:端口) 系统(linux/windows)，每行一个，空格分隔。

**注意：前5个字段组合起来必须唯一，作为一个监控项的ID。即Consul的ServiceID**

再修改导入脚本`selfnode-input.py`中的consul_token和consul_url，保存后执行`selfnode-input.py`，即可导入所有监控目标到Consul，并符合Prometheus的自动发现配置。

### 注意：

##### 主动关机的ECS，会在同步时候从Consul中清除，即会在Prometheus中去除(减少无效的告警)，重新开机后会增加回去。
##### 各ECS的Node_exporter需要自行安装。
##### 【最近7天P99资源使用率】图表需要在Prometheus增加记录规则(采集1小时后出数据)：
```
groups:   #新rule文件需要加这行开头，追加旧的rule文件则不需要。
- name: node_usage_record_rules
  interval: 1m
  rules:
  - record: cpu:usage:rate1m
    expr: (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance,vendor,account,group,name)) * 100
  - record: mem:usage:rate1m
    expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

