import request from '@/utils/request-ops'

export function getAvdList() {
  return request({
    url: '/api/avd/list',
    method: 'get'
  })
}
export function getAvdConfig() {
  return request({
    url: '/api/avd/config',
    method: 'get'
  })
}

export function postAvdJob(avd_config_dict) {
  return request({
    url: '/api/avd/config',
    method: 'post',
    data: { avd_config_dict }
  })
}

export function postAvdRun() {
  return request({
    url: '/api/avd/run',
    method: 'post'
  })
}
