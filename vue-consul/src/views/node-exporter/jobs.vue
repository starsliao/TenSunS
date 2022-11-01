<template>
  <div class="app-container">
    <el-alert type="success" center close-text="朕知道了">
      <el-link icon="el-icon-warning" type="success" href="https://github.com/starsliao/ConsulManager/blob/main/docs/ECS%E4%B8%BB%E6%9C%BA%E7%9B%91%E6%8E%A7.md" target="_blank">应用场景：如何优雅的使用Consul管理ECS主机监控</el-link>&nbsp;&nbsp;
      <el-link icon="el-icon-warning" type="primary" href="https://github.com/starsliao/ConsulManager/blob/main/docs/%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E7%9A%84%E4%BD%BF%E7%94%A8%E4%B8%80%E4%B8%AAmysqld_exporter%E7%9B%91%E6%8E%A7%E6%89%80%E6%9C%89%E7%9A%84MySQL%E5%AE%9E%E4%BE%8B.md" target="_blank">应用场景：如何优雅的使用1个mysqld_exporter监控所有的MySQL实例</el-link>
    </el-alert>
    <el-select v-model="query.vendor" placeholder="云厂商" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in vendor_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select v-model="query.account" placeholder="账户" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in account_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select v-model="query.itype" placeholder="类型" clearable style="width: 150px" class="filter-item" @change="fetchData(query)">
      <el-option v-for="item in itype_list" :key="item" :label="item" :value="item" />
    </el-select>

    <el-tooltip class="item" effect="light" content="清空查询条件" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="info" icon="el-icon-delete" circle @click="resetData" />
    </el-tooltip>
    <el-button class="filter-item" type="primary" icon="el-icon-s-promotion" @click="handleCreate">
      新增云资源
    </el-button>
    <el-button class="filter-item" type="warning" icon="el-icon-edit" @click="handleEdit">
      编辑云资源
    </el-button>
    <div style="float: right;">
      <el-tooltip class="item" effect="light" content="刷新当前页面" placement="top">
        <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchData" />
      </el-tooltip>
    </div>

    <el-table v-loading="listLoading" :data="joblist" :row-class-name="tableRowClassName" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" align="center" />
      <el-table-column prop="vendor" label="云厂商" sortable align="center" />
      <el-table-column prop="account" label="账户" sortable align="center" />
      <el-table-column prop="itype" label="资源" sortable align="center">
        <template slot-scope="{row}">
          <div v-if="row.itype !== 'group'" slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ row.itype.toUpperCase() }}</el-tag>
          </div>
          <div v-else>
            <span>{{ row.itype }} </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="region" label="区域" sortable align="center" />
      <el-table-column prop="count" label="资源数" sortable align="center">
        <template slot-scope="{row}">
          <span style="font-weight:bold">{{ row.count }} </span>
          <el-tooltip v-if="row.itype !== 'group'" style="diaplay:inline" effect="dark" placement="top">
            <div slot="content"> 开机：{{ row.on }}，关机：{{ row.off }} </div>
            <i class="el-icon-info" />
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="runtime" label="上次同步" sortable align="center" />
      <el-table-column prop="interval" label="同步间隔" sortable align="center">
        <template slot-scope="{row}">
          <span>{{ row.interval }}分钟</span>
        </template>
      </el-table-column>
      <el-table-column prop="nextime" label="下次同步" sortable align="center" />
      <el-table-column label="操作" align="center" width="280" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="success" size="mini" @click="row.itype==='group'?handleEnt(row.jobid):handleRes(row.itype,row.jobid)">
            查看
          </el-button>
          <el-button type="warning" size="mini" @click="handleRun(row.jobid)">
            同步
          </el-button>
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            编辑
          </el-button>
          <el-button type="danger" size="mini" @click="handleDelete(row.jobid)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog title="查看组信息" :visible.sync="entFormVisible" width="60%">
      <el-table v-loading="listLoading" :data="entlist" height="540" border fit highlight-current-row style="width: 100%;">
        <el-table-column type="index" align="center" />
        <el-table-column prop="gid" label="组ID" sortable align="center" />
        <el-table-column prop="gname" label="名称" sortable align="center" />
      </el-table>
    </el-dialog>

    <el-dialog title="新增云资源" :visible.sync="newFormVisible" width="40%">
      <el-form ref="dataForm" :rules="rules" :model="ecsJob" label-position="right" label-width="auto" style="width: 90%; margin-left: 1px;">
        <el-form-item label="云厂商" prop="vendor">
          <el-select v-model="ecsJob.vendor" placeholder="请选择" @change="ecsJob.region=[]">
            <el-option v-for="item in vendors" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item prop="account">
          <span slot="label">
            <span class="span-box">
              <span>账户</span>
              <el-tooltip style="diaplay:inline" effect="dark" content="用来区分云厂商不同云账户的标识，支持中文，例如用主账户的名称。" placement="top">
                <i class="el-icon-info" />
              </el-tooltip>
            </span>
          </span>
          <el-input v-model="ecsJob.account" />
        </el-form-item>
        <el-form-item label="Access Key" prop="ak">
          <el-input v-model="ecsJob.ak" placeholder="请输AccessKey ID" />
        </el-form-item>
        <el-form-item label="Secret Key" prop="sk">
          <el-input v-model="ecsJob.sk" placeholder="请输入AccessKey Secret" show-password />
        </el-form-item>
        <el-form-item label="区域" prop="region">
          <el-select v-model="ecsJob.region" filterable multiple collapse-tags placeholder="请选择">
            <el-option v-for="item in regions[ecsJob.vendor]" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="资源类型">
          <el-checkbox-group v-model="restype">
            <el-checkbox label="group" disabled>分组</el-checkbox>
            <el-checkbox label="ecs">ECS</el-checkbox>
            <el-checkbox label="rds">MySQL</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item prop="proj_interval">
          <span slot="label">
            <span class="span-box">
              <span>分组同步间隔(分钟)</span>
              <el-tooltip style="diaplay:inline" effect="dark" content="分组是采集云厂商用于资源分组的字段，阿里云：资源组，华为云：企业项目，腾讯云：所属项目。请在创建云主机时设置好属组。" placement="top">
                <i class="el-icon-info" />
              </el-tooltip>
            </span>
          </span>
          <el-input v-model="ecsJob.proj_interval" />
        </el-form-item>
        <el-form-item v-if="restype.includes('ecs')" label="ECS同步间隔(分钟)" prop="ecs_interval">
          <el-input v-model="ecsJob.ecs_interval" />
        </el-form-item>
        <el-form-item v-if="restype.includes('rds')" label="MySQL同步间隔(分钟)" prop="rds_interval">
          <el-input v-model="ecsJob.rds_interval" />
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="createAndNew()">
          确认并新增
        </el-button>
        <el-button @click="newFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="createData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <el-dialog title="编辑云资源" :visible.sync="editFormVisible" width="40%">
      <el-form ref="dataForm" :rules="rules" :model="editJob" label-position="right" label-width="auto" style="width: 90%; margin-left: 1px;">
        <el-form-item label="云厂商" prop="vendor">
          <el-select v-model="editJob.vendor" placeholder="请选择" @change="editJob.region=[];editJob.account=''">
            <el-option v-for="item in vendors" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="账户" prop="account">
          <el-select v-model="editJob.account" placeholder="请选择" @change="editJob.akskswitch=false;editJob.region=''">
            <el-option v-for="item in cloud_dict[editJob.vendor]" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="修改密钥">
          <el-switch v-model="editJob.akskswitch" />
        </el-form-item>
        <el-form-item v-if="editJob.akskswitch" label="Access Key" prop="ak">
          <el-input v-model="editJob.ak" placeholder="请输AccessKey ID" />
        </el-form-item>
        <el-form-item v-if="editJob.akskswitch" label="Secret Key" prop="sk">
          <el-input v-model="editJob.sk" placeholder="请输入AccessKey Secret" show-password />
        </el-form-item>

        <el-form-item label="区域" prop="region">
          <el-select v-model="editJob.region" filterable placeholder="请选择" @change="fetchGroup(editJob.vendor, editJob.account, editJob.region)">
            <el-option v-for="item in regions[editJob.vendor]" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="资源类型">
          <el-checkbox-group v-model="editJob.restype">
            <el-checkbox label="group" disabled>分组</el-checkbox>
            <el-checkbox label="ecs">ECS</el-checkbox>
            <el-checkbox label="rds">MySQL</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item prop="proj_interval">
          <span slot="label">
            <span class="span-box">
              <span>分组同步间隔(分钟)</span>
              <el-tooltip style="diaplay:inline" effect="dark" content="分组是采集云厂商用于资源分组的字段，阿里云：资源组，华为云：企业项目，腾讯云：所属项目。请在创建云主机时设置好属组。" placement="top">
                <i class="el-icon-info" />
              </el-tooltip>
            </span>
          </span>
          <el-input v-model="editJob.proj_interval" />
        </el-form-item>
        <el-form-item v-if="editJob.restype.includes('ecs')" label="ECS同步间隔(分钟)" prop="ecs_interval">
          <el-input v-model="editJob.ecs_interval" />
        </el-form-item>
        <el-form-item v-if="editJob.restype.includes('rds')" label="MySQL同步间隔(分钟)" prop="rds_interval">
          <el-input v-model="editJob.rds_interval" />
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="editFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="editData(editJob)">
          确认
        </el-button>
      </div>
    </el-dialog>

    <el-dialog title="更新同步间隔" :visible.sync="upFormVisible" width="30%">
      <el-form ref="dataForm" :rules="rules" :model="upjob" label-position="right" label-width="130px" style="margin-left: 20px;">
        <el-form-item label="同步间隔(分钟)" prop="interval">
          <el-input v-model="upjob.interval" placeholder="请输入" clearable style="width: 150px" class="filter-item" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="upFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAllJobs, PostJob, DelJob, getGroup } from '@/api/node-exporter'
import { getCloud, findGroup, PostEditJob } from '@/api/edit'
export default {
  data() {
    const validateInput = (rule, value, callback) => {
      if (!this.checkSpecialKey(value)) {
        callback(new Error('不能含有空格或 [ ]`~!#$^&*=|"{}\':/;\\?'))
      } else {
        callback()
      }
    }
    return {
      dialogStatus: '',
      listLoading: false,
      joblist: [],
      entlist: [],
      job_dict: {},
      vendor_list: [],
      account_list: [],
      itype_list: [],
      itype: [],
      restype: ['group', 'ecs'],
      query: { vendor: '', account: '', itype: '' },
      rules: {
        vendor: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        account: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        ak: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        sk: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        region: [{ required: true, message: '此为必填项', trigger: 'blur' }],
        proj_interval: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        ecs_interval: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }]
      },
      vendors: [{ value: 'alicloud', label: '阿里云' },
        { value: 'tencent_cloud', label: '腾讯云' },
        { value: 'huaweicloud', label: '华为云' }],

      regions: {
        huaweicloud: [
          { value: 'cn-east-3', label: '华东-上海一' },
          { value: 'cn-east-2', label: '华东-上海二' },
          { value: 'cn-south-1', label: '华南-广州' },
          { value: 'cn-north-1', label: '华北-北京一' },
          { value: 'cn-north-4', label: '华北-北京四' },
          { value: 'cn-southwest-2', label: '西南-贵阳一' },
          { value: 'ap-southeast-1', label: '中国-香港' },
          { value: 'ap-southeast-3', label: '新加坡' }
        ],
        alicloud: [
          { value: 'cn-qingdao', label: '华北1(青岛)' },
          { value: 'cn-beijing', label: '华北2(北京)' },
          { value: 'cn-zhangjiakou', label: '华北3(张家口)' },
          { value: 'cn-huhehaote', label: '华北5(呼和浩特)' },
          { value: 'cn-wulanchabu', label: '华北6(乌兰察布)' },
          { value: 'cn-hangzhou', label: '华东1(杭州)' },
          { value: 'cn-shanghai', label: '华东2(上海)' },
          { value: 'cn-shenzhen', label: '华南1(深圳)' },
          { value: 'cn-heyuan', label: '华南2(河源)' },
          { value: 'cn-guangzhou', label: '华南3(广州)' },
          { value: 'cn-chengdu', label: '西南1(成都)' },
          { value: 'cn-hongkong', label: '中国(香港)' },
          { value: 'cn-nanjing', label: '华东5(南京-本地地域)' },
          { value: 'us-east-1', label: '美国东部1(弗吉尼亚)' },
          { value: 'us-west-1', label: '美国(硅谷)' },
          { value: 'eu-west-1', label: '英国(伦敦)' },
          { value: 'ap-southeast-1', label: '新加坡' },
          { value: 'ap-northeast-1', label: '日本(东京)' }
        ],
        tencent_cloud: [
          { value: 'ap-nanjing', label: '华东地区(南京)' },
          { value: 'ap-shanghai', label: '华东地区(上海)' },
          { value: 'ap-guangzhou', label: '华南地区(广州)' },
          { value: 'ap-beijing', label: '华北地区(北京)' },
          { value: 'ap-tianjin', label: '华北地区(天津)' },
          { value: 'ap-chengdu', label: '西南地区(成都)' },
          { value: 'ap-chongqing', label: '西南地区(重庆)' },
          { value: 'ap-hongkong', label: '港澳台地区(中国香港)' },
          { value: 'ap-tokyo', label: '亚太地区(东京)' }
        ]
      },

      ecsJob: { vendor: '', ak: '', sk: '', region: [], account: '', proj_interval: 60, ecs_interval: 5, rds_interval: 5 },
      editJob: { restype: ['group'] },
      cloud_dict: {},
      upjob: { jobid: '', interval: '' },
      newFormVisible: false,
      upFormVisible: false,
      editFormVisible: false,
      entFormVisible: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    checkSpecialKey(str) {
      const specialKey = '[]`~!#$^&*/=\\|{}\'":;? '
      for (let i = 0; i < str.length; i++) {
        if (specialKey.indexOf(str.substr(i, 1)) !== -1) {
          return false
        }
      }
      return true
    },
    tableRowClassName({ row }) {
      if (row.itype === 'ecs') {
        return 'success-row'
      } else if (row.itype === 'rds') {
        return 'warning-row'
      }
      return ''
    },
    resetData() {
      this.query = { vendor: '', account: '', itype: '' }
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getAllJobs(this.query).then(response => {
        this.joblist = response.all_jobs
        this.vendor_list = response.vendor_list
        this.account_list = response.account_list
        this.itype_list = response.itype_list
        this.listLoading = false
      })
    },

    fetchGroup(vendor, account, region) {
      this.listLoading = true
      findGroup(vendor, account, region).then(response => {
        this.editJob.restype = response.restype
        this.editJob.proj_interval = response.interval.proj_interval
        this.editJob.ecs_interval = response.interval.ecs_interval
        this.editJob.rds_interval = response.interval.rds_interval
        this.listLoading = false
      })
    },
    handleEdit() {
      this.editJob = { vendor: '', akskswitch: false, ak: '', sk: '', region: '', account: '', restype: ['group'], proj_interval: 60, ecs_interval: 5, rds_interval: 5 }
      getCloud().then(response => {
        this.cloud_dict = response.cloud_dict
      })
      this.editFormVisible = true
    },
    handleCreate() {
      this.ecsJob = { vendor: '', ak: '', sk: '', region: [], account: '', proj_interval: 60, ecs_interval: 5, rds_interval: 5 }
      this.ecsJob.account = this.query.account
      this.newFormVisible = true
    },
    createAndNew() {
      this.createData()
      this.newFormVisible = true
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.upFormVisible = false
          this.listLoading = true
          this.upjob.dialogStatus = 'update'
          PostJob(this.upjob).then(response => {
            this.fetchData()
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    editData(editJob) {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.editFormVisible = false
          this.listLoading = true
          PostEditJob(editJob).then(response => {
            this.fetchData()
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.newFormVisible = false
          this.listLoading = true
          this.ecsJob.dialogStatus = 'create'
          this.ecsJob.restype = this.restype
          PostJob(this.ecsJob).then(response => {
            this.fetchData()
            this.$message({
              message: response.data,
              type: 'success'
            })
            this.ecsJob.region = []
          })
        }
      })
    },
    handleRun(jobid) {
      this.$confirm('此操作将立刻同步一次【' + jobid + '】是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true
        this.dialogStatus = 'run'
        this.job_dict = { dialogStatus: this.dialogStatus, jobid: jobid }
        PostJob(this.job_dict).then(response => {
          this.fetchData()
          this.$message({
            message: response.data,
            type: 'success'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '同步已取消'
        })
      })
    },
    handleUpdate(row) {
      this.upjob.jobid = row.jobid
      this.upjob.interval = row.interval
      this.upFormVisible = true
    },
    handleRes(restype, jobid) {
      this.$router.push({
        path: '/nodes/' + restype + '/lists',
        query: { job_id: jobid }
      })
    },
    handleEnt(jobid) {
      getGroup(jobid).then(response => {
        this.entFormVisible = true
        this.entlist = response.group
      })
    },
    handleDelete(jobid) {
      this.$confirm('此操作将删除【' + jobid + '】是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        DelJob(jobid).then(response => {
          this.fetchData()
          this.$message({
            message: response.data,
            type: 'success'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    }
  }
}
</script>

<style>
  .el-table .success-row {
    background: #f0f9eb;
  }
  .el-table .warning-row {
    background: oldlace;
  }
</style>
