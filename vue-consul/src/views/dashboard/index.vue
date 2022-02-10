<template>
  <div class="dashboard-container">
    <el-badge :value="1" class="mark">
      <el-link :underline="false" type="primary" icon="el-icon-star-on" href="https://github.com/starsliao/ConsulManager" target="_blank" class="dashboard-text">StarsL.cn</el-link>
    </el-badge>
    <el-timeline>
      <el-timeline-item timestamp="2022/2/10" placement="top">
        <el-card>
          <h4>v0.3.0</h4>
          <p>更名Consul Manager</p>
          <p>增加Consul Web管理功能</p>
          <p>增加Consul服务器的状态查看</p>
          <p>支持Consul Services的增删改查</p>
          <p>支持批量删除Service功能</p>
          <p>优化了对Tags、Meta、健康检查的配置管理</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/1/29" placement="top">
        <el-card>
          <h4>v0.2.0</h4>
          <p>后端使用Flask Blueprint重构，版本号v0.2.0</p>
          <p>前端规范URI路径，匹配后端，版本号v0.1.3</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/1/27" placement="top">
        <el-card>
          <h4>v0.1.2</h4>
          <p>所有字段增加了排序功能</p>
          <p>新增筛选功能：可以根据名称或实例来进行关键字筛选</p>
          <p>新增清空查询条件按钮</p>
          <p>简化了web界面新增操作： </p>
          <p>  选择选项查询后，点击新增或自动填写好选择的选项</p>
          <p>  增加确认并新增按钮，可以自动填上之前填写的前4个字段</p>
          <p>新增批量删除功能</p>
          <p>新增分页功能</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/1/7" placement="top">
        <el-card>
          <h4>v0.1.0</h4>
          <p>基于Prometheus + Blackbox_Exporter实现站点与接口监控。</p>
          <p>基于Consul实现Prometheus监控目标的自动发现。</p>
          <p>Blackbox Manager：基于Flask + Vue实现的Web管理平台维护监控目标。</p>
          <p>实现了一个脚本可批量导入监控目标到Consul。</p>
          <p>更新了一个Blackbox Exporter的Grafana展示看板。</p>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Dashboard',
  computed: {
    ...mapGetters([
      'name'
    ])
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    margin: 30px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
</style>
