<template>
  <div class="app-container">
    <el-alert type="success" center close-text="朕知道了">
      <el-link icon="el-icon-warning" type="success" href="https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E6%8A%8A%E4%B8%BB%E6%9C%BA%E8%87%AA%E5%8A%A8%E5%90%8C%E6%AD%A5%E5%88%B0JumpServer.md" target="_blank">应用场景：如何优雅的把主机信息自动同步到JumpServer</el-link>
    </el-alert>
    <el-select v-model="query.vendor" placeholder="云厂商" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in vendor_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select v-model="query.account" placeholder="账户" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in account_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-tooltip effect="light" content="查询所有" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="success" icon="el-icon-magic-stick" circle @click="resetData" />
    </el-tooltip>
    <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="handleCreate">接入JumpServer</el-button>
    <el-dialog :visible.sync="dialogFormVisible" width="44%">
      <div slot="title" class="header-title">
        <span style="font-size:16px;font-weight:bold;">接入JumpServer</span>&nbsp;&nbsp;
        <el-link type="primary" href="https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E6%8A%8A%E4%B8%BB%E6%9C%BA%E8%87%AA%E5%8A%A8%E5%90%8C%E6%AD%A5%E5%88%B0JumpServer.md" target="_blank" icon="el-icon-question">如何填写</el-link>
      </div>
      <el-form ref="dataForm" :model="jms_config" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="JumpServer URL">
          <el-input v-model="jms_config.url" placeholder="http开头" style="width: 390px;" />
        </el-form-item>
        <el-form-item label="JumpServer 版本">
          <el-select v-model="jms_config.ver" placeholder="版本" style="width: 100px" class="filter-item">
            <el-option key="V2" label="V2" value="V2" />
            <el-option key="V3" label="V3" value="V3" />
          </el-select>
          <span v-if="jms_config.ver === 'V3'"><font size="3px" color="#ff0000">请更新JumpServer到3.5及以上版本</font></span>
        </el-form-item>
        <el-form-item label="JumpServer Token">
          <el-input v-model="jms_config.token" type="password" placeholder="请输入Admin Token" style="width: 390px;" />
        </el-form-item>
        <hr style="FILTER: alpha(opacity=100,finishopacity=0,style=2)" align=left width="96%" SIZE=1>
        <h3>全局通用主机【管理用户】信息：</h3>
        <span v-if="jms_config.ver === 'V3'"><font size="3px" color="#ff0000">JumpServer3.x请使用账号模板的ID：登录JumpServer-账号管理-账号模板-选择账号-基本信息-ID</font></span>
        <div class="demo-input-suffix">
          <h4>Linux：</h4>
          ssh端口：<el-input v-model="jms_config.linuxport" style="width: 72px;" />
          &nbsp;&nbsp;管理用户ID：<el-input v-model="jms_config.linuxuid" style="width: 300px;" />
        </div>
        <div class="demo-input-suffix">
          <h4>Windows：</h4>
          rdp端口：<el-input v-model="jms_config.winport" style="width: 72px;" />
          &nbsp;&nbsp;管理用户ID：<el-input v-model="jms_config.winuid" style="width: 300px;" />
        </div>
        <hr style="FILTER: alpha(opacity=100,finishopacity=0,style=2)" align=left width="96%" SIZE=1>
        <h3>全局特殊主机【管理用户】信息：</h3>
        <el-input v-model="jms_config.custom_ecs_info" :autosize="{ minRows: 5, maxRows: 18}" type="textarea" placeholder="请输入标准Json格式，无特殊主机请留空。" class="filter-item" style="width: 530px;" />
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
    <el-table v-loading="listLoading" :data="ecs_list" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" align="center" width="30" />
      <el-table-column prop="vendor" label="云厂商" sortable align="center" width="90" />
      <el-table-column prop="account" label="账号" sortable align="center" width="100" show-overflow-tooltip />
      <el-table-column prop="count_linux" label="Linux" sortable align="center" width="90" />
      <el-table-column prop="count_win" label="Win" sortable align="center" width="80" />
      <el-table-column prop="count_mem" label="总内存" sortable align="center" width="120" />
      <el-table-column prop="count_cpu" label="总CPU" sortable align="center" width="110" />
      <el-table-column prop="count_ecs" label="资源数" sortable align="center" width="100">
        <template slot-scope="{row}">
          <span style="font-weight:bold">{{ row.count_ecs }} </span>
          <el-tooltip style="diaplay:inline" effect="dark" placement="top">
            <div slot="content"> 开机：{{ row.count_on }}，关机：{{ row.count_off }} </div>
            <i class="el-icon-info" />
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="count_sync" label="同步数" sortable align="center" width="90" />
      <el-table-column prop="runtime" label="上次同步" sortable align="center" />
      <el-table-column prop="interval" label="同步间隔" sortable align="center" />
      <el-table-column prop="nextime" label="下次同步" sortable align="center" />
      <el-table-column label="同步" align="center" width="60" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-switch v-model="row.sync" active-color="#13ce66" @change="fetchSwitch(row.vendor, row.account, row.sync)" />
        </template>
      </el-table-column>
    </el-table>
    <el-dialog title="开启同步JumpServer" :visible.sync="swFormVisible" :before-close="fetchData" width="33%">
      <el-form ref="dataForm" :model="jms_sync" label-position="right" label-width="auto" style="width: 90%; margin-left: 20px;">
        <el-form-item label="同步间隔">
          <el-input v-model="jms_sync.interval" style="width: 180px;" type="number">
            <template slot="append">分钟</template>
          </el-input>
        </el-form-item>
        <el-form-item label="新节点ID">
          <el-input v-model="jms_sync.nodeid" />
        </el-form-item>
        <font size="3px" color="#ff0000">注意：每个云账号必须在JumpServer创建一个新节点！<br><br>JumpServer中已有的同名主机不会同步，日志可查看同名信息。</font>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="fetchData">
          取消
        </el-button>
        <el-button type="primary" @click="createSync(jms_sync)">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import { getJmsList, getJmsConfig, postJmsConfig, postJmsSwitch, postJmsSync } from '@/api/jms'
export default {
  data() {
    return {
      jms_config: { ver: 'V2', url: '', token: '', linuxport: '22', linuxuid: '', winport: '3389', winuid: '', custom_ecs_info: '' },
      listLoading: false,
      dialogFormVisible: false,
      query: { vendor: '', account: '' },
      ecs_list: [],
      vendor_list: [],
      account_list: [],
      jms_sync: { vendor: '', account: '', interval: '3', nodeid: '' },
      switch_dict: {},
      swFormVisible: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchSwitch(vendor, account, sync) {
      this.switch_dict = { vendor: vendor, account: account, sync: sync }
      if (sync) {
        this.jms_sync.vendor = vendor
        this.jms_sync.account = account
        postJmsSwitch(this.switch_dict).then(response => {
          this.jms_sync.interval = response.interval
          this.jms_sync.nodeid = response.nodeid
          this.swFormVisible = true
        })
      } else {
        this.$confirm('此操作将关闭同步功能，是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          postJmsSwitch(this.switch_dict).then(response => {
            this.fetchData()
            this.$message({
              message: response.data,
              type: response.type
            })
          })
        }).catch(() => {
          this.fetchData()
          this.$message({
            type: 'info',
            message: '操作已取消'
          })
        })
      }
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
      this.swFormVisible = false
      this.listLoading = true
      getJmsList(this.query).then(response => {
        this.vendor_list = response.vendor_list
        this.account_list = response.account_list
        this.ecs_list = response.ecs_list
        this.listLoading = false
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.listLoading = true
          postJmsConfig(this.jms_config).then(response => {
            this.listLoading = false
            if (response.code === 20000) {
              this.dialogFormVisible = false
              this.fetchData()
            }
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    createSync(jms_sync) {
      this.$confirm('此操作将开启同步功能，并进行首次同步，请等待（耗时依主机数而定，可在日志中查看进度）是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$refs['dataForm'].validate((valid) => {
          if (valid) {
            this.swFormVisible = false
            this.listLoading = true
            postJmsSync(jms_sync).then(response => {
              this.listLoading = false
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
    }
  }
}
</script>
