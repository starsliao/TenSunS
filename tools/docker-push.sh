#!/bin/bash
ver=0.26
docker login --username=youremail registry.cn-shenzhen.aliyuncs.com

docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${ver}

docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${ver}

docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${ver}
docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${ver}
