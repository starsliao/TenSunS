<template>
  <div class="login-container" :style="{ 'background-image': 'url(' + loginbgimg + ')' }">
    <div v-if="isbig" class="title-container" style="text-align:center; padding: 160px 70px 0;">
      <br><br>
      <img :src="loginlogo" width="720" :height=height>
      <br><br>
    </div>
    <div v-else class="title-container" style="text-align:center; padding: 260px 70px 0;">
      <img :src="loginlogo" width="100" height="100"><br><br><br>
      <h1 style="font-size:40px" class="title">{{ logintitle }}</h1>
    </div>
    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" auto-complete="on" label-position="left" style="padding: 10px 100px 0;">
      <el-form-item prop="username">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="username"
          v-model="loginForm.username"
          placeholder="用户名"
          name="username"
          type="text"
          tabindex="1"
          auto-complete="on"
        />
      </el-form-item>

      <el-form-item prop="password">
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          :key="passwordType"
          ref="password"
          v-model="loginForm.password"
          :type="passwordType"
          placeholder="密码"
          name="password"
          tabindex="2"
          auto-complete="on"
          @keyup.enter.native="handleLogin"
        />
        <span class="show-pwd" @click="showPwd">
          <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
        </span>
      </el-form-item>
      <!-- <el-checkbox v-model="loginForm.Ldapchecked" label="启动ldap验证" border class="ldap" /> -->
      <el-button :loading="loading" type="primary" round class="login-button" @click.native.prevent="handleLogin">登 录</el-button>
    </el-form>
    <div align="center" class="title-container">
      <span style="font-size:12px" class="title">{{ VER }}</span>
    </div>
    <div class="footer">
      <p style="width:100%"><center><el-link href="https://StarsL.cn" :underline="false" target="_blank">Powered by StarsL.cn</el-link></center></p>
    </div>
  </div>
</template>

<script>
import { logo, getbgimg, getitle } from '@/api/login'
import smallogo from '@/assets/login_images/SLH.png'
import biglogo from '@/assets/login_images/tensuns.png'
import bgimg from '@/assets/login_images/bg.png'

export default {
  name: 'Login',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!value) {
        callback(new Error('Please enter the correct user name'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('The password can not be less than 6 digits'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: 'admin',
        password: '',
        Ldapchecked: false // ldap验证开关
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      loading: false,
      passwordType: 'password',
      loginlogo: '',
      loginbgimg: '',
      logintitle: 'Welcome to TenSunS',
      isbig: true,
      height: '330',
      redirect: undefined
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  created() {
    this.fetchtitle()
    this.getlogo()
    this.getbg()
  },
  methods: {
    getlogo() {
      logo().then(response => {
        if (response.data === 'default') {
          if (response.isbig === true) {
            this.loginlogo = biglogo
            this.isbig = true
          } else {
            this.loginlogo = smallogo
            this.isbig = false
          }
        } else {
          if (response.data === 'data:image/png;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7') {
            this.height = response.logoheight
          }
          this.loginlogo = response.data
          this.isbig = response.isbig
        }
      })
    },

    fetchtitle() {
      getitle().then(response => {
        if (response.data !== 'default') {
          this.logintitle = response.data
        }
      })
    },

    getbg() {
      getbgimg().then(response => {
        if (response.data === 'default') {
          this.loginbgimg = bgimg
        } else {
          this.loginbgimg = response.data
        }
      })
    },

    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$store.dispatch('user/login', this.loginForm).then(() => {
            this.$router.push({ path: this.redirect || '/' })
            this.loading = false
          }).catch(() => {
            this.loading = false
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    }
  }
}
</script>

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg:#283443;
$light_gray:#fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

/* reset element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .login-button {
    width:60%;
    display: block;
    margin: 0 auto;
    margin-bottom:15px;
    border: 0px solid rgba(255, 255, 255, 0);
    background: rgba(0, 0, 0, 0.2);
  }
  .el-form-item {
    border: 0px solid rgba(255, 255, 255, 0);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
  .el-form-item__content {
    line-height: 33px;
    position: relative;
    font-size: 14px
  }
}
</style>

<style lang="scss" scoped>
$bg:#2d3a4b;
$dark_gray:#889aa4;
$light_gray:#eee;

.ldap{
  margin-bottom: 9px;
}

.login-container {
  // min-height: 100%;
  // width: 100%;
  // background-color: $bg;
  // overflow: hidden;
  width: 100%;
  height: 100%;
  //background-image: url("../../assets/login_images/bg.png");
  background-size: cover;
  background-position: center;
  position: relative;

  .login-form {
    position: relative;
    width: 460px;
    max-width: 100%;
    padding: 160px 35px 0;
    margin: 0 auto;
    overflow: hidden;
  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 20px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .footer {
    p {
      position:absolute;
      bottom:0px;
      padding:0px;
      margin:0px;
    }
  }
  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }
}
</style>
