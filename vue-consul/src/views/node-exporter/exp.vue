<template>
  <div class="app-container">
    <el-alert title="菜单只显示有到期资源的账户，余额可查询所有账户；单个资源的通知可独立关闭。【自动续费、到期转按需、到期不续费的资源不会采集】【腾讯云仅采集主机到期列表(未找到整体到期接口)】" type="error" close-text="朕知道了" />
    <el-select v-model="query.vendor" placeholder="云厂商" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in vendor_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select v-model="query.account" placeholder="账户" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in account_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-tooltip class="item" effect="light" content="查询所有" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="success" icon="el-icon-magic-stick" circle @click="resetData" />
    </el-tooltip>
    <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="handleCreate">配置余额与到期通知</el-button>
    <el-tooltip class="item" effect="light" content="根据菜单选择查询对应账户余额，菜单为空时，查询所有账户。" placement="top">
      <el-button class="filter-item" type="warning" icon="el-icon-data-line" @click="handleamount">查看余额</el-button>
    </el-tooltip>
    <el-dialog title="配置余额与到期通知" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :model="exp_config" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="采集开关">
          <el-switch v-model="exp_config.switch" /><br>
          <font size="3px" color="#ff0000">
            <li>开启采集：每小时会自动采集一次余额与到期资源信息。</li>
            <li>开启通知：当余额或到期资源低于设定时，会立刻推送通知。</li>
          </font>
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="自动采集">
          <el-input v-model="exp_config.collect_days" style="width: 220px;" type="number">
            <template slot="append">天内到期的资源</template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="自动通知">
          <el-input v-model="exp_config.notify_days" style="width: 220px;" type="number">
            <template slot="append">天内到期的资源</template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="余额低于">
          <el-input v-model="exp_config.notify_amount" style="width: 220px;" type="number">
            <template slot="append">元自动通知</template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="钉钉通知">
          <el-switch v-model="exp_config.dingding" />
        </el-form-item>
        <el-form-item v-if="exp_config.switch && exp_config.dingding" required label="机器人Webhook地址">
          <el-input v-model="exp_config.dingdingwh" type="textarea" autosize /><font size="3px" color="#ff0000">机器人安全设置的自定义关键词请设置为：<strong>资源告警</strong></font>
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="企业微信通知">
          <el-switch v-model="exp_config.wecom" />
        </el-form-item>
        <el-form-item v-if="exp_config.switch && exp_config.wecom" required label="机器人Webhook地址">
          <el-input v-model="exp_config.wecomwh" type="textarea" autosize />
        </el-form-item>
        <el-form-item v-if="exp_config.switch" label="飞书通知">
          <el-switch v-model="exp_config.feishu" />
        </el-form-item>
        <el-form-item v-if="exp_config.switch && exp_config.feishu" required label="机器人Webhook地址">
          <el-input v-model="exp_config.feishuwh" type="textarea" autosize /><font size="3px" color="#ff0000">机器人安全设置的自定义关键词请设置为：<strong>资源告警</strong></font>
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
    <el-table v-loading="listLoading" :data="exp_list" :default-sort="{ prop: 'EndTime', order: 'ascending' }" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" align="center" />
      <el-table-column prop="vendor" label="云厂商" sortable align="center" width="90" />
      <el-table-column prop="account" label="账号" sortable align="center" width="100" />
      <el-table-column prop="Region" label="区域" sortable align="center" width="100" show-overflow-tooltip />
      <el-table-column prop="Ptype" label="类型" sortable align="center" width="150" show-overflow-tooltip />
      <el-table-column prop="Product" label="产品" sortable align="center" width="200" show-overflow-tooltip />
      <el-table-column prop="Name" label="名称" sortable align="center" show-overflow-tooltip />
      <el-table-column prop="id" label="实例ID" sortable align="center" show-overflow-tooltip />
      <el-table-column prop="EndTime" label="到期日" sortable align="center" width="100" />
      <el-table-column label="通知" align="center" width="60" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-switch v-model="row.isnotify" active-color="#13ce66" @change="fetchNotify(row.vendor, row.account, row.notify_id, row.isnotify)" />
        </template>
      </el-table-column>
    </el-table>
    <el-dialog title="查询余额" :visible.sync="amountFormVisible" width="60%">
      <el-table v-loading="listLoading" :data="amount_list" height="540" :default-sort="{ prop: 'amount', order: 'ascending' }" border fit highlight-current-row style="width: 100%;">
        <el-table-column prop="vendor" label="云厂商" sortable align="center" />
        <el-table-column prop="account" label="账户" sortable align="center" />
        <el-table-column prop="amount" label="余额(元)" sortable align="center" />
      </el-table>
    </el-dialog>
  </div>

</template>

<script>
import { getExpList, getExpConfig, postExpJob, postExpIsnotify } from '@/api/exp'
export default {
  data() {
    return {
      listLoading: false,
      dialogFormVisible: false,
      query: { vendor: '', account: '' },
      exp_config: { switch: false, collect_days: 15, notify_days: 7, notify_amount: 1000, wecom: false, dingding: false, feishu: false, wecomwh: '', dingdingwh: '', feishuwh: '' },
      exp_list: [],
      vendor_list: [],
      account_list: [],
      amount_list: [],
      isnotify_dict: {},
      amountFormVisible: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchNotify(vendor, account, notify_id, isnotify) {
      this.isnotify_dict = { vendor: vendor, account: account, notify_id: notify_id, isnotify: isnotify }
      postExpIsnotify(this.isnotify_dict).then(response => {
        this.$message({
          message: response.data,
          type: response.type
        })
      })
    },
    handleCreate() {
      this.listLoading = true
      getExpConfig().then(response => {
        if (Object.keys(response.exp_config).length !== 0) {
          this.exp_config = response.exp_config
        }
        this.listLoading = false
        this.dialogFormVisible = true
      })
    },
    resetData() {
      this.query = { vendor: '', account: '' }
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getExpList(this.query).then(response => {
        this.vendor_list = response.vendor_list
        this.account_list = response.account_list
        this.exp_list = response.exp_list
        this.amount_list = response.amount_list
        this.listLoading = false
      })
    },
    createData() {
      this.$confirm('此操作将开启定时任务，并执行首次所有账号的余额与到期资源信息采集，根据设定进行通知，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$refs['dataForm'].validate((valid) => {
          if (valid) {
            this.dialogFormVisible = false
            this.listLoading = true
            this.exp_config.collect_days = this.exp_config.collect_days * 1
            this.exp_config.notify_days = this.exp_config.notify_days * 1
            this.exp_config.notify_amount = this.exp_config.notify_amount * 1
            postExpJob(this.exp_config).then(response => {
              this.fetchData()
              this.$message({
                message: response.data,
                type: 'success'
              })
            })
          }
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '操作已取消'
        })
      })
    },
    handleamount() {
      this.amountFormVisible = true
    }
  }
}
</script>
