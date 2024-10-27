#!/usr/bin/python3
import csv,re
from io import StringIO
import requests, json, traceback
import xlrd,re,sys
sys.path.append("..")
from config import consul_token,consul_url
from units.config_log import *

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
            logger.info(row)
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
                #"check": {"tcp": instance,"interval": "60s"}
            }
        elif imptype == 'selfrds':
            vendor,account,region,group,name,instance,os = row
            logger.info(row)
            sid = f"{vendor}/{account}/{region}/{group}@{name}@rds"
            ip = instance.split(':')[0]
            port = instance.split(':')[1]
            data = {
                "id": sid,
                "name": 'selfrds_exporter',
                'Address': ip,
                'port': int(port),
                "tags": [vendor,os],
                "Meta": {'vendor':vendor,'account':account,'region':region,'group':group,
                         'name':name,'instance':instance,'os':os},
                "check": {"tcp": instance,"interval": "60s"}
            }
        elif imptype == 'selfredis':
            vendor,account,region,group,name,instance,os = row
            logger.info(row)
            sid = f"{vendor}/{account}/{region}/{group}@{name}@redis"
            ip = instance.split(':')[0]
            port = instance.split(':')[1]
            data = {
                "id": sid,
                "name": 'selfredis_exporter',
                'Address': ip,
                'port': int(port),
                "tags": [vendor,os],
                "Meta": {'vendor':vendor,'account':account,'region':region,'group':group,
                         'name':name,'instance':instance,'os':os},
                "check": {"tcp": instance,"interval": "60s"}
            }
    except Exception as e:
        logger.error(f"【import】导入失败,{e}\n{traceback.format_exc()}")
        return {"code": 50000, "data": f"导入内容格式异常！{row}"} 
    headers = {'X-Consul-Token': consul_token}

    reg = requests.put(f"{consul_url}/agent/service/register", headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        logger.info(f'code: 20000, data: 增加成功！{instance}')
        return {"code": 20000, "data": "增加成功！"}
    else:
        logger.info(f'code: 50000, data: {reg.status_code}:{reg.text},{instance}')
        return {"code": 50000, "data": f'{reg.status_code}:{reg.text}'}

def read_execl(file_contents,imptype):
    data = xlrd.open_workbook(file_contents=file_contents, encoding_override="utf-8")
    table = data.sheets()[0]
    logger.info("【import】开始读取导入文件")
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
                    j = re.sub('[[ \]`~!\\\#$^/&*=|"{}\':;?\t\n]','_',j)
                nrow.append(j)
        imp = importconsul(nrow,imptype)
        if imp['code'] == 50000:
            return imp
    return {"code": 20000, "data": f"导入成功！共导入 {rownum} 条数据。"}

import csv
import re

def read_csv(file_content, imptype):
    file_content_str = file_content.decode('utf-8')
    # 使用StringIO创建一个模拟的文件对象
    csvfile = StringIO(file_content_str)
    # 初始化一个空列表来存储处理后的数据
    processed_rows = []

    # 使用csv模块读取CSV文件
    reader = csv.reader(csvfile)
    next(reader) # 跳过表头行，如果有

    # 遍历CSV文件的每一行
    for row in reader:
        nrow = []  # 初始化一个空列表来存储当前行的处理结果

        # 遍历当前行的每个单元格
        for cell in row:
            cell = cell.strip()  # 去除字符串两端的空白字符

            # 尝试将单元格内容转换为数字
            try:
                # 尝试转换为浮点数，然后检查是否为整数
                num = float(cell)
                if num.is_integer():
                    num = int(num)
                nrow.append(str(num))  # 将数字转换为字符串并添加到列表中
            except ValueError:
                # 如果转换失败，则执行字符串清洗操作
                if cell:  # 如果字符串非空
                    # 替换特殊字符为下划线，除了第6个单元格（索引为5）外
                    if row.index(cell) != 5:
                        cell = re.sub(r'[[\]`~!\\\#$^/&*=|"{}\':;?\t\n]', '_', cell)
                else:
                    cell = '_'  # 空字符串替换为下划线
                nrow.append(cell)  # 将清洗后的字符串添加到列表中

        # 处理完当前行后，将其添加到processed_rows列表中
        processed_rows.append(nrow)

        imp = importconsul(nrow, imptype)
        if imp['code'] == 50000:
            return imp

    # 返回处理后的数据或其他信息，例如成功消息和处理的行数
    return {"code": 20000, "data": f"处理成功！共处理 {len(processed_rows)} 条数据。", "rows": processed_rows}
