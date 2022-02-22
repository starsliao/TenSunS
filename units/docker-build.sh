#!/bin/bash
eth=$(ls /sys/class/net/ | grep -v "`ls /sys/devices/virtual/net/`")
ip=$(ip addr | grep $eth | awk '/^[0-9]+: / {}; /inet.*global/ {print gensub(/(.*)\/(.*)/, "\\1", "g", $2)}' | head -1)
cd flask-consul
docker build -t flask-consul:latest .
cd ../vue-consul
docker build -t nginx-consul:latest .

echo -e "\n\n自行编译的版本，注意修改docker-compose.yml中的镜像地址为本地仓库后再启动。"
echo -e "\n\nBlackbox-Manager:\nhttp://${ip}:1026"
