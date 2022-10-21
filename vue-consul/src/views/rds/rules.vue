<template>
  <div class="app-container">
    <el-button v-clipboard:copy="rules" v-clipboard:success="onCopy" v-clipboard:error="onError" class="filter-item" type="warning" icon="el-icon-document-copy">
      复制配置
    </el-button>
    <pre v-highlightjs="rules" style="line-height:120%"><code class="yaml yamlcode" /></pre>
  </div>
</template>

<script>
import { getRules } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      rules: ''
    }
  },
  created() {
    this.fetchRules()
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
    fetchRules() {
      this.listLoading = true
      getRules().then(response => {
        this.rules = response.rules
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
