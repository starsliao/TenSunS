<template>
  <div class="app-container">
    <el-select v-model="jobrds_name" placeholder="请选择需要查询的云MySQL列表" filterable collapse-tags clearable style="width: 350px" class="filter-item" @change="fetchRds(jobrds_name)">
      <el-option v-for="item in jobrds_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-tooltip class="item" effect="light" content="刷新当前RDS列表" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchRds(jobrds_name)" />
    </el-tooltip>
    <div style="float: right;margin-left: 10px;">
      <el-input v-model="iname" prefix-icon="el-icon-search" placeholder="请输入名称、实例或实例ID进行筛选" clearable style="width: 300px" class="filter-item" />
    </div>

    <el-table
      v-loading="listLoading"
      :data="rds_list.filter(data => !iname || (data.name.toLowerCase().includes(iname.toLowerCase()) || data.instance.toLowerCase().includes(iname.toLowerCase()) || data.iid.toLowerCase().includes(iname.toLowerCase())))"
      :default-sort="{ prop: 'exp', order: 'ascending' }"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" align="center" />
      <el-table-column prop="group" label="分组" sortable align="center" width="150" show-overflow-tooltip />
      <el-table-column prop="name" label="名称" sortable align="center" width="220" show-overflow-tooltip />
      <el-table-column prop="instance" label="实例" sortable align="center" width="180">
        <template slot-scope="{row}">
          <span style="font-weight:bold">{{ row.instance }} </span>
          <el-tooltip style="diaplay:inline" effect="dark" placement="top">
            <div slot="content"> 域名：{{ row.domain }}</div>
            <i class="el-icon-info" />
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="ver" label="版本" sortable align="center" width="80" />
      <el-table-column prop="cpu" label="CPU" sortable align="center" width="80" />
      <el-table-column prop="mem" label="内存" sortable align="center" width="80" />
      <el-table-column prop="disk" label="磁盘" sortable align="center" width="80" />
      <el-table-column prop="exp" label="到期日" sortable align="center" width="120" />
      <el-table-column prop="iid" label="实例ID" sortable align="center" />
    </el-table>
  </div>
</template>

<script>
import { getResList, getJobRds } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      dialogFormVisible: false,
      checked: false,
      jobrds_name: '',
      iname: '',
      jobrds_list: [],
      rds_list: []
    }
  },
  created() {
    getJobRds().then(response => {
      this.jobrds_list = response.jobrds
      if (this.$route.query.job_id) {
        this.fetchRds(this.$route.query.job_id)
      } else {
        this.jobrds_name = this.jobrds_list[0]
        this.fetchRds(this.jobrds_name)
      }
    })
  },
  mounted() {
    if (this.$route.query.job_id) {
      this.jobrds_name = this.$route.query.job_id
    }
  },
  methods: {
    fetchJobRds() {
      getJobRds().then(response => {
        this.jobrds_list = response.jobrds
      })
    },
    fetchRds(job_id) {
      this.checked = false
      this.listLoading = true
      getResList(job_id).then(response => {
        this.rds_list = response.res_list
        this.listLoading = false
      })
    }
  }
}
</script>
