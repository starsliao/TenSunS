#### 安装
> 以下为CentOS7安装说明,其它系统安装部分请参考官网:
> https://developer.hashicorp.com/consul/downloads
```bash
# 使用yum部署consul
yum install -y yum-utils
yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
yum -y install consul
# 如果yum下载失败，可以直接下载RPM包安装
wget https://rpm.releases.hashicorp.com/RHEL/7/x86_64/stable/consul-1.16.0-1.x86_64.rpm
rpm -ivh ./consul-1.16.0-1.x86_64.rpm
``` 

#### 配置
> 执行以下命令获取UUID,填写到下面配置末尾部分,作为最高权限的token
```bash
uuidgen
```
> `/etc/consul.d/consul.hcl`完整配置内容
```bash
data_dir = "/opt/consul"
log_level = "error"

# 服务器有多个IP启动会报错请增加这行配置：填写服务器IP。
advertise_addr = "192.168.x.x"

client_addr = "0.0.0.0"
ui_config{
  enabled = true
}
ports = {
  grpc = -1
  https = -1
  dns = -1
  grpc_tls = -1
  serf_wan = -1
}
peering {
  enabled = false
}
connect {
  enabled = false
}
server = true
bootstrap_expect=1
acl = {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
  tokens {
    initial_management = "生成的UUID"
    agent = "生成的UUID,和上面保持一致"
  }
}
```

#### 启动服务

```bash
mkdir /opt/consul
chown -R consul:consul /opt/consul
sed -i 's/Type=notify/Type=exec/g' /usr/lib/systemd/system/consul.service
systemctl daemon-reload
systemctl enable consul.service
systemctl restart consul.service
```

### consul kv 备份还原
```
consul kv export --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx '' > consul_kv_bak.json
consul kv import --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx @consul_kv_bak.json
```

---

## 历史版本配置记录

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
