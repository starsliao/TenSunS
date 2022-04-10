### Consul字段设计说明

- 所有数据存在一个名为`blackbox_exporter`的Services项中，每个监控目标为一个子Service。
- 每个Service使用Meta的kv保存监控目标的属性：`module`，`company`，`project`，`env`，`name`，`instance`，分别表示：监控类型，公司部门，项目，环境，名称，实例url。
- **新增监控时，监控类型字段(`module`)和Blackbox配置中的`module`必须保持一致。**
- **前5个字段合并即为consul的serviceID，作为唯一监控项标识**

### 配置Prometheus与Blackbox

#### 基于Consul实现Prometheus的自动发现功能配置
- 把Consul每个service的Meta的KV关联到Prometheus每个指标的标签。
- 根据每个指标的标签来对监控目标分类，分组，方便管理维护。
##### 1. 配置Blackbox_Exporter
- 在Web页面点击`Blackbox 站点监控/Blackbox 配置`，点击`复制配置`。
- 编辑blackbox_exporter的`blackbox.yml`，清空已有的配置，把复制的内容粘贴进去，重启blackbox_exporter。
##### 2. 配置Prometheus
- 在Web页面点击`Blackbox 站点监控/Prometheus 配置`，点击`复制配置`。
- 编辑Prometheus的`prometheus.yml`，把复制的内容追加到最后，reload或重启Prometheus。
##### 3. 配置Prometheus告警规则
- 在Web页面点击`Blackbox 站点监控/告警规则`，点击`复制配置`。
- 编辑Prometheus的`rules.yml`，把复制的内容追加到最后，reload或重启Prometheus。
##### 4. 导入Blackbox Exporter Dashboard
- 支持Grafana 8，基于blackbox_exporter 0.19.0设计
- 采用图表+曲线图方式展示TCP，ICMP，HTTPS的服务状态，各阶段请求延时，HTTPS证书信息等
- 优化展示效果，支持监控目标的分组、分类级联展示，多服务同时对比展示。
```
导入ID：9965
详细URL：https://grafana.com/grafana/dashboards/9965
```

---

##### 批量导入脚本

在units目录下`instance.list`中写入监控目标的信息：JOB名称，公司/部门，项目，环境，名称，实例url，每行一个，空格分隔。

**注意：前5个字段组合起来必须唯一，作为一个监控项的ID。**

修改units目录下导入脚本中的consul_token和consul_url，保存后执行input.py，即可导入所有监控目标到Consul，并符合Prometheus的自动发现配置。
