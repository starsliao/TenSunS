import request from '@/utils/request-ops'

export function setldap(data) {
  return request({
    url: '/api/ldap/config',
    method: 'post',
    data: data
  })
}
