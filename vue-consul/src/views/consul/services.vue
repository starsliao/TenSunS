<template>
  <div class="app-container">
    <el-alert title="如需管理【自建主机、blackbox_exporter】的监控实例，建议使用左侧菜单【自建主机管理、Blackbox 站点监控】来维护，更加方便直观。" type="success" center close-text="朕知道了" />
    <el-table
      v-loading="listLoading"
      :data="services"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="ID" width="50px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.$index+1 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="Name" label="服务组" sortable align="center">
        <template slot-scope="{row}">
          <el-link type="primary" style="font-weight:bold" @click="handleInstances(row.Name)"><i class="el-icon-view el-icon--left" />{{ row.Name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="Nodes" label="节点" align="center" width="120">
        <template slot-scope="{row}">
          <el-tag v-for="atag in row.Nodes" :key="atag" type="info" size="mini">{{ atag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="Datacenter" label="数据中心" align="center" width="110">
        <template slot-scope="{row}">
          <span>{{ row.Datacenter }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="Tags" label="Tags" sortable align="center">
        <template slot-scope="{row}">
          <el-tag v-for="atag in row.Tags" :key="atag" size="small">{{ atag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="InstanceCount" label="实例数" sortable align="center" width="100">
        <template slot-scope="{row}">
          <span style="font-weight:bold">{{ row.InstanceCount }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="ChecksPassing" label="健康实例" sortable align="center" width="120">
        <template slot-scope="{row}">
          <el-tooltip effect="dark" content="健康检查成功的实例数" placement="top">
            <el-button size="mini" type="success" icon="el-icon-check" circle>{{ row.ChecksPassing - 1 }}</el-button>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="ChecksCritical" label="实例状态" sortable align="center" width="120">
        <template slot-scope="{row}">
          <el-tooltip v-if="row.ChecksCritical != 0" effect="dark" content="健康检查失败的实例数" placement="top">
            <el-button size="mini" type="danger" icon="el-icon-close" circle>{{ row.ChecksCritical }}</el-button>
          </el-tooltip>
          <el-tooltip v-else-if="row.ChecksPassing == 1" effect="dark" content="所有实例都没有配置健康检查" placement="top">
            <el-button size="mini" type="info" icon="el-icon-minus" circle />
          </el-tooltip>
          <el-tooltip v-else effect="dark" content="已配置的健康检查都通过" placement="top">
            <el-button size="mini" type="success" icon="el-icon-check" circle />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

  </div>
</template>

<script>
import { getServices } from '@/api/consul'
export default {
  data() {
    return {
      services: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getServices().then(response => {
        this.services = response.services
        this.listLoading = false
      })
    },
    handleInstances(sname) {
      this.$router.push({
        path: '/consul/instances',
        query: { service_name: sname }
      })
    }
  }
}
</script>
