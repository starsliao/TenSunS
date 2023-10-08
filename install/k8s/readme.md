## 2023-10-8前使用该install.sh脚本在K8S部署consul的同学请注意.
1. **完成第3步操作前不要删除consul的pod,也不要重启consul,否则会造成所有Consul KV数据丢失**
2. 使用kubectl进入conusl的容器`kubectl exec -i -t -n tensuns consul-0 -c consul -- sh -c "sh"`
3. 备份consul的KV存储数据(确保你部署的consul使用了持久化存储,以下命令会备份到持久化存储映射的目录下:`/consul/data/`.)
```
consul kv export --http-addr=http://127.0.0.1:8500 -token=$(cat /consul/config/consul.hcl|grep agent|awk -F\" '{print $2}') '' > /consul/data/consul_kv_bak.json
```
4. 修改consul的Stateful Sets的yaml文件, 找到`image`字段下面, 增加`args`部分:
```
          args:
            - agent
```
  - 增加完成后应该是如下效果:
```
...
      containers:
        - name: consul
          image: swr.cn-south-1.myhuaweicloud.com/starsl.cn/consul:latest
          args:
            - agent
          ports:
            - name: http
              containerPort: 8500
              protocol: TCP
...
```
5. 保存后重启consul的Stateful Sets
6. 启动完成后再次使用第2步进入consul容器
7. 恢复consul的KV存储数据
```
consul kv import --http-addr=http://127.0.0.1:8500 -token=$(cat /consul/config/consul.hcl|grep agent|awk -F\" '{print $2}') @/consul/data/consul_kv_bak.json
```
8. 完成,可再次重启consul后,验证consul kv数据是否丢失(能正常登录TenSunS说明KV数据正常).
