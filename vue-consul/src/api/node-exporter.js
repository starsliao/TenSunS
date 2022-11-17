import request from '@/utils/request-ops'

export function getAllJobs(query_dict) {
  return request({
    url: '/api/jobs',
    method: 'get',
    params: { query_dict }
  })
}

export function PostJob(job_dict) {
  return request({
    url: '/api/jobs',
    method: 'post',
    data: { job_dict }
  })
}

export function DelJob(job_id) {
  return request({
    url: '/api/jobs',
    method: 'delete',
    params: { job_id }
  })
}

export function getGroup(job_id) {
  return request({
    url: '/api/nodes/group',
    method: 'get',
    params: { job_id }
  })
}

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobEcs() {
  return request({
    url: '/api/nodes/jobecs',
    method: 'get'
  })
}
export function getServicesList() {
  return request({
    url: '/api/nodes/ecs_services',
    method: 'get'
  })
}
export function getConfig(services_dict) {
  return request({
    url: '/api/nodes/config',
    method: 'post',
    data: { services_dict }
  })
}
export function getRules() {
  return request({
    url: '/api/nodes/rules',
    method: 'get'
  })
}

export function postCstEcs(cst_ecs_dict) {
  return request({
    url: '/api/nodes/cstecs',
    method: 'post',
    data: { cst_ecs_dict }
  })
}

export function getCstEcsConfig(iid) {
  return request({
    url: '/api/nodes/cstecsconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstEcsList(jobecs_name, checked) {
  return request({
    url: '/api/nodes/cstecslist',
    method: 'get',
    params: { jobecs_name, checked }
  })
}
