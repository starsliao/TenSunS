<template>
  <div class="app-container">
    <el-button v-clipboard:copy="bconfig" v-clipboard:success="onCopy" v-clipboard:error="onError" class="filter-item" type="warning" icon="el-icon-document-copy">
      复制配置
    </el-button>
    <pre v-highlightjs="bconfig" style="line-height:120%"><code class="yaml yamlcode" /></pre>
  </div>
</template>

<script>
import { getBconfig } from '@/api/blackbox'
export default {
  data() {
    return {
      listLoading: false,
      bconfig: ''
    }
  },
  created() {
    this.fetchBconfig()
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
    fetchBconfig() {
      this.listLoading = true
      getBconfig().then(response => {
        this.bconfig = response.bconfig
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
