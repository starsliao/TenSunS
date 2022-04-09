from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from config import vendors,regions
from units import token_auth,consul_kv
import json
blueprint = Blueprint('jobs',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('job_dict',type=dict)
parser.add_argument('query_dict',type=str)

def init():
    global Scheduler
    Scheduler = APScheduler()
    return Scheduler
    
class Jobs(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self):
        args = parser.parse_args()
        query_dict = json.loads(args['query_dict'])
        if query_dict['vendor'] != '':
            query_dict['vendor'] = {v : k for k, v in vendors.items()}[query_dict['vendor']]
        query_set = set({k:v for k,v in query_dict.items() if v != ''}.items())
        job_list = list(consul_kv.get_kv_dict(f'ConsulManager/jobs').values())
        job_run_dict = {job.id:job.next_run_time.strftime("%m%d/%H:%M") for job in Scheduler.get_jobs()}
        job_count_dict = consul_kv.get_kv_dict('ConsulManager/record/jobs')
        jobs = []
        for i in job_list:
            vendor,account,itype = i['id'].split('/')[0:3]
            job_info_dict = {'vendor':vendor,'account':account,'itype':itype}
            if query_set.issubset(job_info_dict.items()):
                pass
            else:
                continue
            region = i['args'][-1] if len(i['args']) == 2 else 'none'
            interval = i['minutes']
            if f'ConsulManager/record/jobs/{i["id"]}' in job_count_dict:
                count = job_count_dict[f'ConsulManager/record/jobs/{i["id"]}']['count']
                runtime = job_count_dict[f'ConsulManager/record/jobs/{i["id"]}']['update']
                on = job_count_dict[f'ConsulManager/record/jobs/{i["id"]}'].get('on',0)
                off = job_count_dict[f'ConsulManager/record/jobs/{i["id"]}'].get('off',0)
            else:
                count = '无'
                runtime = '无'
                on,off = 0,0
            jobs.append({'region':regions[vendor][region],'vendor':vendors[vendor],'account':account,'itype':itype,
                         'interval':interval,'jobid':i['id'],'nextime':job_run_dict[i['id']],'on':on,'off':off,
                         'count':count, 'runtime':runtime})
        vendor_list = sorted(list(set([i['vendor'] for i in jobs])))
        account_list = sorted(list(set([i['account'] for i in jobs])))
        itype_list = sorted(list(set([i['itype'] for i in jobs])))
        return {'code': 20000,'all_jobs':jobs,'vendor_list':vendor_list,'account_list':account_list,'itype_list':itype_list}

    def post(self):
        args = parser.parse_args()
        job_dict = args['job_dict']
        job_status = job_dict['dialogStatus']
        if job_status == 'create':
            ak = job_dict['ak']
            sk = job_dict['sk']
            consul_kv.put_aksk(job_dict['vendor'],job_dict['account'],ak,sk)

            proj_job_id = f"{job_dict['vendor']}/{job_dict['account']}/group"
            proj_job_func = f"__main__:{job_dict['vendor']}.group"
            proj_job_args = [job_dict['account']]
            proj_job_interval = int(job_dict['proj_interval'])

            ecs_job_id = f"{job_dict['vendor']}/{job_dict['account']}/ecs/{job_dict['region']}"
            ecs_job_func = f"__main__:{job_dict['vendor']}.ecs"
            ecs_job_args = [job_dict['account'],job_dict['region']]
            ecs_job_interval = int(job_dict['ecs_interval'])

            Scheduler.add_job(id=proj_job_id, func=proj_job_func, args=proj_job_args, trigger='interval', 
                              minutes=proj_job_interval, replace_existing=True)
            Scheduler.add_job(id=ecs_job_id, func=ecs_job_func, args=ecs_job_args, trigger='interval',
                              minutes=ecs_job_interval, replace_existing=True)

            proj_job_dict = {'id':proj_job_id,'func':proj_job_func,'args':proj_job_args,'minutes':proj_job_interval,
                             "trigger": "interval","replace_existing": True}
            Scheduler.run_job(proj_job_id)
            ecs_job_dict = {'id':ecs_job_id,'func':ecs_job_func,'args':ecs_job_args,'minutes':ecs_job_interval,
                             "trigger": "interval","replace_existing": True}
            record_dict = consul_kv.get_value(f"ConsulManager/record/jobs/{proj_job_id}")
            if record_dict['status'] == 20000:
                consul_kv.put_kv(f'ConsulManager/jobs/{proj_job_id}',proj_job_dict)
                consul_kv.put_kv(f'ConsulManager/jobs/{ecs_job_id}',ecs_job_dict)
            else:
                Scheduler.remove_job(proj_job_id)
                Scheduler.remove_job(ecs_job_id)
            return {'code': record_dict['status'], 'data': f"{record_dict['update']}：{record_dict['msg']}"}
        elif job_status == 'update':
            jobid = job_dict['jobid']
            interval = int(job_dict['interval'])
            Scheduler.modify_job(jobid,trigger='interval',minutes=interval)
            upjob_dict = consul_kv.get_value(f'ConsulManager/jobs/{jobid}')
            upjob_dict['minutes'] = interval
            consul_kv.put_kv(f'ConsulManager/jobs/{jobid}',upjob_dict)
            return {'code': 20000, 'data': '更新成功！'}
        elif job_status == 'run':
            Scheduler.run_job(job_dict['jobid'])
            record_dict = consul_kv.get_value(f"ConsulManager/record/jobs/{job_dict['jobid']}")
            return {'code': record_dict['status'], 'data': f"{record_dict['update']}：{record_dict['msg']}"}

    def delete(self):
        args = parser.parse_args()
        job_id = args['job_id']
        Scheduler.remove_job(job_id)
        del_job = consul_kv.del_key(f'ConsulManager/jobs/{job_id}')
        return {'code': 20000, 'data': '删除成功！'}

api.add_resource(Jobs, '/api/jobs')
