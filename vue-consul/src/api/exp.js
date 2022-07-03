import request from '@/utils/request-ops'

export function getExpList(query_dict) {
  return request({
    url: '/api/exp/list',
    method: 'get',
    params: { query_dict }
  })
}
export function getExpConfig() {
  return request({
    url: '/api/exp/config',
    method: 'get'
  })
}

export function postExpJob(exp_config_dict) {
  return request({
    url: '/api/exp/config',
    method: 'post',
    data: { exp_config_dict }
  })
}

export function postExpIsnotify(isnotify_dict) {
  return request({
    url: '/api/exp/isnotify',
    method: 'post',
    data: { isnotify_dict }
  })
}
