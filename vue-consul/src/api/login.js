import request from '@/utils/request-ops'

export function logo() {
  return request({
    url: '/api/login/logo',
    method: 'get'
  })
}

