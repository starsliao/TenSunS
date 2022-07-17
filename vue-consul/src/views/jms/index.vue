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
    <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="handleCreate">接入JumpServer</el-button>
    <el-tooltip class="item" effect="light" content="根据菜单选择查询对应账户余额，菜单为空时，查询所有账户。" placement="top">
      <el-button class="filter-item" type="warning" icon="el-icon-data-line" @click="handleamount">查看余额</el-button>
    </el-tooltip>
    <el-dialog title="接入JumpServer" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :model="jms_config" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="JumpServer URL">
          <el-input v-model="jms_config.url" placeholder="http开头" style="width: 390px;" />
        </el-form-item>
        <el-form-item label="JumpServer Token">
          <el-input v-model="jms_config.token" placeholder="请输入Admin Token" style="width: 390px;" show-password />
        </el-form-item>
        <el-form-item label="全局管理用户信息：" />
        <div class="demo-input-suffix">
          <h3>Linux：</h3>
          ssh端口：<el-input v-model="jms_config.linuxport" style="width: 72px;" />
          &nbsp;&nbsp;管理用户ID：<el-input v-model="jms_config.linuxuid" style="width: 300px;" />
        </div>
        <div class="demo-input-suffix">
          <h3>Windows：</h3>
          rdp端口：<el-input v-model="jms_config.winport" style="width: 72px;" />
          &nbsp;&nbsp;管理用户ID：<el-input v-model="jms_config.winuid" style="width: 300px;" />
        </div>
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
import { getExpList, getJmsConfig, postJmsConfig, postExpIsnotify } from '@/api/jms'
export default {
  data() {
    return {
      jms_config: { url: '', token: '', linuxport: '22', linuxuid: '', winport: '3389', winuid: '' },
      listLoading: false,
      dialogFormVisible: false,
      query: { vendor: '', account: '' },
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
      getJmsConfig().then(response => {
        if (Object.keys(response.jms_config).length !== 0) {
          this.jms_config = response.jms_config
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
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.dialogFormVisible = false
          this.listLoading = true
          postJmsConfig(this.jms_config).then(response => {
            this.listLoading = false
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    handleamount() {
      this.amountFormVisible = true
    }
  }
}
</script>
