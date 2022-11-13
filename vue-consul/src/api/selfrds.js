import request from '@/utils/request-ops'

export function getAllList(vendor, account, region, group) {
  return request({
    url: '/api/selfrds/alllist',
    method: 'get',
    params: { vendor, account, region, group }
  })
}

export function getAllInfo() {
  return request({
    url: '/api/selfrds/service',
    method: 'get'
  })
}
export function addService(data) {
  return request({
    url: '/api/selfrds/service',
    method: 'post',
    data
  })
}
export function updateService(del_dict, up_dict) {
  return request({
    url: '/api/selfrds/service',
    method: 'put',
    data: { del_dict, up_dict }
  })
}
export function delService(data) {
  return request({
    url: '/api/selfrds/service',
    method: 'delete',
    data
  })
}
