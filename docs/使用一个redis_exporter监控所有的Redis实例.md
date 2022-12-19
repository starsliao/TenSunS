# 使用一个redis_exporter监控所有的Redis实例
### 一、如何在ConsulManager中接入云厂商的Redis
1. 新增云账号的情况：目前新增时，支持多选区域，以及选择增加的资源类型，勾选REDIS即可接入自动同步云REDIS，记得设置好同步间隔。

![图片](https://user-images.githubusercontent.com/3349611/204356330-330865fd-6eea-48eb-88e1-757e7ea4a0b1.png)


2. 对已经添加过的账号，增加同步云REDIS资源：点击编辑云资源，选择好需要编辑的厂商、账号及区域，再勾选资源类型REDIS，配置上同步间隔即可增加自动同步云REDIS。

![图片](https://user-images.githubusercontent.com/3349611/204356547-3d6b8b57-33f4-4938-ac4a-cf9e5abe2a31.png)


3. 接入完成后，可手动点击同步按钮，完成首次同步；或者等待设定好的同步周期后会自动同步。

![图片](https://user-images.githubusercontent.com/3349611/204356757-be3e86da-dff6-44ca-8086-a033a9750067.png)


4. 同步完成后，可在`云资源管理`-`REDIS管理`-`云REDIS列表`，查看同步的云redis信息以及自定义实例监控的IP和端口（再次同步不会覆盖实例自定义的IP端口信息）。
![图片](https://user-images.githubusercontent.com/3349611/204357662-09f44475-9545-4667-abf1-29bbb78a4935.png)

#### 接入自建redis
1. 进入`云资源管理`-`REDIS管理`-`自建REDIS管理`，即可新增或批量导入自建的redis列表。
![图片](https://user-images.githubusercontent.com/3349611/208393735-bb7a0ee2-59ef-4a0c-8430-a5c32552d7cc.png)


### 二、部署一个支持多实例的redis_exporter

> 官方仓库：https://github.com/oliver006/redis_exporter

新建一个`docker-compose.yml`，内容如下：

```
version: "3.2"
services:
  redis-exporter:
    image: oliver006/redis_exporter
    container_name: redis-exporter
    restart: unless-stopped
    command:
      - "-redis.password-file=/redis_passwd.json"
    volumes:
      - /usr/share/zoneinfo/PRC:/etc/localtime
      - /data/redis-exporter/redis_passwd.json:/redis_passwd.json
    expose:
      - 9121
    network_mode: "host"
```
新建一个redis的实例地址与密码文件，`/data/redis-exporter/redis_passwd.json`：
```
{
  "redis://xxxxxxxxxxx.dcs.huaweicloud.com:6379":"",
  "redis://aaaaaaaa.cn-south-1.dcs.myhuaweicloud.com:6379":"q1azw2sx"
}
```
- docker-compose中挂载配置文件文件的本地路径注意根据实际情况修改。
- 配置文件的格式为json，每行一个实例的信息格式为："redis://`实例地址端口`":"`redis密码`"
- `实例地址端口`请查看`云REDIS列表`或`自建redis管理`的`实例`字段。
- 如redis无密码，保留空双引号即可`""`。

启动：`docker-compose up -d`

### 三、如何接入到Prometheus
点击菜单`云资源管理`-`REDIS管理`-`prometheus配置`：
- 在右侧选择需要加入监控的云账号REDIS组，并且输入redis_exporter的IP和端口，点击生成配置，即可复制生成的JOB内容到prometheus。
- 由于Redis_Exporter无法监控到云数据库的CPU、部分资源使用率的情况，所以ConsulManager开发了Exporter功能，配置到Prometheus即可直接从云厂商采集到这些指标！选择需要采集指标的REDIS账号区域，ConsulManager地址和端口，即可生成Prometheus的JOB配置。

![图片](https://user-images.githubusercontent.com/3349611/204361542-c922963d-e79e-4ffd-8e3b-d752bd198d7b.png)

### 四、参考告警规则
![图片](https://user-images.githubusercontent.com/3349611/204361766-6584b1db-c91f-438b-a74f-b475fbd511f8.png)

### 五、参考Grafana看板
[GRAFANA：Redis Exporter Dashboard 中文版](https://grafana.com/grafana/dashboards/17507)

![图片](https://user-images.githubusercontent.com/3349611/204360251-d0486e7c-9a46-43c8-8397-b0dca521e0e9.png)

