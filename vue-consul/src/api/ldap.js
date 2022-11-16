import request from '@/utils/request-ops'

export function setldap(data) {
  return request({
    url: '/api/ldap/config',
    method: 'post',
    data: data
  })
}
export function getLdap() {
  return request({
    url: '/api/ldap/config',
    method: 'get'
  })
}
export function delLdap() {
  return request({
    url: '/api/ldap/config',
    method: 'delete'
  })
}
