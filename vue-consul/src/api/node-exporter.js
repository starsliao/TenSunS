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

export function getEcsList(job_id) {
  return request({
    url: '/api/nodes/ecs',
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
