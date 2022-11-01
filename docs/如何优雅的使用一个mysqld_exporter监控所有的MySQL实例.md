# 如何优雅的使用一个mysqld_exporter监控所有的MySQL实例
### 一、如何在ConsulManager中接入云厂商的数据库
1. 新增云账号的情况：目前新增时，支持多选区域，以及选择增加的资源类型，勾选MySQL即可接入自动同步云数据库，记得设置好同步间隔。

![图片](https://user-images.githubusercontent.com/3349611/199262165-3582e051-a924-4043-bc05-96643b17caca.png)

2. 对已经添加过的账号，增加同步云数据库资源：点击编辑云资源，选择好需要编辑的厂商、账号及区域，再勾选资源类型MySQL，配置上同步间隔即可增加自动同步云数据库。

![图片](https://user-images.githubusercontent.com/3349611/199264858-f2a325bf-fad2-4850-bc39-76e9271d883e.png)

3. 接入完成后，可手动点击同步按钮，完成首次同步；或者等待设定好的同步周期后会自动同步。

![图片](https://user-images.githubusercontent.com/3349611/199267039-a010ce6f-3e04-4e54-8e44-6bde7ff5a000.png)

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
![图片](https://user-images.githubusercontent.com/3349611/199270662-f4f280ed-f6b8-482b-bb28-5cc4d3799dc1.png)
