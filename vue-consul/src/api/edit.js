import request from '@/utils/request-ops'

export function getCloud() {
  return request({
    url: '/api/edit/cloud',
    method: 'get'
  })
}
export function findGroup(vendor, account, region) {
  return request({
    url: '/api/edit/find',
    method: 'get',
    params: { vendor, account, region }
  })
}
export function PostEditJob(editJob) {
  return request({
    url: '/api/edit/commit',
    method: 'post',
    data: { editJob }
  })
}
