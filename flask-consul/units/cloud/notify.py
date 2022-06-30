import requests,json
def wecom(webhook,content):
    headers = {'Content-Type': 'application/json'}
    params = {'msgtype': 'markdown', 'markdown': {'content' : content}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    print('【wecom】',response.json(),flush=True)

def dingding(webhook,content):
    headers = {'Content-Type': 'application/json'}
    params = {"msgtype":"markdown","markdown":{"title":"资源告警","text":content},"at":{"isAtAll":True}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    print('【dingding】',response.json(),flush=True)

def feishu(webhook,title,md):
    headers = {'Content-Type': 'application/json'}
    params = {"msg_type": "interactive",
              "card": {"header": {"title": {"tag": "plain_text","content": title},"template": "red"},
                       "elements": [{"tag": "markdown","content": f"{md}\n<at id=all></at>",}]}}
    data = json.dumps(params)
    response = requests.post(webhook, headers=headers, data=data)
    print('【feishu】',response.json(),flush=True)
