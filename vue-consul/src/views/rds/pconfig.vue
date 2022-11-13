<template>
  <div class="app-container">
    <el-select v-model="services" multiple placeholder="选择需要自动发现的MySQL组" filterable collapse-tags clearable style="width: 260px" class="filter-item">
      <el-option v-for="item in services_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-input v-model="exporter" placeholder="Mysqld_Exporter IP端口" clearable style="width: 200px;" class="filter-item" />&nbsp;&nbsp;
    <el-select v-model="jobrds" multiple placeholder="选择需要采集指标的MySQL组" filterable collapse-tags clearable style="width: 260px" class="filter-item">
      <el-option v-for="item in jobrds_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-input v-model="cm_exporter" placeholder="ConsulManager IP端口" clearable style="width: 190px;" class="filter-item" />&nbsp;&nbsp;
    <el-button class="filter-item" type="primary" icon="el-icon-magic-stick" @click="fetchRdsConfig">
      生成配置
    </el-button>
    <el-button v-clipboard:copy="configs" v-clipboard:success="onCopy" v-clipboard:error="onError" class="filter-item" type="warning" icon="el-icon-document-copy">
      复制配置
    </el-button>
    <pre v-highlightjs="configs" style="line-height:120%"><code class="yaml yamlcode" /></pre>
  </div>
</template>

<script>
import { getRdsServicesList, getRdsConfig, getJobRds } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      services: [],
      jobrds: [],
      ostype: [],
      services_list: [],
      services_dict: {},
      jobrds_list: [],
      exporter: '',
      cm_exporter: '',
      configs: '该功能用于生成Prometheus的两个JOB配置，生成后请复制到Prometheus配置中：\n\n1. 选择需要同步的账号，Prometheus即可自动发现该账号下的所有DRS实例。\n\n2. 由于Mysqld_Exporter无法监控到云数据库的CPU、内存、磁盘的使用情况，所以ConsulManager开发了Exporter功能，可以直接从云厂商获取到这些指标并接入Prometheus！\n   选择需要采集指标的RDS账号区域，即可生成Prometheus的JOB配置。'
    }
  },
  created() {
    this.fetchRdsList()
  },
  methods: {
    onCopy() {
      this.$message({
        message: '复制成功！',
        type: 'success'
      })
    },
    onError() {
      this.$message.error('复制失败！')
    },
    fetchRdsList() {
      this.listLoading = true
      getRdsServicesList().then(response => {
        this.services_list = response.services_list
        this.services_list.push('selfrds_exporter')
      })
      getJobRds().then(response => {
        this.jobrds_list = response.jobrds
      })
      this.listLoading = false
    },
    fetchRdsConfig() {
      this.listLoading = true
      this.services_dict.services_list = this.services
      this.services_dict.exporter = this.exporter
      this.services_dict.jobrds_list = this.jobrds
      this.services_dict.cm_exporter = this.cm_exporter
      getRdsConfig(this.services_dict).then(response => {
        this.configs = response.configs
        this.listLoading = false
      })
    }
  }
}
</script>
<style>
  .yamlcode {
    font-family:'Consolas';
  }
  pre {
    max-height: 640px;
    white-space: pre-wrap;
    overflow:auto;
  }
</style>
