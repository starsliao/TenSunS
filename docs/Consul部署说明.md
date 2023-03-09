#### 安装
##### 注意：暂时不兼容consul-1.15.x的版本，已安装1.15.x版本的请先卸载后安装以下版本。

```bash
# 使用yum部署consul
yum install -y yum-utils
yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
yum -y install consul-1.14.5-1
# 如果yum下载失败，可以直接下载RPM包安装
wget https://rpm.releases.hashicorp.com/RHEL/7/x86_64/stable/consul-1.14.5-1.x86_64.rpm
rpm -ivh ./consul-1.14.5-1.x86_64.rpm
``` 

#### 配置

```bash
vi /etc/consul.d/consul.hcl
log_level = "ERROR" #日志级别，日志太多可以只打印error日志，不需要可以去掉这行。
advertise_addr = "192.168.x.x" #填写你的网卡IP，如果启动或运行有报错，可以尝试去掉这行。
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

#### 启动服务

```bash
chown -R consul:consul /opt/consul  #注意下数据目录的权限。
systemctl enable consul.service
systemctl start consul.service
```

### 安装后首次获取登录Token（记录SecretID，即为Consul登录的Token）
```bash
consul acl bootstrap|grep SecretID
```


### 忘记global-management Token，重新生成
```
# 记录最后的reset index: xx
consul acl bootstrap

# 进入consul数据目录执行
echo 13 > acl-bootstrap-reset

# 重新创建一个global-management Token
consul acl bootstrap
```

### consul kv 备份还原
```
consul kv export --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx '' > consul_kv_bak.json
consul kv import --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx @consul_kv_bak.json
```
