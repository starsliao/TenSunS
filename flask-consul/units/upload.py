#!/usr/bin/python3
import requests, json
import xlrd
import sys
sys.path.append("..")
from config import consul_token,consul_url

def importconsul(row):
    module, company, project, env, name, instance = row
    headers = {'X-Consul-Token': consul_token}
    data = {
            "id": f"{module}/{company}/{project}/{env}@{name}",
            "name": 'blackbox_exporter',
            "tags": [module],
            "Meta": {'module': module, 'company': company, 'project': project, 'env': env, 'name': name,
                     'instance': instance}
    }

    reg = requests.put(f"{consul_url}/agent/service/register", headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        print({"code": 20000, "data": "增加成功！"},instance,flush=True)
    else:
        print({"code": 50000, "data": f'{reg.status_code}:{reg.text}'},instance,flush=True)

def read_execl(file_contents):
    data = xlrd.open_workbook(file_contents=file_contents, encoding_override="utf-8")
    table = data.sheets()[0]
    print("开始读取",flush=True)
    for rownum in range(table.nrows):
        row = table.row_values(rownum)
        if rownum == 0:
            continue
        importconsul(row)
    return {"code": 20000, "data": f"导入成功！"}
