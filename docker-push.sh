#!/bin/bash
vf=0.1.3
vb=0.2.0
docker login --username=starsliao@163.com registry.cn-shenzhen.aliyuncs.com

docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${vf}

docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${vb}

docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${vf}
docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${vb}
