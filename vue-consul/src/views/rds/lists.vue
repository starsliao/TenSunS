<template>
  <div class="app-container">
    <el-select v-model="jobecs_name" placeholder="请选择需要查询的云MySQL列表" filterable collapse-tags clearable style="width: 350px" class="filter-item" @change="fetchEcs(jobecs_name)">
      <el-option v-for="item in jobecs_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-checkbox v-model="checked" style="margin-left: 10px;" label="仅显示修改过的" border @change="cstEcsList(jobecs_name,checked)" />
    <el-tooltip class="item" effect="light" content="刷新当前ECS列表" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchEcs(jobecs_name)" />
    </el-tooltip>
    <div style="float: right;margin-left: 10px;">
      <el-input v-model="iname" prefix-icon="el-icon-search" placeholder="请输入名称、实例或实例ID进行筛选" clearable style="width: 300px" class="filter-item" />
    </div>
    <el-dialog title="自定义实例信息" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :model="cst_ecs" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="自定义端口">
          <el-switch v-model="cst_ecs.portswitch" />
        </el-form-item>
        <el-form-item v-if="cst_ecs.portswitch" required label="端口：">
          <el-input v-model="cst_ecs.port" />
        </el-form-item>
        <el-form-item label="自定义IP">
          <el-switch v-model="cst_ecs.ipswitch" />
        </el-form-item>
        <el-form-item v-if="cst_ecs.ipswitch" required label="IP：">
          <el-input v-model="cst_ecs.ip" />
        </el-form-item>
        <font size="3px" color="#ff0000">如需恢复同步该实例的IP端口信息，请关闭开启的自定义选项后，再同步一次所属数据源。</font>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="createData">
          确认
        </el-button>
      </div>
    </el-dialog>

    <el-table
      v-loading="listLoading"
      :data="ecs_list.filter(data => !iname || (data.name.toLowerCase().includes(iname.toLowerCase()) || data.instance.toLowerCase().includes(iname.toLowerCase()) || data.iid.toLowerCase().includes(iname.toLowerCase())))"
      :default-sort="{ prop: 'exp', order: 'ascending' }"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" align="center" />
      <el-table-column prop="group" label="分组" sortable align="center" width="150" show-overflow-tooltip />
      <el-table-column prop="name" label="名称" sortable align="center" width="220" show-overflow-tooltip />
      <el-table-column prop="instance" label="实例" sortable align="center" width="180" />
      <el-table-column prop="os" label="系统" sortable align="center" width="100" />
      <el-table-column prop="cpu" label="CPU" sortable align="center" width="80" />
      <el-table-column prop="mem" label="内存" sortable align="center" width="80" />
      <el-table-column prop="exp" label="到期日" sortable align="center" width="120" />
      <el-table-column prop="iid" label="实例ID" sortable align="center" />
      <el-table-column label="操作" align="center" width="120" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row.iid)">
            自定义实例
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getEcsList, getJobEcs, postCstEcs, getCstEcsConfig, getCstEcsList } from '@/api/node-exporter'
export default {
  data() {
    return {
      listLoading: false,
      dialogFormVisible: false,
      checked: false,
      jobecs_name: '',
      iname: '',
      jobecs_list: [],
      ecs_list: [],
      cst_ecs: { iid: '', portswitch: false, ipswitch: false, port: '', ip: '' }
    }
  },
  created() {
    getJobEcs().then(response => {
      this.jobecs_list = response.jobecs
      if (this.$route.query.job_id) {
        this.fetchEcs(this.$route.query.job_id)
      } else {
        this.jobecs_name = this.jobecs_list[0]
        this.fetchEcs(this.jobecs_name)
      }
    })
  },
  mounted() {
    if (this.$route.query.job_id) {
      this.jobecs_name = this.$route.query.job_id
    }
  },
  methods: {
    cstEcsList(jobecs_name, checked) {
      this.listLoading = true
      getCstEcsList(jobecs_name, checked).then(response => {
        this.ecs_list = response.ecs_list
        this.listLoading = false
      })
    },
    handleUpdate(iid) {
      this.listLoading = true
      this.dialogFormVisible = true
      getCstEcsConfig(iid).then(response => {
        this.cst_ecs = response.cst_ecs
        this.listLoading = false
        this.dialogFormVisible = true
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.dialogFormVisible = false
          this.listLoading = true
          postCstEcs(this.cst_ecs).then(response => {
            this.fetchEcs(this.jobecs_name)
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    fetchJobEcs() {
      getJobEcs().then(response => {
        this.jobecs_list = response.jobecs
      })
    },
    fetchEcs(job_id) {
      this.checked = false
      this.listLoading = true
      getEcsList(job_id).then(response => {
        this.ecs_list = response.ecs_list
        this.listLoading = false
      })
    }
  }
}
</script>
