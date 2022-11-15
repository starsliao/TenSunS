<template>
  <el-main>
    <el-tabs :tab-position="tabPosition" style="height: auto;width: 600px;">
      <el-tab-pane label="统一认证">
        <!-- 统一认证 -->
        <el-form ref="ruleForm" :model="ruleForm" status-icon :rules="rules" label-width="100px" class="demo-ruleForm">
          <el-form-item label="认证地址:" prop="ldap_url">
            <el-input v-model="ruleForm.ldap_url" type="text" autocomplete="off" />
          </el-form-item>

          <el-form-item label="端口号:" prop="port">
            <el-input v-model="ruleForm.port" type="text" autocomplete="off" />
          </el-form-item>

          <el-alert class="alert" title="示例：uid=xxx,cn=xxx,dc=xxx,dc=xxx" type="info" />
          <el-form-item label="bind_dn:" prop="rule">
            <el-input v-model="ruleForm.rule" type="text" autocomplete="off" />
          </el-form-item>

          <el-form-item label="认证密码:" prop="password">
            <el-input v-model="ruleForm.password" type="password" autocomplete="off" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
            <el-button @click="resetForm('ruleForm')">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-main>
</template>
<script>
import { setldap } from '@/api/ldap'
export default {
  data() {
    return {
      tabPosition: 'left',
      ruleForm: {}, // 存储ldap
      rules: {
        ldap_url: [{ validator: 'xxx', trigger: 'blur' }],
        port: [{ validator: 'xxxx', trigger: 'blur' }],
        rule: [{ validator: 'xxx', trigger: 'blur' }],
        password: [{ validator: 'xxx', trigger: 'blur' }]
      } // 校验规则
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // 使用箭头函数进行发送请求
          setldap(this.ruleForm).then(response => {
            if (response.code === 200) {
              this.$message({
                type: 'success',
                message: response.message
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
