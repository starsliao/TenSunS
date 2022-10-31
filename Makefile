help:
	echo "Read Makefile" && echo "make build" && echo "make push ver=x.x.x"
build:
	cd flask-consul && docker build -t flask-consul:latest .
	cd vue-consul && docker build -t nginx-consul:latest .
	cd vue-consul && docker build -t nginx-consul:tensuns-latest -f Dockerfile.tensuns .
	echo -e "\n\n自行编译的版本，注意修改docker-compose.yml中的镜像地址为本地仓库后再启动。\nBlackbox-Manager:\nhttp://{ip}:1026\n"

push:
	#docker login --username=starsliao@163.com registry.cn-shenzhen.aliyuncs.com
	docker tag nginx-consul:latest swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:latest
	docker tag nginx-consul:latest swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:${ver}
	docker tag flask-consul:latest swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:latest
	docker tag flask-consul:latest swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:${ver}
	docker push swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:latest
	docker push swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:${ver}
	docker push swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:latest
	docker push swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:${ver}
	docker tag nginx-consul:tensuns-latest swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:tensuns-latest
	docker push swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:tensuns-latest

update:
	docker-compose pull && docker-compose up -d
