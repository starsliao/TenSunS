<template>
  <div class="app-container">
    <el-button v-clipboard:copy="pconfig" v-clipboard:success="onCopy" v-clipboard:error="onError" class="filter-item" type="warning" icon="el-icon-document-copy">
      复制配置
    </el-button>
    <pre v-highlightjs="pconfig" style="line-height:120%"><code class="yaml yamlcode" /></pre>
  </div>
</template>

<script>
import { getPconfig } from '@/api/blackbox'
export default {
  data() {
    return {
      listLoading: false,
      pconfig: ''
    }
  },
  created() {
    this.fetchPconfig()
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
    fetchPconfig() {
      this.listLoading = true
      getPconfig().then(response => {
        this.pconfig = response.pconfig
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
