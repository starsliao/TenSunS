import sys,requests,hashlib,json
from datetime import datetime
from bs4 import BeautifulSoup

def get_avd():
    avd_url = 'https://avd.aliyun.com'
    res = requests.get(avd_url) # + '/high-risk/list')
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    bugs = soup.select('tr')
    for index, avd_info in enumerate(bugs[1:]):
        avd = avd_info.select('td')
        avd_dict = {}
        avd_dict['avd_id'] = avd[0].getText(strip=True)
        avd_dict['avd_id_url'] = avd_url + avd[0].a.attrs['href']
        avd_dict['avd_name'] = avd[1].getText(strip=True)
        avd_dict['avd_type'] = avd[2].button.attrs.get('title',avd[2].getText(strip=True))
        avd_dict['avd_time'] = avd[3].getText(strip=True)
        avd_dict['avd_stat'] = avd[4].select('button')[1].attrs['title']
    print(avd_dict)

get_avd()
