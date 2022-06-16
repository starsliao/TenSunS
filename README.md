# 🏷目录
* [🚀概述](#概述)
* [💎实现功能](#实现功能)
* [📌更新记录](#更新记录)
* [🎨截图预览](#截图预览点击查看完整截图)
* [💾部署说明](#部署说明)
* [🥇最佳实践](#最佳实践)
* [💖特别鸣谢](#特别鸣谢)

## 🚀概述
- **ConsulManager**是一个使用Flask+Vue开发的Consul WEB运维助手，弥补了官方UI对Services管理的不足，优化了Consul对Services的配置管理与查询展示。
- 本工具基于Prometheus自动发现Consul，还实现了几个监控管理的功能：
  1. 支持云厂商ECS与分组自动同步到Consul，并接入Prometheus监控。（设计了一个关联的Grafana看板）
  2. 基于Blackbox实现站点与接口监控接入Consul，通过Web界面方便管理。（设计了一个关联的Grafana看板）
  3. 高危漏洞采集与实时告警通知。

## 💎实现功能
### 🏆Consul 管理
- 支持Consul Services的增删改查，可以批量删除Service。
- 直观的查看每个Services实例的信息，及整体Services的健康状态。
- 可以便捷的对Services实例的Tags、Meta、健康检查配置管理与查询展示。

### 🏆Node 主机监控
- 基于Consul实现Prometheus监控目标的自动发现。
- 支持同步阿里云、腾讯云、华为云的ECS主机与分组信息到Consul。
- 支持自建主机接入监控管理，并提供脚本批量导入主机到Consul。
- 提供了可查询分组与ECS信息的页面，指标中加入了ECS到期日等信息，可直接监控。
- 提供了按需生成Prometheus配置与告警规则的功能。
- 提供了一个匹配ECS Manager各字段的node_exporter Grafana展示看板。

### 🏆Blackbox 站点监控
- 基于Prometheus + Blackbox_Exporter实现站点与接口监控。
- 基于Consul实现Prometheus监控目标的自动发现。
- 使用Web操作即可简单的对监控目标增删改查，支持批量删除，以及方便的分类维护管理。
- 提供脚本可批量导入监控目标到Consul。
- 提供了Blackbox的配置，Prometheus的配置以及Prometheus站点监控的告警规则。
- 提供了一个匹配Blackbox Manager各字段的Blackbox Exporter Grafana展示看板。

### 🏆高危漏洞采集与实时告警
- 增加了高危风险漏洞采集与实时告警通知功能。
- 功能开启即可采集最新30个漏洞列表。
- 每小时采集一次，发现新漏洞立即推送到群机器人。
- 支持企微、钉钉、飞书群机器人通知。

## 📌[更新记录](https://github.com/starsliao/ConsulManager/releases)

## 🎨截图预览（[点击查看完整截图](https://github.com/starsliao/ConsulManager/tree/main/screenshot#%E6%88%AA%E5%9B%BE)）
### Consul Web Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul3.PNG)
### ECS Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/ecs1.PNG)
### Node Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/node1.png)
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/node2.png)
### Blackbox Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/blackbox1.PNG)
### Blackbox Exporter Dashboard 截图
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/vue-consul/public/blackbox.png)
### 高危漏洞采集与通知 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/bug.png)
##### 钉钉告警通知
![图片](https://user-images.githubusercontent.com/3349611/173263960-4d69fff9-82fe-42a1-ba18-4c78775cf35e.png)

## 💾部署说明
##### 1. Consul Manager需要依赖`Consul`，请先完成Consul的部署。（[Consul部署文档](docs/Consul部署说明.md)）
##### 2. 使用`docker-compose`来部署Consul Manager
- 下载：`wget https://raw.githubusercontent.com/starsliao/ConsulManager/main/docker-compose.yml`
- 国内下载：`wget https://starsl.cn/static/img/docker-compose.yml`
- 编辑：`docker-compose.yml`，修改3个环境变量：
  - **`consul_token`**：consul的登录token
  - **`consul_url`**：consul的URL(http开头，/v1要保留)
  - **`admin_passwd`**：登录Consul Manager的admin密码
- 启动：`docker-compose pull && docker-compose up -d`
- 访问：`http://{IP}:1026`，使用配置的Consul Manager密码登录
---
## 🥇最佳实践
- ### [ConsulManager：实践与FAQ](https://github.com/starsliao/ConsulManager/docs)
- ### [应用场景1：如何优雅的基于Consul自动同步ECS主机监控](https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md)
- ### [应用场景2：如何优雅的使用Consul管理Blackbox站点监控](https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md)


## 💖特别鸣谢
### 赞赏与关注公众号【**云原生DevOps**】加入交流群（注明consul），获取更多...
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

