<div align="center">

[![StarsL.cn](https://img.shields.io/badge/website-StarsL.cn-orange)](https://starsl.cn)
[![Commits](https://img.shields.io/github/commit-activity/m/starsliao/ConsulManager?color=ffff00)](https://github.com/starsliao/ConsulManager/commits/main)
[![GitHub Stargazers](https://img.shields.io/github/stars/starsliao/ConsulManager?color=ff69b4)](https://github.com/starsliao/ConsulManager/stargazers)
[![Python](https://img.shields.io/badge/python-%3E=v3.6.8-3776ab)](https://nodejs.org)
[![Node.js](https://img.shields.io/badge/node.js-%3E=v14.19-229954)](https://nodejs.org)
[![GitHub license](https://img.shields.io/badge/license-MIT-blueviolet)](https://github.com/starsliao/ConsulManager/blob/main/LICENSE)
[![OSCS Status](https://www.oscs1024.com/platform/badge/starsliao/ConsulManager.svg?size=small)](https://www.murphysec.com/dr/Zoyt5g0huRavAtItj2)
</div>

# 🏷目录
* [🚀概述](#概述)
* [🌈实现功能](#实现功能)
* [📌更新记录](#更新记录)
* [🎨截图预览](#截图预览点击查看完整截图)
* [💾部署说明](#部署说明)
* [🥇最佳实践](#最佳实践)
* [💖特别鸣谢](#特别鸣谢)

## 🦄概述
>**ConsulManager**是一个使用Flask+Vue开发的WEB运维平台，弥补了Consul官方UI对Services管理的不足；并且基于Consul的自动发现与键值存储：实现了各云厂商资源与Prometheus的无缝同步，以及对各类监控资源的优雅管理与展示。

## 🌈实现功能
### 🎡Consul 管理
- 支持Consul Services的增删改查，可以批量删除Service。
- 直观的查看每个Services实例的信息，及整体Services的健康状态。
- 可以便捷的对Services实例的Tags、Meta、健康检查配置管理与查询展示。

### 💎云资源监控管理
>**基于Consul实现Prometheus监控目标的自动发现。**

- 支持阿里云、腾讯云、华为云的ECS主机、分组、标签自动同步到Consul。
- 支持自建主机接入WEB管理，并支持WEB批量导入自建主机到Consul。
- 支持阿里云、腾讯云、华为云账户余额与云资源到期日设置阈值告警通知。
- 提供了可查询分组与ECS信息的页面，指标中加入了ECS到期日等信息。
- 提供了按需生成Prometheus配置与ECS告警规则的功能。
- 设计了一个支持同步的各字段展示的Node_Exporter Grafana看板。

### 🚀站点与接口监控管理
>**基于Consul + Prometheus + Blackbox_Exporter实现站点的自动发现与监控。**

- 使用Web页面即可对监控目标增删改查，支持站点的分级分组查询管理。
- 支持对监控目标的批量删除与批量导入，数据实时同步到Consul。
- 提供了Blackbox的配置、Prometheus的配置以及Prometheus站点监控的告警规则。
- 设计了一个支持各分级分组字段展示的Blackbox_Exporter Grafana看板。

### 💫高危漏洞采集与实时告警
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
- ### [ConsulManager：实践与FAQ](https://github.com/starsliao/ConsulManager/tree/main/docs)
- ### [应用场景1：如何优雅的基于Consul自动同步ECS主机监控](https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md)
- ### [应用场景2：如何优雅的使用Consul管理Blackbox站点监控](https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md)


## 💖特别鸣谢
### 赞赏与关注公众号【**云原生DevOps**】加入交流群（请备注：consul），获取更多...
![](https://starsl.cn/static/img/thanks.png)

---

### 💰赞赏
@南城阿宇  @mac🐬 🌈  @Stephen  @蔡志昆  @风与尘的誓约  @Initᯤ⁶ᴳ  @254209  @Runner91  @烂泥

---

### ✅提交代码
[@dbdocker](https://github.com/dbdocker)

---

### 🎃提交bug
@会飞的鱼  [@奈](https://github.com/Wp516781950)  @Swancavalier  @Show Lo

---

### 📢提供建议
[@dong9205](https://github.com/dong9205)  [@dissipator](https://github.com/dissipator)

---
# 💖感谢伟大的[Flask](https://github.com/pallets/flask)、[VUE](https://github.com/vuejs/vue)、[vue-admin-template](https://github.com/PanJiaChen/vue-admin-template)
