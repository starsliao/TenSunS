<template>
  <el-main>
    <el-tabs :tab-position="tabPosition" style="height: auto;width: 600px;">
      <el-tab-pane label="LDAP">
        <!-- 统一认证 -->
        <el-form ref="ruleForm" :model="ruleForm" status-icon :rules="rules" label-width="150px" class="demo-ruleForm">
          <el-form-item label="地址" prop="ldap_url">
            <el-input v-model="ruleForm.ldap_url" type="text" placeholder="仅输入IP或域名，如：192.168.10.26" autocomplete="off" />
          </el-form-item>
          <el-form-item label="端口" prop="port">
            <el-input v-model="ruleForm.port" type="text" placeholder="LDAP的端口" autocomplete="off" />
          </el-form-item>
          <!-- <el-alert class="alert" title="示例：uid=xxx,cn=xxx,dc=xxx,dc=xxx" type="info" /> -->
          <el-form-item label="绑定 DN" prop="rule">
            <el-input v-model="ruleForm.rule" type="textarea" placeholder="uid=xxx,cn=abc,dc=def,dc=yyy" autosize autocomplete="off" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="ruleForm.password" type="password" placeholder="Bind DN Password" autocomplete="off" />
          </el-form-item>

          <el-form-item label="LDAP用户名模板" prop="ldapusr">
            <el-input v-model="ruleForm.ldapusr" type="textarea" placeholder="uid={username},cn=abc,dc=def,dc=yyy" autosize autocomplete="off" /><br><font size="2px" color="#ff0000">请复制绑定DN，然后把用户名部分用＂{username}＂替换。</font>
          </el-form-item>
          <el-form-item label="LDAP用户白名单" prop="allow">
            <el-input v-model="ruleForm.allow" type="textarea" placeholder="请输入允许登录的LDAP用户名" autosize autocomplete="off" /><br><font size="2px" color="#ff0000">多用户使用＂,＂间隔，*：允许所有LDAP用户，留空：禁用LDAP</font>
          </el-form-item>
          <el-form-item style="text-align: center">
            <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
            <!-- <el-button @click="resetForm('ruleForm')">重置表单</el-button> -->
            <el-button type="danger" @click="delForm()">删除LDAP</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-main>
</template>
<script>
import { setldap, getLdap, delLdap } from '@/api/ldap'
export default {
  data() {
    return {
      tabPosition: 'left',
      ruleForm: { port: '389', allow: '*' }, // 存储ldap
      rules: {
        ldap_url: [{ required: true, trigger: 'blur', message: '地址不能为空' }],
        port: [{ required: true, trigger: 'blur', message: '端口不能为空' }],
        rule: [{ required: true, trigger: 'blur', message: '绑定 DN不能为空' }],
        password: [{ required: true, trigger: 'blur', message: '密码不能为空' }],
        ldapusr: [{ required: true, trigger: 'blur', message: 'LDAP用户名模板不能为空' }]
      } // 校验规则
    }
  },
  created() {
    this.fetchData()
  },

  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // 使用箭头函数进行发送请求
          setldap(this.ruleForm).then(response => {
            if (response.code === 20000) {
              this.$message({
                type: 'success',
                message: 'LDAP配置成功！'
              })
              return
            }
            this.$message({
              type: 'error',
              message: response.message
            })
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    fetchData() {
      this.listLoading = true
      getLdap().then(response => {
        this.ruleForm = response.ldap_info
        this.listLoading = false
      })
    },
    delForm() {
      this.listLoading = true
      this.$confirm('此操作将删除所有的LDAP设置?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        delLdap().then(response => {
          this.$message({
            message: response.data,
            type: 'success'
          })
          this.ruleForm = { port: '389', allow: '*' }
          this.listLoading = false
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>

<style lang="scss">
.alert{
  width: 500px;
  margin-left:100px;
  margin-bottom:2px;
}
</style>
