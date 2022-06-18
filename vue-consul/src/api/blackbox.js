import request from '@/utils/request-ops'

export function getAllList(module, company, project, env) {
  return request({
    url: '/api/blackbox/alllist',
    method: 'get',
    params: { module, company, project, env }
  })
}

export function getAllInfo() {
  return request({
    url: '/api/blackbox/service',
    method: 'get'
  })
}
export function addService(data) {
  return request({
    url: '/api/blackbox/service',
    method: 'post',
    data
  })
}
export function updateService(del_dict, up_dict) {
  return request({
    url: '/api/blackbox/service',
    method: 'put',
    data: { del_dict, up_dict }
  })
}
export function delService(data) {
  return request({
    url: '/api/blackbox/service',
    method: 'delete',
    data
  })
}
export function getRules() {
  return request({
    url: '/api/blackboxcfg/rules',
    method: 'get'
  })
}
export function getPconfig() {
  return request({
    url: '/api/blackboxcfg/pconfig',
    method: 'get'
  })
}
export function getBconfig() {
  return request({
    url: '/api/blackboxcfg/bconfig',
    method: 'get'
  })
}

export function upload_web(data) {
  return request({
    url: '/api/blackboxcfg/upload_web',
    method: 'get',
    data
  })
}
