help:
	echo "Read Makefile"

build:
	cd flask-consul && docker build -t flask-consul:latest .
	cd vue-consul && docker build -t nginx-consul:latest .
	echo -e "\n\n自行编译的版本，注意修改docker-compose.yml中的镜像地址为本地仓库后再启动。"
	echo -e "\n\nBlackbox-Manager:\nhttp://{ip}:1026"

push:
	docker login --username=starsliao@163.com registry.cn-shenzhen.aliyuncs.com
	docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
	docker tag nginx-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${vf}
	docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
	docker tag flask-consul:latest registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${vb}
	docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:latest
	docker push registry.cn-shenzhen.aliyuncs.com/starsl/nginx-consul:${vf}
	docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:latest
	docker push registry.cn-shenzhen.aliyuncs.com/starsl/flask-consul:${vb}

update:
	docker-compose pull && docker-compose up -d
