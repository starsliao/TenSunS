import request from '@/utils/request-ops'

export function getHosts() {
  return request({
    url: '/api/consul/hosts',
    method: 'get'
  })
}

export function getServices() {
  return request({
    url: '/api/consul/services',
    method: 'get'
  })
}

export function getServicesName() {
  return request({
    url: '/api/consul/services_name',
    method: 'get'
  })
}

export function getInstances(service_name) {
  return request({
    url: '/api/consul/instances',
    method: 'get',
    params: { service_name }
  })
}

export function delSid(sid) {
  return request({
    url: '/api/consul/sid',
    method: 'delete',
    params: { sid }
  })
}

export function addSid(instance_dict) {
  return request({
    url: '/api/consul/sid',
    method: 'post',
    data: { instance_dict }
  })
}

export function updateSid(sid, instance_dict) {
  return request({
    url: '/api/consul/sid',
    method: 'put',
    data: { sid, instance_dict }
  })
}
