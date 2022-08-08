#!/usr/bin/python3
import requests, json
import xlrd,re,sys
sys.path.append("..")
from config import consul_token,consul_url

def importconsul(row,imptype):
    try:
        if imptype == 'blackbox':
            module, company, project, env, name, instance = row
            data = {
                "id": f"{module}/{company}/{project}/{env}@{name}",
                "name": 'blackbox_exporter',
                "tags": [module],
                "Meta": {'module': module, 'company': company, 'project': project,
                         'env': env, 'name': name,'instance': instance}
            }
        elif imptype == 'selfnode':
            vendor,account,region,group,name,instance,os = row
            print(row)
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
    except Exception as e:
        print("【import】导入失败",e,flush=True)
        return {"code": 50000, "data": f"导入内容格式异常！{row}"} 
    headers = {'X-Consul-Token': consul_token}

    reg = requests.put(f"{consul_url}/agent/service/register", headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        print({"code": 20000, "data": "增加成功！"},instance,flush=True)
        return {"code": 20000, "data": "增加成功！"}
    else:
        print({"code": 50000, "data": f'{reg.status_code}:{reg.text}'},instance,flush=True)
        return {"code": 50000, "data": f'{reg.status_code}:{reg.text}'}

def read_execl(file_contents,imptype):
    data = xlrd.open_workbook(file_contents=file_contents, encoding_override="utf-8")
    table = data.sheets()[0]
    print("【import】开始读取导入文件",flush=True)
    for rownum in range(table.nrows):
        row = table.row_values(rownum)
        if rownum == 0:
            continue
        nrow = []
        for i in row:
            try:
                float(i)
                if i % 1 == 0:
                    i = int(i)
                nrow.append(str(i))
            except:
                j = i.strip()
                j = '_' if j == '' else j
                if i != row[5]:
                    j = re.sub('[[ \]`~!\\\#$^/&*=|"{}\':;?]','_',j)
                nrow.append(j)
        imp = importconsul(nrow,imptype)
        if imp['code'] == 50000:
            return imp
    return {"code": 20000, "data": f"导入成功！共导入 {rownum} 条数据。"}
