<template>
  <div class="app-container">
    <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="handleCreate">配置漏洞通知</el-button>
    <el-button class="filter-item" type="warning" icon="el-icon-magic-stick" @click="handleRun">测试一次</el-button>
    <el-dialog title="配置漏洞通知" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :model="avd_config" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="漏洞采集">
          <el-switch v-model="avd_config.switch" /><br>
          <font size="3px" color="#ff0000">
            <li>开启采集：每小时会自动采集一次漏洞信息。</li>
            <li>开启通知：当发现新漏洞时，会立刻推送到群机器人。</li>
          </font>
        </el-form-item>
        <el-form-item v-if="avd_config.switch" label="钉钉通知">
          <el-switch v-model="avd_config.dingding" />
        </el-form-item>
        <el-form-item v-if="avd_config.switch && avd_config.dingding" required label="机器人Webhook地址">
          <el-input v-model="avd_config.dingdingwh" type="textarea" autosize /><font size="3px" color="#ff0000">机器人安全设置的自定义关键词请设置为：<strong>漏洞告警</strong></font>
        </el-form-item>
        <el-form-item v-if="avd_config.switch" label="企业微信通知">
          <el-switch v-model="avd_config.wecom" />
        </el-form-item>
        <el-form-item v-if="avd_config.switch && avd_config.wecom" required label="机器人Webhook地址">
          <el-input v-model="avd_config.wecomwh" type="textarea" autosize />
        </el-form-item>
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
    <el-table v-loading="listLoading" :data="avd_list" :default-sort="{ prop: 'avd_time', order: 'descending' }" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" align="center" />
      <el-table-column prop="avd_id" label="AVD编号" sortable align="center" width="150" />
      <el-table-column prop="avd_name" label="漏洞名称" sortable align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <el-link type="primary" style="font-weight:bold" :href="row.avd_id_url" target="_blank"><i class="el-icon-view el-icon--left" />{{ row.avd_name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="avd_type" label="漏洞类型" sortable align="center" width="220" show-overflow-tooltip />
      <el-table-column prop="avd_stat" label="漏洞状态" sortable align="center" width="160" />
      <el-table-column prop="avd_time" label="披露时间" sortable align="center" width="120" />
    </el-table>
  </div>

</template>

<script>
import { getAvdList, getAvdConfig, postAvdJob, postAvdRun } from '@/api/avd'
export default {
  data() {
    return {
      listLoading: false,
      dialogFormVisible: false,
      avd_config: { switch: false, wecom: false, dingding: false, wecomwh: '', dingdingwh: '' },
      avd_list: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    handleCreate() {
      this.listLoading = true
      getAvdConfig().then(response => {
        if (Object.keys(response.avd_config).length !== 0) {
          this.avd_config = response.avd_config
        }
        this.listLoading = false
        this.dialogFormVisible = true
      })
    },
    fetchData() {
      this.listLoading = true
      getAvdList().then(response => {
        this.avd_list = response.avd_list
        this.listLoading = false
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.dialogFormVisible = false
          this.listLoading = true
          postAvdJob(this.avd_config).then(response => {
            this.fetchData()
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    handleRun() {
      this.$confirm('此操作将立刻执行一次漏洞通知，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        postAvdRun().then(response => {
          this.fetchData()
          this.$message({
            message: response.data,
            type: 'success'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '操作已取消。'
        })
      })
    }
  }
}
</script>
