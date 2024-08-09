#!/usr/bin/env python3
from flask import Flask
from units import consul_kv,consul_manager
import uuid,sys
from units.config_log import *

if consul_manager.get_consul_ver() == False:
    sys.exit("请求consul异常, 程序退出.")

skey_path = 'ConsulManager/assets/secret/'
if consul_kv.get_kv_dict(skey_path + 'skey') == {}:
    from datetime import datetime
    now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    skeyuid = ''.join(str(uuid.uuid4()).split('-'))
    consul_kv.put_kv(skey_path + 'skey',{'sk':skeyuid})
    consul_kv.put_kv(f'{skey_path}bak-skey{now}',{'sk':skeyuid})
    logger.warning(f"【初始化SKey完成】")        

from views import login, blackbox, consul, jobs, nodes, selfnode, selfrds, selfredis, avd, exp, jms, edit_cloud, ldap, rds, redis
from views.prom import cloud_metrics
from units.cloud import huaweicloud,alicloud,tencent_cloud,awscloud
from units.avd import avd_list
from units.jms import sync_jms

app = Flask(__name__)
#非nginx调试，解决跨域CORS问题
#CORS(app, supports_credentials=True)

app.register_blueprint(login.blueprint)
app.register_blueprint(blackbox.blueprint)
app.register_blueprint(consul.blueprint)
app.register_blueprint(jobs.blueprint)
app.register_blueprint(nodes.blueprint)
app.register_blueprint(selfnode.blueprint)
app.register_blueprint(selfrds.blueprint)
app.register_blueprint(selfredis.blueprint)
app.register_blueprint(avd.blueprint)
app.register_blueprint(exp.blueprint)
app.register_blueprint(jms.blueprint)
app.register_blueprint(edit_cloud.blueprint)
app.register_blueprint(cloud_metrics.blueprint)
app.register_blueprint(ldap.blueprint)
app.register_blueprint(rds.blueprint)
app.register_blueprint(redis.blueprint)

class Config(object):
    JOBS = []
    SCHEDULER_API_ENABLED = True

ecs_jobs = consul_kv.get_kv_dict('ConsulManager/jobs')
avd_jobs = consul_kv.get_kv_dict('ConsulManager/avd/jobs')
exp_jobs = consul_kv.get_kv_dict('ConsulManager/exp/jobs')
jms_jobs = consul_kv.get_kv_dict('ConsulManager/jms/jobs')
init_jobs = { **ecs_jobs, **avd_jobs, **exp_jobs, **jms_jobs }

if init_jobs is not None:
    for k,v in init_jobs.items():
        logger.info(f"初始化任务：{k}：{v['args']}，{v['minutes']}m")
    Config.JOBS = init_jobs.values()

app.config.from_object(Config())

if __name__ == "__main__":    
    scheduler = jobs.init()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host="0.0.0.0", port=2026)
