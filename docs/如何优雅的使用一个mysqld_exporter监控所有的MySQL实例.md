# 如何优雅的使用一个mysqld_exporter监控所有的MySQL实例
### 一、如何在ConsulManager中接入云厂商的数据库
1. 新增云账号的情况：目前新增时，支持多选区域，以及选择增加的资源类型，勾选MySQL即可接入自动同步云数据库，记得设置好同步间隔。

![图片](https://user-images.githubusercontent.com/3349611/199262165-3582e051-a924-4043-bc05-96643b17caca.png)

2. 对已经添加过的账号，增加同步云数据库资源：点击编辑云资源，选择好需要编辑的厂商、账号及区域，再勾选资源类型MySQL，配置上同步间隔即可增加自动同步云数据库。

![图片](https://user-images.githubusercontent.com/3349611/199264858-f2a325bf-fad2-4850-bc39-76e9271d883e.png)

3. 接入完成后，可手动点击同步按钮，完成首次同步；或者等待设定好的同步周期后会自动同步。

![图片](https://user-images.githubusercontent.com/3349611/199267039-a010ce6f-3e04-4e54-8e44-6bde7ff5a000.png)

4. 同步完成后，可在`云资源管理`-`MySQL管理`-`云MySQL列表`，查看同步的云数据库信息。
![图片](https://user-images.githubusercontent.com/3349611/199276321-f8523931-b56d-43ca-84bd-def33f70b8eb.png)


### 二、部署一个支持多实例的Mysqld_exporter

> 官方main版本的代码已经支持多目标的mysqld_exporter，只是还没有发Releases。所以基于最新的main版本自行编译了一个mysqld_exporter，并且做成了docker镜像。

详细说明查看：https://github.com/starsliao/multi_mysqld_exporter

新建一个`docker-compose.yml`，内容如下：

```
version: "3.2"
services:
  mysqld_exporter:
    image: swr.cn-south-1.myhuaweicloud.com/starsl.cn/mysqld_exporter:latest
    container_name: mysqld_exporter
    hostname: mysqld_exporter
    restart: always
    ports:
      - "9104:9104"
    volumes:
      - /usr/share/zoneinfo/PRC:/etc/localtime
    environment:
      MYSQLD_EXPORTER_PASSWORD: xxxxxxxxxxxxx
    entrypoint:
      - /bin/mysqld_exporter
      - --collect.info_schema.innodb_metrics
      - --collect.info_schema.tables
      - --collect.info_schema.processlist
      - --collect.info_schema.tables.databases=*
      - --mysqld.username=xxxxxxxxxx
```

- docker-compose中有2个变量：监控专用的mysql账号和密码，注意修改掉后再启动。
- docker-compose配置方式是**所有的mysql实例都配置了一样的mysql监控账号和密码。**
- 如果你有不同mysql实例需要配置不同监控账号密码的需求，请参考官方readme使用配置文件的方式启动。

启动：`docker-compose up -d`

### 三、如何接入到Prometheus
点击菜单`云资源管理`-`MySQL管理`-`prometheus配置`
在右侧选择需要加入监控的云账号RDS组，并且输入mysqld_exporter的IP和端口，点击生成配置，即可复制生成的JOB内容到prometheus。
![图片](https://user-images.githubusercontent.com/3349611/199271393-6a7083dc-e861-4ce1-b4da-4ef99aa72868.png)


### 四、参考告警规则
![图片](https://user-images.githubusercontent.com/3349611/199274588-85f39fa1-8401-41f5-b0eb-4059a5e45007.png)

### 五、参考Grafana看板
[GRAFANA：Mysqld Exporter Dashboard 22_11_01中文版](https://grafana.com/orgs/starsliao/dashboards/17320)

![mysql1](https://user-images.githubusercontent.com/3349611/199293017-ecd09b7d-4731-44f0-9cc8-eefdd59550a1.png)

![mysql2](https://user-images.githubusercontent.com/3349611/199293035-dd6a911c-838d-4f01-93d3-14bda375ee64.png)
