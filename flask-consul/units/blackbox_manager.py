import requests,json,consul_kv
from config import consul_token,consul_url

headers = {'X-Consul-Token': consul_token}
init_module_list = ['http_2xx','http_4xx','tcp_connect','icmp','http200igssl','httpNoRedirect4ssl','http_5xx','http_post_2xx','ssh_banner']
def get_all_list(module,company,project,env):
    module = f'and Meta.module=="{module}"' if module != '' else f'and Meta.module != ""'
    company = f'and Meta.company=="{company}"' if company != '' else f'and Meta.company != ""'
    project = f'and Meta.project=="{project}"' if project != '' else f'and Meta.project != ""'
    env = f'and Meta.env=="{env}"' if env != '' else f'and Meta.env != ""'
    url = f'{consul_url}/agent/services?filter=Service == blackbox_exporter {module} {company} {project} {env}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        module_list = consul_kv.get_value('ConsulManager/record/blackbox/module_list')['module_list']
        company_list = sorted(list(set([i['company'] for i in all_list])))
        project_list = sorted(list(set([i['project'] for i in all_list])))
        env_list = sorted(list(set([i['env'] for i in all_list])))

        init_m_list = [x for x in init_module_list if x not in module_list]
        module_list = module_list + ['---'] + init_m_list

        return {'code': 20000,'all_list':all_list,'module_list':module_list,
                'company_list':company_list,'project_list':project_list,'env_list':env_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def get_service():
    response = requests.get(f'{consul_url}/agent/services?filter=Service == blackbox_exporter', headers=headers)
    if response.status_code == 200:
        info = response.json()
        all_list = [i['Meta'] for i in info.values()]
        module_list = sorted(list(set([i['module'] for i in all_list])))
        company_list = sorted(list(set([i['company'] for i in all_list])))
        project_list = sorted(list(set([i['project'] for i in all_list])))
        env_list = sorted(list(set([i['env'] for i in all_list])))
        consul_kv.put_kv('ConsulManager/record/blackbox/module_list',{'module_list':module_list})
        init_m_list = [x for x in init_module_list if x not in module_list]
        module_list = module_list + ['------'] + init_m_list

        return {'code': 20000,'all_list':all_list,'module_list':module_list,
                'company_list':company_list,'project_list':project_list,'env_list':env_list}
    else:
        return {'code': 50000, 'data': f'{response.status_code}:{response.text}'}

def add_service(module,company,project,env,name,instance):
    sid = f"{module}/{company}/{project}/{env}@{name}"
    if '//' in sid or sid.startswith('/') or sid.endswith('/'):
        return {"code": 50000, "data": f"服务ID【{sid}】首尾不能包含'/'，并且不能包含两个连续的'/'"}
    data = {
            "id": sid,
            "name": 'blackbox_exporter',
            "tags": [module],
            "Meta": {'module':module,'company':company,'project':project,'env':env,'name':name,'instance':instance}
           }
    reg = requests.put(f'{consul_url}/agent/service/register', headers=headers, data=json.dumps(data))
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】增加成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

def del_service(module,company,project,env,name):
    sid = f"{module}/{company}/{project}/{env}@{name}"
    reg = requests.put(f'{consul_url}/agent/service/deregister/{sid}', headers=headers)
    if reg.status_code == 200:
        return {"code": 20000, "data": f"【{sid}】删除成功！"}
    else:
        return {"code": 50000, "data": f"{reg.status_code}【{sid}】{reg.text}"}

def get_rules():
    rules = """
- name: Domain
  rules:
  - alert: 站点可用性
    expr: probe_success == 0
    for: 1m
    labels:
      alertype: domain
      severity: critical
    annotations:
      description: "{{ $labels.env }}_{{ $labels.name }}({{ $labels.project }})：站点无法访问\\n> {{ $labels.instance }}"

  - alert: 站点1h可用性低于80%
    expr: sum_over_time(probe_success[1h])/count_over_time(probe_success[1h]) * 100 < 80
    for: 3m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{ $labels.env }}_{{ $labels.name }}({{ $labels.project }})：站点1h可用性：{{ $value | humanize }}%\\n> {{ $labels.instance }}"

  - alert: 站点状态异常
    expr: (probe_success == 0 and probe_http_status_code > 499) or probe_http_status_code == 0
    for: 1m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{ $labels.env }}_{{ $labels.name }}({{ $labels.project }})：站点状态异常：{{ $value }}\\n> {{ $labels.instance }}"

  - alert: 站点耗时过高
    expr: probe_duration_seconds > 0.5
    for: 2m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{ $labels.env }}_{{ $labels.name }}({{ $labels.project }})：当前站点耗时：{{ $value | humanize }}s\\n> {{ $labels.instance }}"

  - alert: SSL证书有效期
    expr: (probe_ssl_earliest_cert_expiry-time()) / 3600 / 24 < 15
    for: 2m
    labels:
      alertype: domain
      severity: warning
    annotations:
      description: "{{ $labels.env }}_{{ $labels.name }}({{ $labels.project }})：证书有效期剩余{{ $value | humanize }}天\\n> {{ $labels.instance }}"
"""
    return {"code": 20000, "rules": rules}

def get_bconfig():
    bconfig = """
modules:
  http_2xx:
    prober: http
    http:
      valid_status_codes: [200,204]
      no_follow_redirects: false
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  # 用于需要检查SSL证书有效性，但是该域名访问后又会重定向到其它域名的情况，这样检查的证书有效期就是重定向后域名的。
  # 如果需要检查源域名信息，需要在blackbox中增加禁止重定向参数。
  httpNoRedirect4ssl:
    prober: http
    http:
      valid_status_codes: [200,204,301,302,303]
      no_follow_redirects: true
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  # 用于忽略SSL证书检查的站点监控。
  http200igssl:
    prober: http
    http:
      valid_status_codes:
      - 200
      tls_config:
        insecure_skip_verify: true

  http_4xx:
    prober: http
    http:
      valid_status_codes: [401,403,404]
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  http_5xx:
    prober: http
    http:
      valid_status_codes: [500,502]
      preferred_ip_protocol: ip4
      ip_protocol_fallback: false

  http_post_2xx:
    prober: http
    http:
      method: POST

  icmp:
    prober: icmp

  tcp_connect:
    prober: tcp

  ssh_banner:
    prober: tcp
    tcp:
      query_response:
      - expect: "^SSH-2.0-"
      - send: "SSH-2.0-blackbox-ssh-check"
"""
    return {"code": 20000, "bconfig": bconfig}

def get_pconfig():
    consul_server = consul_url.split("/")[2]
    pconfig = f"""
  - job_name: 'blackbox_exporter'
    metrics_path: /probe
    consul_sd_configs:
      - server: '{consul_server}'
        token: '{consul_token}'
        services: ['blackbox_exporter']
    relabel_configs:
      - source_labels: ["__meta_consul_service_metadata_instance"]
        target_label: __param_target
      - source_labels: [__meta_consul_service_metadata_module]
        target_label: __param_module
      - source_labels: [__meta_consul_service_metadata_module]
        target_label: module
      - source_labels: ["__meta_consul_service_metadata_company"]
        target_label: company
      - source_labels: ["__meta_consul_service_metadata_env"]
        target_label: env
      - source_labels: ["__meta_consul_service_metadata_name"]
        target_label: name
      - source_labels: ["__meta_consul_service_metadata_project"]
        target_label: project
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115
"""
    return {"code": 20000, "pconfig": pconfig}
