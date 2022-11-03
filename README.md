<div align="center">

[![StarsL.cn](https://img.shields.io/badge/website-StarsL.cn-orange)](https://starsl.cn)
[![Commits](https://img.shields.io/github/commit-activity/m/starsliao/ConsulManager?color=ffff00)](https://github.com/starsliao/ConsulManager/commits/main)
[![open issues](http://isitmaintained.com/badge/open/starsliao/ConsulManager.svg)](https://github.com/starsliao/ConsulManager/issues)
[![GitHub Stargazers](https://img.shields.io/github/stars/starsliao/ConsulManager?color=ff69b4)](https://github.com/starsliao/ConsulManager/stargazers)
[![Python](https://img.shields.io/badge/python-%3E=v3.10-3776ab)](https://nodejs.org)
[![Node.js](https://img.shields.io/badge/node.js-%3E=v14-229954)](https://nodejs.org)
[![GitHub license](https://img.shields.io/badge/license-MIT-blueviolet)](https://github.com/starsliao/ConsulManager/blob/main/LICENSE)
[![OSCS Status](https://www.oscs1024.com/platform/badge/starsliao/ConsulManager.svg?size=small)](https://www.murphysec.com/dr/Zoyt5g0huRavAtItj2)
</div>

### 注意：v0.9版本开始镜像更换到华为云，请修改[docker-compose.yml](https://github.com/starsliao/ConsulManager/blob/main/docker-compose.yml)内的镜像地址。
- swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:latest
- swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:latest
---

# 🏷目录
* [🚀概述](#概述)
* [🌈实现功能](#实现功能)
* [📌更新记录](#更新记录)
* [🎨截图预览](#截图预览点击查看完整截图)
* [💾部署说明](#部署说明)
* [🥇最佳实践](#最佳实践)
* [💖特别鸣谢](#特别鸣谢)

## 🦄概述
>**ConsulManager**是一个使用Flask+Vue开发的WEB运维平台，弥补了Consul官方UI对Services管理的不足；并且基于Consul的服务发现与键值存储：实现了各云厂商资源与Prometheus的无缝同步，以及对各类监控资源的优雅管理与展示。

## 🌈实现功能
### 🎡Consul管理(比官方更优雅的Consul Web UI)
- 支持Consul Services的增删改查，可以批量删除Service。
- 直观的查看每个Services实例的信息，及整体Services的健康状态。
- 可以便捷的对Services实例的Tags、Meta、健康检查配置管理与查询。

### 💎云资源监控管理
>**基于Consul实现Prometheus监控目标的自动发现。**

- ✔**当前已支持对接阿里云、腾讯云、华为云。**

  - ✔支持多云ECS的**资源、分组、标签**自动同步到Consul(提供Prometheus自动发现)。
  - ✔支持多云ECS信息自动同步到**JumpServer**。
  - ✔支持多云MySQL资源信息自动同步到Consul(提供Prometheus自动发现)。
  - ✔支持多云**账户余额**与云资源**到期日**设置阈值告警通知。
- 支持自建主机接入WEB管理，并支持WEB批量导入自建主机到Consul。
- 提供了可查询分组、ECS、MySQL信息的页面，指标中加入了到期日等信息。
- 提供了按需生成Prometheus配置与ECS、MySQL告警规则的功能。
- 设计了一个支持同步的各字段展示的Node_Exporter、Mysqld_Exporter Grafana看板。
- **提供了一个支持1对多目标的Mysqld_exporter(官方main分支编译)：[使用1个mysqld_exporter就可以监控所有的MySQL了！](https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E7%9A%84%E4%BD%BF%E7%94%A8%E4%B8%80%E4%B8%AAmysqld_exporter%E7%9B%91%E6%8E%A7%E6%89%80%E6%9C%89%E7%9A%84MySQL%E5%AE%9E%E4%BE%8B.md)**

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

<details><summary>💥点击展开</summary>
  
### Consul Web Manager 界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/consul3.PNG)
### 多云ECS同步Consul界面
![](https://raw.githubusercontent.com/starsliao/ConsulManager/main/screenshot/ecs1.PNG)
### 多云ECS同步JumpServer界面
![图片](https://user-images.githubusercontent.com/3349611/180870935-56e536d2-0b71-4803-b5f8-0839a241c79a.png)
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

</details>
  
## 💾部署说明
##### 1. ConsulManager需要依赖`Consul`，请先完成Consul的部署。（[docs/Consul部署说明.md](https://github.com/starsliao/ConsulManager/blob/main/docs/Consul%E9%83%A8%E7%BD%B2%E8%AF%B4%E6%98%8E.md)）
##### 2. 使用`docker-compose`来部署ConsulManager
- 下载：`wget https://starsl.cn/static/img/docker-compose.yml`（仓库根目录下`docker-compose.yml`）
- 编辑：`docker-compose.yml`，修改3个环境变量：
  - **`consul_token`**：consul的登录token（[如何获取？](https://github.com/starsliao/ConsulManager/blob/main/docs/Consul%E9%83%A8%E7%BD%B2%E8%AF%B4%E6%98%8E.md#%E8%8E%B7%E5%8F%96%E7%99%BB%E5%BD%95token%E8%AE%B0%E5%BD%95secretid%E5%8D%B3%E4%B8%BAconsul%E7%99%BB%E5%BD%95%E7%9A%84token)）
  - **`consul_url`**：consul的URL(http开头，/v1要保留)
  - **`admin_passwd`**：登录ConsulManager Web的admin密码
- 启动：`docker-compose pull && docker-compose up -d`
- 访问：`http://{IP}:1026`，使用配置的ConsulManager admin密码登录
---
## 🥇最佳实践
- ### [ConsulManager：实践与FAQ](https://github.com/starsliao/ConsulManager/tree/main/docs)
- ### [应用场景1：如何优雅的基于Consul自动同步ECS主机监控](https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md)
- ### [应用场景2：如何优雅的使用Consul管理Blackbox站点监控](https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md)
- ### [应用场景3：如何把云主机自动同步到JumpServer](https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E6%8A%8A%E4%B8%BB%E6%9C%BA%E8%87%AA%E5%8A%A8%E5%90%8C%E6%AD%A5%E5%88%B0JumpServer.md)
- ### [应用场景4：使用1个mysqld_exporter监控所有的MySQL实例](https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E7%9A%84%E4%BD%BF%E7%94%A8%E4%B8%80%E4%B8%AAmysqld_exporter%E7%9B%91%E6%8E%A7%E6%89%80%E6%9C%89%E7%9A%84MySQL%E5%AE%9E%E4%BE%8B.md)


## 💖特别鸣谢
### 赞赏与关注公众号【**云原生DevOps**】加入交流群（请备注：consul），获取更多...

**如果看不到图片请点击该链接：[https://starsl.cn/static/img/thanks.png](https://starsl.cn/static/img/thanks.png)**
![](https://starsl.cn/static/img/thanks.png)

---

### 💰赞赏
##### 🥇榜一大哥：**@浩哥**
##### 🥈榜二大哥：**@Swancavalier**
##### 🥉榜三大哥：**@南城阿宇** **@新的奇迹** **@李宫俊**
##### 🏆榜N大哥：
@mac🐬 🌈  @Stephen  @蔡志昆  @风与尘的誓约  @Initᯤ⁶ᴳ  @254209  @Runner91  @烂泥  @ASL·D·阿威  @惊雷

---

### ✅提交代码
[@dbdocker](https://github.com/dbdocker)

---

### 🎃提交bug
@会飞的鱼  [@奈](https://github.com/Wp516781950)  @Swancavalier  [@Show_Lo](https://github.com/ShowXian)

---

### 📢提供建议
[@dong9205](https://github.com/dong9205)  [@dissipator](https://github.com/dissipator) @烂泥

---

### 🏆开源推荐
[🌉Go-Ldap-Admin: 基于Go+Vue实现的openLDAP后台管理项目](https://github.com/eryajf/go-ldap-admin)

---

# 💖感谢伟大的[Flask](https://github.com/pallets/flask)、[VUE](https://github.com/vuejs/vue)、[vue-admin-template](https://github.com/PanJiaChen/vue-admin-template)
