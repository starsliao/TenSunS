#!/bin/bash
tsspath="/opt/tensuns"
mkdir -p $tsspath

cat <<EOF > $tsspath/docker-compose.yaml
version: '3.6'
services:
  flask-consul:
    image: swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:latest
    container_name: flask-consul
    hostname: flask-consul
    restart: always
    volumes:
      - /usr/share/zoneinfo/PRC:/etc/localtime
    environment:
      consul_token: xxxxx-xxxxx-xxxxx
      consul_url: http://x.x.x.x:8500/v1
      admin_passwd: xxxxxxxx
      log_level: INFO
    networks:
      - TenSunS

  nginx-consul:
    image: swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:latest
    container_name: nginx-consul
    hostname: nginx-consul
    restart: always
    ports:
      - "1026:1026"
    volumes:
      - /usr/share/zoneinfo/PRC:/etc/localtime
    depends_on:
      - flask-consul
    networks:
      - TenSunS

networks:
  TenSunS:
    name: TenSunS
    driver: bridge
    ipam:
      driver: default
EOF


echo -e "\n编辑：$tsspath/docker-compose.yaml，修改3个环境变量：\n\033[31;1mconsul_token\033[0m：consul的登录token（安装consul时生成的UUID）\n\033[31;1mconsul_url\033[0m：consul的URL(http开头，/v1要保留)\n\033[31;1madmin_passwd\033[0m：登录后羿运维平台admin用户的密码\n"
echo "启动：cd $tsspath && docker-compose up -d"
echo -e "\n请使用浏览器访问 http://{你的IP}:1026 并登录使用\n"
echo -e "\033[31;1mhttp://`ip route get 1.2.3.4 | awk '{print $NF}'|head -1`:1026\033[0m\n"
