<template>
  <div>
    <br>
    <el-row :gutter="20">
      <el-col :span="12" :offset="6">
        <el-card shadow="always" style="text-align: center">
          Grafana 看板详情：
          <el-link href="https://grafana.com/grafana/dashboards/9965" target="_blank" type="primary">https://grafana.com/grafana/dashboards/9965</el-link><br><br>
          Grafana 看板ID：<strong>9965</strong>
        </el-card>
      </el-col>
    </el-row>
    <br>
    <div class="block">
      <el-image style="width: 100%; height: 100%" src="/blackbox.png" />
    </div>
  </div>
</template>
