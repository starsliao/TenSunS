# 概述
- ConsulManager是一个使用Flask+Vue开发的Consul WEB管理工具，比官方自带的WEB UI实现了更多的功能。
- 可以方便的对Consul Services进行增删改查，支持批量操作；并优化了对Tags、Meta、健康检查的配置管理与查询展示。
- 本工具基于Prometheus自动发现Consul，实现了两个监控管理维护的应用：
  1. 基于云厂商ECS的自动同步到Consul，并接入Prometheus监控。
  2. 基于Blackbox实现站点与接口监控接入Consul，通过Web界面方便管理。
- 本工具支持使用docker-compose快速部署。

## 实现功能
### Consul Web Manager
- 比官方自带的WEB UI实现了更多的功能。
- 包含Consul服务器的状态信息。
- 支持Consul Services的增删改查，可以批量删除Service。
- 直观的查看每个Services实例的信息，及整体Services的健康状态。
- 可以方便的对每个Services实例的Tags、Meta、健康检查进行配置。

### ECS Manager
- 支持同步阿里云，腾讯云，华为云的ECS主机信息到Consul。
- 基于Consul实现Prometheus监控目标的自动发现。
- 支持同步各云厂商的分组信息到Consul，用于关联ECS分组。
- 提供了可查询分组与ECS信息的页面，指标中加入了ECS到期日等信息，可直接监控。
- 可调整同步的时间间隔。
- 提供了按需的Prometheus配置生成功能。
- 提供了一个匹配ECS Manager各字段的node_exporter Grafana展示看板。

### Blackbox Manager 
- 基于Prometheus + Blackbox_Exporter实现站点与接口监控。
- 基于Consul实现Prometheus监控目标的自动发现。
- 使用Web操作即可简单的对监控目标增删改查，支持批量删除，以及方便的分类维护管理。
- 提供了Blackbox的配置，Prometheus的配置以及Prometheus站点监控的告警规则。
- 提供了一个匹配Blackbox Manager各字段的Blackbox Exporter Grafana展示看板。
- 提供脚本可批量导入监控目标到Consul。

## [更新记录](https://github.com/starsliao/ConsulManager/releases)

## 截图
### Consul Web Manager 界面
![](https://github.com/starsliao/ConsulManager/blob/main/screenshot/consul2.PNG?raw=true)
### ECS Manager 界面
![](https://github.com/starsliao/ConsulManager/blob/main/screenshot/ecs1.PNG?raw=true)
### Blackbox Manager 界面
![](https://github.com/starsliao/ConsulManager/blob/main/screenshot/blackbox1.PNG?raw=true)
### Node Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/node-exporter.png)
### Blackbox Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/blackbox.png)

## 部署说明

### 1. 部署Consul

##### 安装

```bash
# 使用yum部署consul
yum install -y yum-utils
yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
yum -y install consul
# 或者直接下RPM包安装
wget https://rpm.releases.hashicorp.com/RHEL/7/x86_64/stable/consul-1.11.4.x86_64.rpm
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
wget https://raw.githubusercontent.com/starsliao/ConsulManager/main/docker-compose.yml
编辑docker-compose.yaml文件，修改传入的3个环境变量：
- **consul的`token`，consul的`URL`(/v1要保留)，登录Consul Manager的`密码`**

- 启动：`docker-compose pull && docker-compose up -d`
- 访问：`http://{IP}:1026`
---

## [应用场景1：如何优雅的使用Consul管理ECS主机监控](https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md)
## [应用场景2：如何优雅的使用Consul管理Blackbox站点监控](https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md)


# 特别鸣谢
## 赞赏与关注公众号【**云原生DevOps**】加入运维群交流，获取更多...
![](https://github.com/starsliao/ConsulManager/blob/main/thanks.png)

---

### 赞助
暂无

---

### 提交代码
暂无

---

### 提交bug
@会飞的鱼

---

### 提供建议
[@dong9205](https://github.com/dong9205)

[@dissipator](https://github.com/dissipator)

---

