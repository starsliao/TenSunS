<template>
  <div class="app-container">
    <el-alert v-if="services_name === 'blackbox_exporter'" title="如需管理【blackbox_exporter】的监控实例，建议使用左侧菜单【Blackbox 站点监控】来维护，更加方便直观。" type="success" center close-text="知道了" />
    <el-select v-model="services_name" placeholder="请选择 Services" filterable collapse-tags style="width: 250px" class="filter-item" @change="fetchData(services_name)">
      <el-option v-for="item in services_name_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-tooltip class="item" effect="light" content="刷新当前Services" placement="top">
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-refresh" circle @click="fetchData(services_name)" />
    </el-tooltip>
    <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="handleCreate">
      新增
    </el-button>
    <el-button class="filter-item" type="danger" icon="el-icon-delete" @click="handleDelAll">
      批量删除
    </el-button>

    <el-table ref="expandstable" v-loading="listLoading" :data="instances" border fit highlight-current-row style="width: 100%;" @selection-change="handleSelectionChange">
      <el-table-column type="selection" align="center" width="30" />
      <el-table-column label="ID" width="50px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.$index+1 }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="id" label="实例ID" sortable align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.ID }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="address" label="地址" sortable width="150px" align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.address }} </span>
        </template>
      </el-table-column>

      <el-table-column prop="port" label="端口" width="80px" sortable align="center">
        <template slot-scope="{row}">
          <span>{{ row.port }} </span>
        </template>
      </el-table-column>

      <el-table-column prop="tags" label="Tags" sortable align="center" width="200">
        <template slot-scope="{row}">
          <el-tag v-for="atag in row.tags" :key="atag" size="mini">{{ atag }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="meta" label="Meta" align="center" width="80px">
        <template slot-scope="{row}">
          <span v-if="row.meta === '无'">{{ row.meta }}</span>
          <el-link v-else type="primary" @click="expandsHandle(row)">展开</el-link>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="80px" sortable align="center">
        <template slot-scope="{row}">
          <span>{{ row.status }} </span>
        </template>
      </el-table-column>

      <el-table-column prop="output" label="检查明细" sortable align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span style="font-size: 12px">{{ row.output }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            编辑
          </el-button>
          <el-button size="mini" type="danger" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
      <el-table-column type="expand" width="1">
        <template slot-scope="{row}">
          <el-table style="width: 100%" :data="row.meta" row-class-name="success-row" fit border>
            <el-table-column v-for="{ prop, label } in row.meta_label" :key="prop" :prop="prop" :label="label" />
          </el-table>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="45%">
      <el-form ref="dataForm" :rules="rules" :model="newService" label-position="right" label-width="100px" style="width: 500px; margin-left: 50px;">
        <el-form-item label="所属服务组" prop="name">
          <el-autocomplete v-model="newService.name" :fetch-suggestions="Sugg_name" placeholder="优先选择" clearable style="width: 360px" class="filter-item" />
        </el-form-item>
        <div v-if="dialogStatus==='update'">
          <el-form-item label="服务实例ID" prop="ID">
            <el-input v-model="newService.ID" placeholder="请输入" clearable style="width: 360px" :disabled="true" />
          </el-form-item>
        </div>
        <div v-else>
          <el-form-item label="服务实例ID" prop="ID">
            <el-input v-model="newService.ID" placeholder="请输入" clearable style="width: 360px" class="filter-item" />
          </el-form-item>
        </div>
        <el-form-item label="地址" prop="address">
          <el-input v-model="newService.address" placeholder="请输入" clearable style="width: 360px" class="filter-item" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input v-model="newService.port" placeholder="请输入" clearable style="width: 360px" class="filter-item" />
        </el-form-item>
        <el-form-item label="Tags" prop="tags">
          <el-tag v-for="tag in newService.tags" :key="tag" closable :disable-transitions="false" @close="handleClose(tag)">{{ tag }}</el-tag>
          <el-input v-if="inputVisible" ref="saveTagInput" v-model="inputValue" class="input-new-tag" size="small" @keyup.enter.native="handleInputConfirm" @blur="handleInputConfirm" />
          <el-button v-else class="button-new-tag" size="small" type="primary" icon="el-icon-circle-plus-outline" @click="showInput">新增</el-button>
        </el-form-item>

        <el-form-item label="配置Meta" prop="isMeta">
          <el-switch v-model="newService.metaInfo.isMeta" />
        </el-form-item>
        <el-form-item v-if="newService.metaInfo.isMeta" prop="newmeta">
          <span slot="label">
            <span class="span-box">
              <span>Meta</span>
              <el-tooltip style="diaplay:inline" effect="dark" content='Meta必须是JSON字符串格式，例如：{ "aaa":"bbb", "ccc": "ddd" }' placement="top">
                <i class="el-icon-info" />
              </el-tooltip>
            </span>
          </span>
          <el-input v-model="newService.metaInfo.metaJson" :autosize="{ minRows: 2, maxRows: 4}" type="textarea" placeholder='{ "aaa": "bbb", "ccc": "ddd" }' clearable style="width: 360px" class="filter-item" />
        </el-form-item>

        <el-form-item v-if="coption !== '' && dialogStatus==='update'" label="健康检查操作" prop="coption">
          <el-radio-group v-model="coption" @change="modcheck">
            <el-radio label="false">不修改</el-radio>
            <el-radio label="delete">删除健康检查</el-radio>
            <el-radio label="modf">修改健康检查</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form :inline="true" class="demo-form-inline" label-position="right" label-width="100px">
          <el-form-item v-if="coption === '' || coption === 'modf'" label="健康检查" prop="isCheck">
            <el-switch v-model="newService.checkInfo.isCheck" active-text="　　　　　" />
          </el-form-item>
          <el-form-item v-if="newService.checkInfo.isCheck" label="检查类型" prop="ctype">
            <el-select v-model="newService.checkInfo.ctype" placeholder="请选择" style="width: 120px">
              <el-option label="TCP" value="TCP" />
              <el-option label="HTTP" value="HTTP" />
              <el-option label="GRPC" value="GRPC" />
            </el-select>
          </el-form-item>
        </el-form>
        <el-form-item v-if="newService.checkInfo.isCheck" label="检查地址" prop="isAddress">
          <el-radio-group v-model="newService.checkInfo.isAddress">
            <el-radio label="true">与实例IP端口一致</el-radio>
            <el-radio label="false">自定义</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="newService.checkInfo.isCheck && newService.checkInfo.isAddress === 'false'" prop="caddress">
          <span slot="label">
            <span class="span-box">
              <span>地址信息</span>
              <el-tooltip style="diaplay:inline" effect="dark" content="检查类型为HTTP时，地址必须以http开头。" placement="top">
                <i class="el-icon-info" />
              </el-tooltip>
            </span>
          </span>
          <el-input v-model="newService.checkInfo.caddress" placeholder="请输入" clearable style="width: 360px" />
        </el-form-item>

        <el-form v-if="newService.checkInfo.isCheck" :inline="true" class="demo-form-inline" label-position="right" label-width="100px">
          <el-form-item label="检查间隔" prop="interval">
            <el-input v-model="newService.checkInfo.interval" placeholder="请输入" clearable style="width: 120px" />
          </el-form-item>
          <el-form-item label="检查超时" prop="timeout">
            <el-input v-model="newService.checkInfo.timeout" placeholder="请输入" clearable style="width: 120px" />
          </el-form-item>
        </el-form>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button v-if="dialogStatus==='create'" type="primary" @click="createAndNew">
          确认并新增
        </el-button>
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getInstances, getServicesName, delSid, addSid } from '@/api/consul'
export default {
  data() {
    const validateInput = (rule, value, callback) => {
      if (!this.checkSpecialKey(value)) {
        callback(new Error('不能含有空格或 [ ]`~!#$^&*=|"{}\':;?'))
      } else {
        callback()
      }
    }
    return {
      instances: [],
      services_name: '',
      services_name_list: [],
      multipleSelection: [],
      newService: {
        ID: '',
        name: '',
        address: '',
        port: '',
        tags: [],
        metaInfo: {
          isMeta: false,
          metaJson: ''
        },
        checkInfo: {
          isCheck: false,
          ctype: 'TCP',
          isAddress: 'true',
          caddress: '',
          interval: '15s',
          timeout: '5s'
        }
      },
      coption: '',
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '更新',
        create: '创建'
      },
      value_name: [],
      inputVisible: false,
      inputValue: '',
      rules: {
        name: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }],
        ID: [{ required: true, message: '此为必填项', trigger: 'change' },
          { validator: validateInput, trigger: ['blur', 'change'] }]
      }
    }
  },
  created() {
    this.fetchServicesName()
    if (this.$route.query.service_name) {
      this.fetchData(this.$route.query.service_name)
    }
  },
  mounted() {
    if (this.$route.query.service_name) {
      this.services_name = this.$route.query.service_name
    }
  },
  methods: {
    expandsHandle(row) {
      this.$refs.expandstable.toggleRowExpansion(row)
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    Sugg_name(queryString, cb) {
      var xname = this.xname
      var results = queryString ? xname.filter(this.createFilter(queryString)) : xname
      cb(results)
    },
    load_name() {
      for (const x in this.services_name_list) {
        this.value_name.push({ 'value': this.services_name_list[x] })
      }
      return this.value_name
    },
    createFilter(queryString) {
      return (restaurant) => {
        return (restaurant.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0)
      }
    },
    handleClose(tag) {
      this.newService.tags.splice(this.newService.tags.indexOf(tag), 1)
    },

    showInput() {
      this.inputVisible = true
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus()
      })
    },

    handleInputConfirm() {
      const inputValue = this.inputValue
      if (inputValue) {
        this.newService.tags.push(inputValue)
      }
      this.inputVisible = false
      this.inputValue = ''
    },
    checkSpecialKey(str) {
      const specialKey = '[]`~!#$^&*=|{}\'":;? '
      for (let i = 0; i < str.length; i++) {
        if (specialKey.indexOf(str.substr(i, 1)) !== -1) {
          return false
        }
      }
      return true
    },
    modcheck(label) {
      if (label === 'modf') {
        this.newService.checkInfo.isCheck = true
      } else {
        this.newService.checkInfo.isCheck = false
      }
    },
    handleCreate() {
      this.coption = ''
      this.newService = { ID: '', name: '', address: '', port: '', tags: [], metaInfo: { isMeta: false, metaJson: '' }, checkInfo: { isCheck: false, ctype: 'TCP', isAddress: 'true', caddress: '', interval: '15s', timeout: '5s' }}
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.newService.name = this.services_name
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.newService.tags = [...new Set(this.newService.tags)]
          addSid(this.newService).then(response => {
            this.fetchServicesName()
            this.services_name = this.newService.name
            this.fetchData(this.newService.name)
            this.dialogFormVisible = false
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
        }
      })
    },
    createAndNew() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.newService.tags = [...new Set(this.newService.tags)]
          addSid(this.newService).then(response => {
            this.fetchServicesName()
            this.services_name = this.newService.name
            this.fetchData(this.newService.name)
            this.$message({
              message: response.data,
              type: 'success'
            })
            this.dialogStatus = 'create'
            this.newService.ID = ''
            this.newService.address = ''
            this.newService.port = ''
            this.$nextTick(() => {
              this.$refs['dataForm'].clearValidate()
            })
          })
        }
      })
    },
    fetchData(sname) {
      this.listLoading = true
      getInstances(sname).then(response => {
        this.instances = response.instances
        this.listLoading = false
      })
    },
    fetchServicesName() {
      this.listLoading = true
      getServicesName().then(response => {
        this.services_name_list = response.services_name
        this.listLoading = false
        this.xname = this.load_name()
      })
    },
    handleUpdate(row) {
      this.coption = ''
      this.newService.checkInfo.isCheck = false
      this.newService.ID = row.ID
      this.newService.name = row.name
      this.newService.address = row.address
      this.newService.port = row.port
      if (row.tags === '无') {
        this.newService.tags = []
      } else {
        this.newService.tags = row.tags
      }
      if (row.meta === '无') {
        this.newService.metaInfo.isMeta = false
      } else {
        this.newService.metaInfo.isMeta = true
        this.newService.metaInfo.metaJson = JSON.stringify(row.meta[0])
      }
      if (row.status === '无') {
        this.newService.checkInfo.isCheck = false
      } else {
        this.coption = 'false'
      }

      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          if (this.coption === 'delete') {
            delSid(this.newService.ID).then(response => {
              addSid(this.newService).then(response => {
                this.fetchServicesName()
                this.services_name = this.newService.name
                this.fetchData(this.newService.name)
                this.dialogFormVisible = false
                this.$message({
                  message: response.data,
                  type: 'success'
                })
              })
            })
          } else {
            addSid(this.newService).then(response => {
              this.fetchServicesName()
              this.services_name = this.newService.name
              this.fetchData(this.newService.name)
              this.dialogFormVisible = false
              this.$message({
                message: response.data,
                type: 'success'
              })
            })
          }
        }
      })
    },
    handleDelete(row) {
      this.$confirm('此操作将删除【' + row.name + '】：\n' + row.ID + '，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        delSid(row.ID).then(response => {
          this.$message({
            message: response.data,
            type: 'success'
          })
          this.$delete(this.instances, this.instances.indexOf(row))
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleDelAll() {
      this.$confirm('此操作将批量删除选中行，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        for (let i = 0; i < this.multipleSelection.length; i++) {
          delSid(this.multipleSelection[i].ID).then(response => {
            this.$message({
              message: response.data,
              type: 'success'
            })
          })
          this.$delete(this.instances, this.instances.indexOf(this.multipleSelection[i]))
        }
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
.el-table__expand-column .cell {
  display: none;
}
.el-table .success-row {
  background: oldlace;
}
.el-tag + .el-tag {
  margin-left: 10px;
}
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>
