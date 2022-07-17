import request from '@/utils/request-ops'

export function getExpList(query_dict) {
  return request({
    url: '/api/exp/list',
    method: 'get',
    params: { query_dict }
  })
}
export function getJmsConfig() {
  return request({
    url: '/api/jms/config',
    method: 'get'
  })
}

export function postJmsConfig(jms_config) {
  return request({
    url: '/api/jms/config',
    method: 'post',
    data: { jms_config }
  })
}

export function postExpIsnotify(isnotify_dict) {
  return request({
    url: '/api/exp/isnotify',
    method: 'post',
    data: { isnotify_dict }
  })
}
