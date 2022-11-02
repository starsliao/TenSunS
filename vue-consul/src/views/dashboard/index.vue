<template>
  <div class="dashboard-container">
    <el-badge :value="1" class="mark">
      <el-link :underline="false" type="primary" icon="el-icon-star-on" href="https://github.com/starsliao/ConsulManager" target="_blank" class="dashboard-text">StarsL.cn</el-link>
    </el-badge>
    <el-timeline>
      <el-timeline-item timestamp="2022/11/03" placement="top">
        <el-card>
          <h4>v0.9.2</h4>
          <p><el-button type="warning" size="mini" icon="el-icon-star-off" circle />镜像存储更换到华为云，请查看仓库根目录下的<el-link href="https://github.com/starsliao/ConsulManager/blob/main/docker-compose.yml" target="_blank">docker-compose.yml</el-link>，更新您的镜像地址。</p>
          <p><el-button type="success" size="mini" icon="el-icon-star-off" circle />增加RDS云数据库监控接入：支持同步华为云、阿里云、腾讯云的RDS信息到Consul并接入到Prometheus监控！</p>
          <p>更新了阿里云、华为云、腾讯云的SDK。</p>
          <p>优化了菜单展示，资源分类更加直观。</p>
          <p>增加了MySQL的Grafana监控看板。</p>
          <p>增加了从Consul同步RDS到Prometheus的配置生成界面，可生成Prometheus的配置。</p>
          <p>增加了RDS的Prometheus告警规则信息生成页面。</p>
          <p>新增云资源界面可以多选区域和同步的资源类型了。</p>
          <p>新增编辑云资源界面，可以对已添加的账号增删区域、资源类型等操作。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/7/26" placement="top">
        <el-card>
          <h4>v0.8.1</h4>
          <p><el-button type="primary" size="mini" icon="el-icon-star-off" circle />新增自动同步云资产到JumpServer的功能！</p>
          <p>当您在云厂商界面新增、删除、修改ECS后，都会及时的自动同步到JumpServer中。</p>
          <p>并且在JumpServer各资产的备注中会记录ID等资产信息，方便查询筛选登录。</p>
          <p>同步页面提供了云账号ECS资产整体的系统、资源、状态信息。</p>
          <p>优化了站点监控管理页面的用户操作体验，方便增加各类型的站点监控。</p>
          <p>关机的云主机也会同步到consul，并加上tag标识，默认不会接入Prometheus。</p>
          <p>优化后端镜像大小，更新大量前端依赖，修复漏洞。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/7/3" placement="top">
        <el-card>
          <h4>v0.7.0</h4>
          <p><el-button type="warning" size="mini" icon="el-icon-star-off" circle />新增阿里云、华为云、腾讯云账户余额和资源到期前通知！</p>
          <p>可自定义到期前时长与通知余额。</p>
          <p>支持钉钉、企业微信、飞书通知。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/23" placement="top">
        <el-card>
          <h4>v0.6.5</h4>
          <p><el-button type="warning" size="mini" icon="el-icon-star-off" circle /> 云主机同步支持自定义IP端口功能，可在【云主机列表】菜单操作。</p>
          <p>修复了WEB页面批量导入自建主机与站点功能的BUG。</p>
          <p>优化了实例管理、云主机列表页的展示效果和支持搜索。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/19" placement="top">
        <el-card>
          <h4>v0.6.3</h4>
          <p>★支持在Web页面直接批量导入自建主机。</p>
          <p>★支持在Web页面直接批量导入站点监控。</p>
          <p>修复了部分页面前端展示的bug。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/16" placement="top">
        <el-card>
          <h4>v0.6.2</h4>
          <p>已披露的漏洞有状态或类型更新，再次推送时候增加了提示。</p>
          <p>同步阿里云ECS支持同步ECS的标签到Consul的meta中，注意标签的key有中文或符号会忽略，因为meta的key不支持。</p>
          <p>自建主机的新增页面优化了描述和提交处理逻辑。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/13" placement="top">
        <el-card>
          <h4>v0.6.1</h4>
          <p>漏洞通知增加了飞书的支持。</p>
          <p>优化了漏洞通知页面的描述信息。</p>
          <p>修复了一个启动漏洞通知的bug。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/13" placement="top">
        <el-card>
          <h4>v0.6.0</h4>
          <p><el-button type="primary" size="mini" icon="el-icon-star-off" circle /> 新增高危漏洞采集与实时通知功能。</p>
          <p>功能开启即可采集最新30个漏洞列表。</p>
          <p>每小时采集一次，发现新漏洞立即推送到群机器人。</p>
          <p>支持企业微信与钉钉群机器人通知。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/6/3" placement="top">
        <el-card>
          <h4>v0.5.2</h4>
          <p>增加了node-exporter的告警规则。</p>
          <p>修正了一个新增自建主机监控项的bug。</p>
          <p>新增站点监控的描述做了优化。</p>
          <p>登录过期时间修改为8小时。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/5/8" placement="top">
        <el-card>
          <h4>v0.5.1</h4>
          <p><el-button type="warning" size="mini" icon="el-icon-star-off" circle /> Node 主机监控可以方便在页面上管理自建主机了，增加后记得重新生成Prometheus配置，复选上selfnode_exporter。</p>
          <p>优化了导入脚本，并且支持了自建主机的批量导入。</p>
          <p>云主机同步增加了部分国外的区域。</p>
          <p>web页面的描述做了优化，修复了一些bug。</p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/4/7" placement="top">
        <el-card>
          <h4>v0.5.0</h4>
          <p><el-button type="success" size="mini" icon="el-icon-star-off" circle /> 增加ECS云主机监控：支持自动同步阿里、腾讯、华为云的ECS、分组信息到Consul并接入到Prometheus监控！并更新了对应的Grafana看板。</p>
          <p>增加了从Consul同步ECS，站点信息到Prometheus的配置生成界面，可生成Prometheus的配置。</p>
          <p>增加了Blackbox的配置信息与Prometheus告警规则信息生成页面。</p>
          <p>优化了Blackbox接入Prometheus的配置，只需配置1个job即可接入所有类型的站点监控，并更新了对应的Grafana看板。(使用旧版本配置的请参考新文档配置)</p>
          <p><el-button type="primary" size="mini" icon="el-icon-star-off" circle /> 更新了站点监控的grafana看板，增加了URL筛选，查询关联所有图表，并支持展示单job的配置方式。</p>
          <p><el-button type="warning" size="mini" icon="el-icon-star-off" circle /> 更新了主机监控的grafana看板，可匹配自动同步方式采集ECS信息字段的展示， 优化了大量图表，使用新版表格重建，新增健康评分概念，并新增了整体资源消耗信息的一些图表。</p>
          <p>修正了一个修改Consul实例健康检查不能生效的bug。</p>
          <p>优化了多个展示信息的说明，与帮助文档的描述，以及增加了鸣谢信息。</p>
          <p>更新了登录界面。</p>
          <p><el-button type="primary" plain size="small" icon="el-icon-s-promotion" circle /> <el-link type="primary" href="https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md" target="_blank">应用场景1：如何优雅的基于Consul自动同步ECS主机监控</el-link></p>
          <p><el-button type="primary" plain size="small" icon="el-icon-s-promotion" circle /> <el-link type="primary" href="https://github.com/starsliao/ConsulManager/blob/main/docs/blackbox%E7%AB%99%E7%82%B9%E7%9B%91%E6%8E%A7.md" target="_blank">应用场景2：如何优雅的使用Consul管理Blackbox站点监控</el-link></p>
        </el-card>
      </el-timeline-item>
      <el-timeline-item timestamp="2022/2/23" placement="top">
        <el-card>
          <h4>v0.3.1</h4>
          <p>允许在实例ID字段使用'/'，(可以在Consul管理中对blackbox-exporter的监控实例做自定义编辑了，例如：增加标签，增加Meta)。</p>
          <p>优化了描述和引导使用Blackbox站点监控。</p>
          <p>增加了Makefile文件，可以使用make update来更新等操作。</p>
        </el-card>
      </el-timeline-item>
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
