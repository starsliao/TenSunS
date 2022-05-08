### 查后端实时日志（先进入docker-compose.yml所在目录）
```
docker-compose logs --tail=10 -f flask-consul
```
### 查前端实时日志（先进入docker-compose.yml所在目录）
```
docker-compose logs --tail=10 -f flask-vue
```
### 检查consul连接是否正常
```
进入容器，执行:
nc -vz {ip} 8500
```
