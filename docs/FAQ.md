### 查后端实时日志（先进入docker-compose.yml所在目录）
```
docker-compose logs --tail=50 -f flask-consul
```
### 查前端实时日志（先进入docker-compose.yml所在目录）
```
docker-compose logs --tail=50 -f nginx-consul
```
### 后端报错requests.exceptions.ConnectionError: HTTPConnectionPool(host='xxx', port=8500)
![图片](https://user-images.githubusercontent.com/3349611/219944354-7be4c686-ff8e-4a03-8939-0fd6dedfb1b7.png)
- 这是由于flask-consul容器无法连接到consul服务端，请检查容器到consul的网络是否通。
- 可以检查下iptables防火墙规则，设置允许访问8500端口：
```
# 参考命令
iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 8500 -j ACCEPT
firewall-cmd --zone=public --add-port=8500/tcp --permanent
```

### 检查consul连接是否正常？
```
# 进入容器：
docker-compose exec flask-consul sh
# 如果flask-consul容器无法正常启动，可以进入nginx-consul容器测试
docker-compose exec nginx-consul sh
# 执行检查:
nc -vz {consul_ip} 8500
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
### prometheus配置告警规则后报错怎么办？
- 进入prometheus所在的目录，执行如下命令即可检查：
```
./promtool check rules ./rules.yml 
```
