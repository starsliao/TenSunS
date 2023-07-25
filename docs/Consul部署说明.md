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
> 编辑配置文件`/etc/consul.d/consul.hcl`
```bash
data_dir = "/opt/consul"
log_level = "warn"

# 服务器有多个IP启动会报错请增加这行配置:填写服务器IP,如果启动或运行有报错,可以尝试去掉这行
advertise_addr = "192.168.x.x"

client_addr = "0.0.0.0"
ui_config{
  enabled = true
}
server = true
bootstrap_expect=1
acl = {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
  tokens = {
    initial_management = "生成的UUID"
    agent = "生成的UUID,和上面保持一致"
  }
}
```

#### 启动服务

```bash
mkdir /opt/consul
chown -R consul:consul /opt/consul
systemctl enable consul.service
systemctl start consul.service
```

### consul kv 备份还原
```
consul kv export --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx '' > consul_kv_bak.json
consul kv import --http-addr=http://127.0.0.1:8500 -token=xxxxxxxx @consul_kv_bak.json
```
