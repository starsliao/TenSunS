#!/bin/bash
uuid=`uuidgen`
mkdir -p /opt/consul/config
cat <<EOF > /opt/consul/config/consul.hcl
log_level = "error"
data_dir = "/consul/data"
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
    initial_management = "$uuid"
    agent = "$uuid"
  }
}
EOF
chmod 777 -R /opt/consul/config
cat <<EOF > /opt/consul/docker-compose.yaml
version: '3.6'
services:
  consul:
    image: swr.cn-south-1.myhuaweicloud.com/starsl.cn/consul:latest
    hostname: consul
    container_name: consul
    restart: always
    ports:
      - "8500:8500"
    volumes:
      - /opt/consul/data:/consul/data
      - /opt/consul/config:/consul/config
      - /usr/share/zoneinfo/PRC:/etc/localtime
    ports:
      - "8500:8500"
    command: "agent"
    networks:
      - TenSunS

networks:
  TenSunS:
    name: TenSunS
    driver: bridge
    ipam:
      driver: default
EOF

echo "请进入/opt/consul目录执行 docker-compose up -d 启动consul"
echo "consul的管理员token是: $uuid"
