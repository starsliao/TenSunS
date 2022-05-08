from config import consul_token,consul_url
def ecs_config(services_list,ostype_list):
    consul_server = consul_url.split("/")[2]
    job_dict = {'linux':'node_exporter','windows':'windows_exporter'}
    configs = ''
    for ostype in ostype_list:
        job_name = job_dict[ostype]
        config_str = f"""
  - job_name: {job_name}
    scrape_interval: 15s
    scrape_timeout: 5s
    consul_sd_configs:
      - server: '{consul_server}'
        token: '{consul_token}'
        refresh_interval: 30s
        services: {services_list}
        tags: ['{ostype}']
    relabel_configs:
      - source_labels: ['__meta_consul_service']
        target_label: cservice
      - source_labels: ['__meta_consul_service_metadata_vendor']
        target_label: vendor
      - source_labels: ['__meta_consul_service_metadata_region']
        target_label: region
      - source_labels: ['__meta_consul_service_metadata_group']
        target_label: group
      - source_labels: ['__meta_consul_service_metadata_account']
        target_label: account
      - source_labels: ['__meta_consul_service_metadata_name']
        target_label: name
      - source_labels: ['__meta_consul_service_metadata_iid']
        target_label: iid
      - source_labels: ['__meta_consul_service_metadata_exp']
        target_label: exp
      - source_labels: ['__meta_consul_service_metadata_instance']
        target_label: instance
      - source_labels: [instance]
        target_label: __address__
"""
        configs = configs + config_str
    return {'code': 20000,'configs': configs }
