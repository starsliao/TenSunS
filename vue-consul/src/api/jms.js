import request from '@/utils/request-ops'

export function getJmsList(query_dict) {
  return request({
    url: '/api/jms/list',
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

export function postJmsSwitch(switch_dict) {
  return request({
    url: '/api/jms/switch',
    method: 'post',
    data: { switch_dict }
  })
}

export function postJmsSync(jms_sync) {
  return request({
    url: '/api/jms/sync',
    method: 'post',
    timeout: 600 * 1000,
    data: { jms_sync }
  })
}
