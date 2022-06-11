<template>
  <div class="app-container">
    <el-select v-model="jobecs_name" placeholder="请选择需要查询的ECS列表" filterable collapse-tags clearable style="width: 350px" class="filter-item" @change="fetchEcs(jobecs_name)">
      <el-option v-for="item in jobecs_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-tooltip class="item" effect="light" content="刷新当前ECS列表" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchEcs(jobecs_name)" />
    </el-tooltip>

    <el-table v-loading="listLoading" :data="ecs_list" :default-sort="{ prop: 'exp', order: 'ascending' }" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" align="center" />
      <el-table-column prop="group" label="分组" sortable align="center" width="180" show-overflow-tooltip />
      <el-table-column prop="name" label="名称" sortable align="center" width="280" />
      <el-table-column prop="instance" label="实例" sortable align="center" width="180" />
      <el-table-column prop="os" label="系统" sortable align="center" width="100" />
      <el-table-column prop="cpu" label="CPU" sortable align="center" width="80" />
      <el-table-column prop="mem" label="内存" sortable align="center" width="80" />
      <el-table-column prop="exp" label="到期日" sortable align="center" width="120" />
      <el-table-column prop="iid" label="实例ID" sortable align="center" />
    </el-table>
  </div>
</template>

<script>
import { getEcsList, getJobEcs } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      jobecs_name: '',
      jobecs_list: [],
      ecs_list: []
    }
  },
  created() {
    this.fetchJobEcs()
    if (this.$route.query.job_id) {
      this.fetchEcs(this.$route.query.job_id)
    }
  },
  mounted() {
    if (this.$route.query.job_id) {
      this.jobecs_name = this.$route.query.job_id
    }
  },
  methods: {
    fetchJobEcs() {
      getJobEcs().then(response => {
        this.jobecs_list = response.jobecs
      })
    },
    fetchEcs(job_id) {
      this.listLoading = true
      getEcsList(job_id).then(response => {
        this.ecs_list = response.ecs_list
        this.listLoading = false
      })
    }
  }
}
</script>
