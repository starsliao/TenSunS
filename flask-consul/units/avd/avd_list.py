import sys,requests,hashlib,json
from datetime import datetime
from bs4 import BeautifulSoup
from units import consul_kv
from units.config_log import *

def get_avd():
    avd_url = 'https://avd.aliyun.com'
    res = requests.get(avd_url + '/high-risk/list')
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    bugs = soup.select('tr')
    last_avd = consul_kv.get_value('ConsulManager/avd/list/0')
    now = datetime.now().strftime('%Y-%m-%d')
    if last_avd != {}:
        del last_avd['avd_collect']
    for index, avd_info in enumerate(bugs[1:]):
        avd = avd_info.select('td')
        avd_dict = {}
        avd_dict['avd_id'] = avd[0].getText(strip=True)
        avd_dict['avd_id_url'] = avd_url + avd[0].a.attrs['href']
        avd_dict['avd_name'] = avd[1].getText(strip=True)
        avd_dict['avd_type'] = avd[2].button.attrs.get('title',avd[2].getText(strip=True))
        avd_dict['avd_time'] = avd[3].getText(strip=True)
        avd_dict['avd_stat'] = avd[4].select('button')[1].attrs['title']
        if index == 0 and avd_dict == last_avd:
            logger.info('【JOB】===> avd_list 未采集到新漏洞。')
            break
        else:
            avd_dict['avd_collect'] = now
            consul_kv.put_kv(f'ConsulManager/avd/list/{index}',avd_dict)
            if index == 0:
                logger.info(f'【JOB】===> avd_list {avd_dict}')
                avd_switch = consul_kv.get_value('ConsulManager/avd/switch')
                wecomwh = avd_switch.get('wecomwh','')
                dingdingwh = avd_switch.get('dingdingwh','')
                feishuwh = avd_switch.get('feishuwh','')
                content = f"# <font color=\"#ff0000\">{avd_dict['avd_name']}</font>\n" \
                    f"- 编号：{avd_dict['avd_id']}[【详情】]({avd_dict['avd_id_url']})\n" \
                    f"- 类型：{avd_dict['avd_type']}\n" \
                    f"- 披露：{avd_dict['avd_time']}\n" \
                    f"- 状态：<font color=\"#ff0000\">{avd_dict['avd_stat']}</font>({avd_dict['avd_collect']})\n"
                if avd_dict['avd_id'] == last_avd.get('avd_id'):
                    content = content + '(已披露漏洞，今日推送为状态或类型有更新。)\n'
                if avd_switch['switch'] and avd_switch.get('wecom',False) and wecomwh.startswith('https://qyapi.weixin.qq.com'):
                    wecom(wecomwh,content)
                if avd_switch['switch'] and avd_switch.get('dingding',False) and dingdingwh.startswith('https://oapi.dingtalk.com'):
                    dingding(dingdingwh,content)
                if avd_switch['switch'] and avd_switch.get('feishu',False) and feishuwh.startswith('https://open.feishu.cn'):
                    title = '漏洞告警:' + avd_dict['avd_name']
                    md = f"编号：{avd_dict['avd_id']}[【详情】]({avd_dict['avd_id_url']})\n" \
                         f"类型：{avd_dict['avd_type']}\n" \
                         f"披露：{avd_dict['avd_time']}\n" \
                         f"状态：**{avd_dict['avd_stat']}**({avd_dict['avd_collect']})"
                    if avd_dict['avd_id'] == last_avd.get('avd_id'):
                        md = md + '\n(已披露漏洞，今日推送为状态或类型有更新。)'
                    feishu(feishuwh,title,md)
                
def wecom(webhook,content):
    headers = {'Content-Type': 'application/json'}
    params = {'msgtype': 'markdown', 'markdown': {'content' : content}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    logger.info(f'【wecom】{response.json()}')

def dingding(webhook,content):
    headers = {'Content-Type': 'application/json'}
    params = {"msgtype":"markdown","markdown":{"title":"漏洞告警","text":content},"at":{"isAtAll":True}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    logger.info(f'【dingding】{response.json()}')

def feishu(webhook,title,md):
    headers = {'Content-Type': 'application/json'}
    params = {"msg_type": "interactive",
              "card": {"header": {"title": {"tag": "plain_text","content": title},"template": "red"},
                       "elements": [{"tag": "markdown","content": f"{md}\n<at id=all></at>",}]}}
    data = json.dumps(params)
    response = requests.post(webhook, headers=headers, data=data)
    logger.info(f'【feishu】{response.json()}')
