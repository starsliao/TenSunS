import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobRedis() {
  return request({
    url: '/api/redis/jobredis',
    method: 'get'
  })
}

export function getRedisServicesList() {
  return request({
    url: '/api/redis/redis_services',
    method: 'get'
  })
}

export function getRedisConfig(services_dict) {
  return request({
    url: '/api/redis/redispconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getRedisRules() {
  return request({
    url: '/api/redis/redisrules',
    method: 'get'
  })
}

export function postCstRedis(cst_redis_dict) {
  return request({
    url: '/api/redis/cstredis',
    method: 'post',
    data: { cst_redis_dict }
  })
}

export function getCstRedisConfig(iid) {
  return request({
    url: '/api/redis/cstredisconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstRedisList(jobredis_name, checked) {
  return request({
    url: '/api/redis/cstredislist',
    method: 'get',
    params: { jobredis_name, checked }
  })
}
