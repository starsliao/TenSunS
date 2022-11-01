<template>
  <div>
    <br>
    <el-row :gutter="20">
      <el-col :span="12" :offset="6">
        <el-card shadow="always" style="text-align: center">
          Grafana 看板详情：
          <el-link href="https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E7%9A%84%E4%BD%BF%E7%94%A8%E4%B8%80%E4%B8%AAmysqld_exporter%E7%9B%91%E6%8E%A7%E6%89%80%E6%9C%89%E7%9A%84MySQL%E5%AE%9E%E4%BE%8B.md" target="_blank" type="primary">如何优雅的使用一个mysqld_exporter监控所有的MySQL实例</el-link><br><br>
        </el-card>
      </el-col>
    </el-row>
    <br>
    <div class="block">
      <el-image style="width: 100%; height: 100%" src="/mysql1.png" />
      <el-image style="width: 100%; height: 100%" src="/mysql2.png" />
    </div>
  </div>
</template>
