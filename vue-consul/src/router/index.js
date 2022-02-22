import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: 'Dashboard', icon: 'dashboard' }
    }]
  },

  {
    path: '/consul',
    component: Layout,
    redirect: '/consul/services',
    name: 'Consul 管理',
    meta: { title: 'Consul 管理', icon: 'example' },
    children: [
      {
        path: 'hosts',
        name: 'Hosts',
        component: () => import('@/views/consul/hosts'),
        meta: { title: 'Hosts', icon: 'el-icon-school' }
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('@/views/consul/services'),
        meta: { title: 'Services', icon: 'el-icon-news' }
      },
      {
        path: 'instances',
        name: 'Instances',
        component: () => import('@/views/consul/instances'),
        meta: { title: 'Instances', icon: 'el-icon-connection' }
      }
    ]
  },
  {
    path: '/blackbox',
    component: Layout,
    children: [{
      path: 'index',
      name: 'Blackbox 站点监控',
      component: () => import('@/views/blackbox/index'),
      meta: { title: 'Blackbox 站点监控', icon: 'tree' }
    }]
  },
  {
    path: '友情链接',
    component: Layout,
    meta: { title: '友情链接', icon: 'link' },
    children: [
      {
        path: 'https://starsl.cn',
        meta: { title: 'StarsL.cn', icon: 'el-icon-s-custom' }
      },
      {
        path: 'https://github.com/starsliao?tab=repositories',
        meta: { title: '我的Github', icon: 'el-icon-star-off' }
      },
      {
        path: 'https://grafana.com/orgs/starsliao/dashboards',
        meta: { title: '我的Grafana', icon: 'el-icon-odometer' }
      },
      {
        path: 'https://starsl.cn/static/img/qr.png',
        meta: { title: '我的公众号', icon: 'el-icon-chat-dot-round' }
      },
      {
        path: 'https://element.eleme.cn',
        meta: { title: 'Element', icon: 'el-icon-eleme' }
      }

    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
