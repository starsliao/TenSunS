<template>
  <div class="app-container">
    <el-select v-model="services" multiple placeholder="请选择需要生成配置的服务" filterable collapse-tags clearable style="width: 350px" class="filter-item">
      <el-option v-for="item in services_list" :key="item" :label="item" :value="item" />
    </el-select>
    &nbsp;&nbsp;<font color="#ff0000">*</font>MySQLd_Exporter IP端口
    <el-input v-model="exporter" placeholder="x.x.x.x:9104" clearable style="width: 200px;" class="filter-item" />&nbsp;&nbsp;
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
import { getRdsServicesList, getRdsConfig } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      services: [],
      ostype: [],
      services_list: [],
      services_dict: {},
      exporter: '',
      configs: ''
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
        this.listLoading = false
      })
    },
    fetchRdsConfig() {
      this.listLoading = true
      this.services_dict.services_list = this.services
      this.services_dict.exporter = this.exporter
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
