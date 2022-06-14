# 🚀概述
- **ConsulManager**是一个使用Flask+Vue开发的Consul WEB管理工具，弥补了官方UI对Services管理的不足，可以方便的对Consul Services进行增删改查，支持批量操作；并优化了对Tags、Meta、健康检查的配置管理与查询展示。
- 本工具基于Prometheus自动发现Consul，实现了两个监控管理维护的应用：
  1. 基于云厂商ECS的自动同步到Consul，并接入Prometheus监控。（设计了一个关联的Grafana看板）
  2. 基于Blackbox实现站点与接口监控接入Consul，通过Web界面方便管理。（设计了一个关联的Grafana看板）
- 本工具支持使用docker-compose快速部署。

## 💎实现功能
### 🏆Consul 管理
- 比官方自带的WEB UI实现了更多的功能。
- 包含Consul服务器的状态信息。
- 支持Consul Services的增删改查，可以批量删除Service。
- 直观的查看每个Services实例的信息，及整体Services的健康状态。
- 可以方便的对每个Services实例的Tags、Meta、健康检查进行配置。

### 🏆Node 主机监控
- 基于Consul实现Prometheus监控目标的自动发现。
- 支持同步阿里云，腾讯云，华为云的ECS主机信息到Consul。
- 支持同步各云厂商的分组信息到Consul，用于关联ECS分组。
- 支持自建主机接入监控管理，并提供脚本批量导入主机到Consul。
- 提供了可查询分组与ECS信息的页面，指标中加入了ECS到期日等信息，可直接监控。
- 提供了按需的Prometheus配置生成功能。
- 提供了一个匹配ECS Manager各字段的node_exporter Grafana展示看板。

### 🏆Blackbox 站点监控
- 基于Prometheus + Blackbox_Exporter实现站点与接口监控。
- 基于Consul实现Prometheus监控目标的自动发现。
- 使用Web操作即可简单的对监控目标增删改查，支持批量删除，以及方便的分类维护管理。
- 提供了Blackbox的配置，Prometheus的配置以及Prometheus站点监控的告警规则。
- 提供了一个匹配Blackbox Manager各字段的Blackbox Exporter Grafana展示看板。
- 提供脚本可批量导入监控目标到Consul。

### 🏆高危漏洞采集与通知
- 增加了高危风险漏洞采集与告警通知功能。
- 功能开启即可采集最新30个漏洞列表。
- 每小时采集一次，发现新漏洞立即推送到群机器人。
- 支持企微、钉钉、飞书群机器人通知。

## [更新记录](https://github.com/starsliao/ConsulManager/releases)

## 🎨部分截图（[点击查看完整截图](https://github.com/starsliao/ConsulManager/tree/main/screenshot#%E6%88%AA%E5%9B%BE)）
### Consul Web Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul1.PNG)
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul3.PNG)
### ECS Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/ecs1.PNG)
### Blackbox Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/blackbox1.PNG)
### 高危漏洞采集与通知 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/bug.png)
##### 通知界面
![图片](https://user-images.githubusercontent.com/3349611/173263960-4d69fff9-82fe-42a1-ba18-4c78775cf35e.png)

### Node Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/node1.png)
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/node2.png)
### Blackbox Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/blackbox.png)

## 💾部署说明

### 1. 部署Consul（[部署文档](docs/Consul部署说明.md)）

### 2. 部署Consul Manager

##### 使用docker-compose来部署
- 下载：`wget https://raw.githubusercontent.com/starsliao/ConsulManager/main/docker-compose.yml`
- 国内下载：`wget https://starsl.cn/static/img/docker-compose.yml`
- 编辑：`docker-compose.yml`，修改3个环境变量：
  - consul的token：**`consul_token`**
  - consul的URL(/v1要保留)：**`consul_url`**
  - 登录Consul Manager的密码：**`admin_passwd`**
- 启动：`docker-compose pull && docker-compose up -d`
- 访问：`http://{IP}:1026`
---
## [项目GitHub仓库](https://github.com/starsliao/ConsulManager)
## [应用场景1：如何优雅的基于Consul自动同步ECS主机监控](https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md)
## [应用场景2：如何优雅的使用Consul管理Blackbox站点监控](https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md)

### 💯开发线路
![图片](https://github.com/starsliao/ConsulManager/blob/main/Roadmap.png)

# 💖特别鸣谢
## 赞赏与关注公众号【**云原生DevOps**】加入交流群（注明consul），获取更多...
![](https://starsl.cn/static/img/thanks.png)

---

### 💰赞赏
@南城阿宇  @mac🐬 🌈  @Stephen  @蔡志昆  @风与尘的誓约  @Initᯤ⁶ᴳ  @254209  @Runner91

---

### ✅提交代码
暂无

---

### 🎃提交bug
@会飞的鱼  [@奈](https://github.com/Wp516781950)  @Swancavalier

---

### 📢提供建议
[@dong9205](https://github.com/dong9205)  [@dissipator](https://github.com/dissipator)

---

