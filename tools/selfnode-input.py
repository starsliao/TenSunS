#!/usr/bin/python3
import requests,json
consul_token = 'xxxxxxxxxx'  #Consul SecretID
consul_url = 'http://x.x.x.x:8500/v1'

with open('selfnode-instance.list', 'r') as file:
  lines = file.readlines()
  for line in lines:
    if line.startswith('#'):
        continue
    vendor,account,region,group,name,instance,os = line.split()
    headers = {'X-Consul-Token': consul_token}
    sid = f"{vendor}/{account}/{region}/{group}@{name}"
    ip = instance.split(':')[0]
    port = instance.split(':')[1]
    data = {
            "id": sid,
            "name": 'selfnode_exporter',
            'Address': ip,
            'port': int(port),
            "tags": [vendor,os],
            "Meta": {'vendor':vendor,'account':account,'region':region,'group':group,
                     'name':name,'instance':instance,'os':os},
            "check": {"tcp": instance,"interval": "60s"}
           }

    reg = requests.put(f"{consul_url}/agent/service/register", headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        print({"code": 20000,"data": "增加成功！"})
    else:
        print({"code": 50000,"data": f'{reg.status_code}:{reg.text}'})
