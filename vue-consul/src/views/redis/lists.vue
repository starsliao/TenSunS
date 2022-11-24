<template>
  <div class="app-container">
    <el-select v-model="jobredis_name" placeholder="请选择需要查询的云MySQL列表" filterable collapse-tags clearable style="width: 350px" class="filter-item" @change="fetchRedis(jobredis_name)">
      <el-option v-for="item in jobredis_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-checkbox v-model="checked" style="margin-left: 10px;" label="仅显示修改过的" border @change="cstRedisList(jobredis_name,checked)" />
    <el-tooltip class="item" effect="light" content="刷新当前REDIS列表" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchEcs(jobredis_name)" />
    </el-tooltip>
    <div style="float: right;margin-left: 10px;">
      <el-input v-model="iname" prefix-icon="el-icon-search" placeholder="请输入名称、实例或实例ID进行筛选" clearable style="width: 300px" class="filter-item" />
    </div>
    <el-dialog title="自定义实例信息" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :model="cst_redis" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="自定义端口">
          <el-switch v-model="cst_redis.portswitch" />
        </el-form-item>
        <el-form-item v-if="cst_redis.portswitch" required label="端口：">
          <el-input v-model="cst_redis.port" />
        </el-form-item>
        <el-form-item label="自定义IP">
          <el-switch v-model="cst_redis.ipswitch" />
        </el-form-item>
        <el-form-item v-if="cst_redis.ipswitch" required label="IP：">
          <el-input v-model="cst_redis.ip" />
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
      :data="redis_list.filter(data => !iname || (data.name.toLowerCase().includes(iname.toLowerCase()) || data.instance.toLowerCase().includes(iname.toLowerCase()) || data.iid.toLowerCase().includes(iname.toLowerCase())))"
      :default-sort="{ prop: 'exp', order: 'ascending' }"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" align="center" />
      <el-table-column prop="group" label="分组" sortable align="center" width="150" show-overflow-tooltip />
      <el-table-column prop="name" label="名称" sortable align="center" width="180" show-overflow-tooltip />
      <el-table-column prop="instance" label="实例" sortable align="center">
        <template slot-scope="{row}">
          <span style="font-weight:bold">{{ row.instance }} </span>
          <el-tooltip style="diaplay:inline" effect="dark" placement="top">
            <div slot="content"> IP：{{ row.ip }}</div>
            <i class="el-icon-info" />
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="ver" label="版本" sortable align="center" width="80" />
      <el-table-column prop="mem" label="内存" sortable align="center" width="90" />
      <el-table-column prop="exp" label="到期日" sortable align="center" width="95" />
      <el-table-column prop="itype" label="类型" sortable align="center" width="120" show-overflow-tooltip />
      <el-table-column prop="iid" label="实例ID" sortable align="center" width="150" show-overflow-tooltip />
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
import { getResList, getJobRedis, postCstRedis, getCstRedisConfig, getCstRedisList } from '@/api/redis'
export default {
  data() {
    return {
      listLoading: false,
      dialogFormVisible: false,
      checked: false,
      jobredis_name: '',
      iname: '',
      jobredis_list: [],
      redis_list: [],
      cst_redis: { iid: '', portswitch: false, ipswitch: false, port: '', ip: '' }
    }
  },
  created() {
    getJobRedis().then(response => {
      this.jobredis_list = response.jobredis
      if (this.$route.query.job_id) {
        this.fetchRedis(this.$route.query.job_id)
      } else {
        this.jobredis_name = this.jobredis_list[0]
        this.fetchRedis(this.jobredis_name)
      }
    })
  },
  mounted() {
    if (this.$route.query.job_id) {
      this.jobredis_name = this.$route.query.job_id
    }
  },
  methods: {
    cstRedisList(jobredis_name, checked) {
      this.listLoading = true
      getCstRedisList(jobredis_name, checked).then(response => {
        this.redis_list = response.res_list
        this.listLoading = false
      })
    },
    handleUpdate(iid) {
      this.listLoading = true
      this.dialogFormVisible = true
      getCstRedisConfig(iid).then(response => {
        this.cst_redis = response.cst_redis
        this.listLoading = false
        this.dialogFormVisible = true
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.dialogFormVisible = false
          this.listLoading = true
          postCstRedis(this.cst_redis).then(response => {
            this.fetchRedis(this.jobredis_name)
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    fetchJobRedis() {
      getJobRedis().then(response => {
        this.jobredis_list = response.jobredis
      })
    },
    fetchRedis(job_id) {
      this.checked = false
      this.listLoading = true
      getResList(job_id).then(response => {
        this.redis_list = response.res_list
        this.listLoading = false
      })
    }
  }
}
</script>
