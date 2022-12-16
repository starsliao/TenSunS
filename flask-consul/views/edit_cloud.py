from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
from config import vendors,regions
from units import token_auth,consul_kv
from .jobs import deljob,addjob,runjob,modjob_interval,modjob_args
import json
from units.config_log import *
blueprint = Blueprint('edit_cloud',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('vendor',type=str)
parser.add_argument('account',type=str)
parser.add_argument('region',type=str)
parser.add_argument('editJob',type=dict)
class Edit(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self,stype):
        job_list = list(consul_kv.get_kv_dict(f'ConsulManager/jobs').values())
        if stype == 'cloud':
            cloud_dict = {}
            for i in job_list:
                vendor,account = i['id'].split('/')[0:2]
                if vendor in cloud_dict:
                    if account not in cloud_dict[vendor]:
                        cloud_dict[vendor].append(account)
                else:
                    cloud_dict[vendor] = [account]
            return {'code': 20000,'cloud_dict': cloud_dict}
        if stype == 'find':
            args = parser.parse_args()
            vendor = args['vendor']
            account = args['account']
            region = args['region']
            restype = ['group']
            interval = {'proj_interval': 60, 'ecs_interval': 10, 'rds_interval': 20, 'redis_interval': 20}
            isextip = False
            for i in job_list:
                if f'{vendor}/{account}/group' == i['id']:
                    interval['proj_interval'] = i['minutes']
                elif f'{vendor}/{account}/ecs/{region}' == i['id']:
                    restype.append('ecs')
                    interval['ecs_interval'] = i['minutes']
                    isextip = i["args"][-1] if len(i["args"]) == 3 else False
                elif f'{vendor}/{account}/rds/{region}' == i['id']:
                    restype.append('rds')
                    interval['rds_interval'] = i['minutes']
                elif f'{vendor}/{account}/redis/{region}' == i['id']:
                    restype.append('redis')
                    interval['redis_interval'] = i['minutes']
            return {'code': 20000, 'restype': restype, 'interval': interval, 'isextip': isextip}
    def post(self,stype):
        job_list = list(consul_kv.get_kv_dict(f'ConsulManager/jobs').values())
        if stype == 'commit':
            args = parser.parse_args()
            editjob_dict = args['editJob']
            vendor = editjob_dict['vendor']
            account = editjob_dict['account']
            region = editjob_dict['region']
            restype = editjob_dict['restype']
            isextip = editjob_dict['isextip']
            proj_interval = int(editjob_dict['proj_interval'])
            ecs_interval = int(editjob_dict['ecs_interval'])
            rds_interval = int(editjob_dict['rds_interval'])
            redis_interval = int(editjob_dict['redis_interval'])
            logger.info(f'{editjob_dict}')
            if editjob_dict['akskswitch']:
                ak = editjob_dict['ak']
                sk = editjob_dict['sk']
                consul_kv.put_aksk(editjob_dict['vendor'],editjob_dict['account'],ak,sk)

            jobgroup = [x for x in job_list if x['id'] == f'{vendor}/{account}/group'][0]
            if proj_interval != jobgroup['minutes']:
                jobgroup['minutes'] = proj_interval
                jobid = f'{vendor}/{account}/group'
                consul_kv.put_kv(f'ConsulManager/jobs/{jobid}',jobgroup)
                modjob_interval(jobid,proj_interval)

            ecs_jobid = f'{vendor}/{account}/ecs/{region}'
            rds_jobid = f'{vendor}/{account}/rds/{region}'
            redis_jobid = f'{vendor}/{account}/redis/{region}'
            if 'ecs' in restype:
                isecs = [x for x in job_list if x['id'] == f'{vendor}/{account}/ecs/{region}']
                if len(isecs) == 1:
                    if ecs_interval != isecs[0]['minutes']:
                        isecs[0]['minutes'] = ecs_interval
                        consul_kv.put_kv(f'ConsulManager/jobs/{ecs_jobid}',isecs[0])
                        modjob_interval(ecs_jobid,ecs_interval)

                    if len(isecs[0]['args']) != 3 or isextip != isecs[0]['args'][2]:
                        try:
                            isecs[0]['args'][2] = isextip
                        except:
                            isecs[0]['args'].append(isextip)
                        consul_kv.put_kv(f'ConsulManager/jobs/{ecs_jobid}',isecs[0])
                        modjob_args(ecs_jobid,isecs[0]['args'])
                else:
                    job_func = f"__main__:{vendor}.ecs"
                    job_args = [account,region,isextip]
                    job_interval = ecs_interval
                    addjob(ecs_jobid, job_func, job_args, job_interval)      
                    job_dict = {'id':ecs_jobid,'func':job_func,'args':job_args,'minutes':job_interval,
                                "trigger": "interval","replace_existing": True}
                    consul_kv.put_kv(f'ConsulManager/jobs/{ecs_jobid}',job_dict)
            else:
                try:
                    consul_kv.del_key(f'ConsulManager/jobs/{ecs_jobid}')
                    deljob(ecs_jobid)
                except:
                    pass        

            if 'rds' in restype:
                isrds = [x for x in job_list if x['id'] == f'{vendor}/{account}/rds/{region}']
                if len(isrds) == 1:
                    if rds_interval != isrds[0]['minutes']:
                        isrds[0]['minutes'] = rds_interval
                        consul_kv.put_kv(f'ConsulManager/jobs/{rds_jobid}',isrds[0])
                        modjob_interval(rds_jobid,rds_interval)
                else:
                    job_func = f"__main__:{vendor}.rds"
                    job_args = [account,region]
                    job_interval = rds_interval
                    addjob(rds_jobid, job_func, job_args, job_interval)
                    job_dict = {'id':rds_jobid,'func':job_func,'args':job_args,'minutes':job_interval,
                                "trigger": "interval","replace_existing": True}
                    consul_kv.put_kv(f'ConsulManager/jobs/{rds_jobid}',job_dict)
            else:
                try:
                    consul_kv.del_key(f'ConsulManager/jobs/{rds_jobid}')
                    deljob(rds_jobid)
                except:
                    pass

            if 'redis' in restype:
                isredis = [x for x in job_list if x['id'] == f'{vendor}/{account}/redis/{region}']
                if len(isredis) == 1:
                    if redis_interval != isredis[0]['minutes']:
                        isredis[0]['minutes'] = redis_interval
                        consul_kv.put_kv(f'ConsulManager/jobs/{redis_jobid}',isredis[0])
                        modjob_interval(redis_jobid,redis_interval)
                else:
                    job_func = f"__main__:{vendor}.redis"
                    job_args = [account,region]
                    job_interval = redis_interval
                    addjob(redis_jobid, job_func, job_args, job_interval)
                    job_dict = {'id':redis_jobid,'func':job_func,'args':job_args,'minutes':job_interval,
                                "trigger": "interval","replace_existing": True}
                    consul_kv.put_kv(f'ConsulManager/jobs/{redis_jobid}',job_dict)
            else:
                try:
                    consul_kv.del_key(f'ConsulManager/jobs/{redis_jobid}')
                    deljob(redis_jobid)
                except:
                    pass

            return {'code': 20000, 'data': f'{vendor}/{account}/{region}：编辑成功！'}
api.add_resource(Edit, '/api/edit/<stype>')
