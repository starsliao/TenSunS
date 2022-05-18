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
### blackbox_exporter监控某个站点有异常，如何debug
- 在blackbox检测该站点的链接末尾加上`&debug=true`，请求即可，例如：
```
http://10.0.0.26:9115/probe?module=http_2xx&target=https%3A%2F%2Fpayapp.weixin.qq.com&debug=true
```
- 在blackbox_exporter的启动命令增加参数`--log.level=debug`，即可开启blackbox_exporter的debug日志，systemd方式启动的日志追踪方式：
```
journalctl -u blackbox_exporter.service -n20 -f
```
