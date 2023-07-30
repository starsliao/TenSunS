import request from '@/utils/request-ops'

export function logo() {
  return request({
    url: '/api/login/logo',
    method: 'get'
  })
}

export function postnologo(height) {
  return request({
    url: '/api/login/nologo',
    method: 'post',
    data: { height }
  })
}

export function rebig() {
  return request({
    url: '/api/login/rebig',
    method: 'post'
  })
}

export function resmall() {
  return request({
    url: '/api/login/resmall',
    method: 'post'
  })
}
export function rebgimg() {
  return request({
    url: '/api/login/rebgimg',
    method: 'post'
  })
}
export function retitle() {
  return request({
    url: '/api/login/retitle',
    method: 'post'
  })
}

export function getbgimg() {
  return request({
    url: '/api/login/bgimg',
    method: 'get'
  })
}

export function getitle() {
  return request({
    url: '/api/login/title',
    method: 'get'
  })
}

export function postitle(title) {
  return request({
    url: '/api/login/title',
    method: 'post',
    data: { title }
  })
}
