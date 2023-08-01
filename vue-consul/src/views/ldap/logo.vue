<template>
  <div>
    <el-alert type="success" center close-text="朕知道了">
      图片大小不能超过380KB,建议使用<el-link type="primary" href="https://tinypng.com/" target="_blank">TinyPNG</el-link>在线压缩图片
    </el-alert>
    <el-row>
      <el-col :span="8" align='center'><div class="grid-content bg-purple">
        <el-alert
          title="更换背景壁纸(自动拉伸)"
          center
          :closable="false"
          type="info"
          effect="dark"
        />
        <el-upload
          class="avatar-uploader"
          action="/api/login/bgimg"
          :headers="myHeaders"
          :show-file-list="false"
          :on-success="handleAvatarSuccess1"
          :before-upload="beforeAvatarUpload"
        >
          <img v-if="imageUrl1" :src="imageUrl1" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon" />
        </el-upload>
        <br><el-button type="primary" @click="setrebgimg">恢复默认壁纸</el-button>
      </div></el-col>
      <el-col :span="8" align='center'><div class="grid-content bg-purple-light">
        <el-alert
          title="使用横幅风格(自动缩放720*330,并隐藏名称)"
          center
          :closable="false"
          type="warning"
          effect="dark"
        />
        <el-upload
          class="avatar-uploader"
          action="/api/login/biglogo"
          :headers="myHeaders"
          :show-file-list="false"
          :on-success="handleAvatarSuccess2"
          :before-upload="beforeAvatarUpload"
        >
          <img v-if="imageUrl2" :src="imageUrl2" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon" />
        </el-upload>
        <br><el-button type="primary" @click="setrebig">恢复默认横幅风格</el-button>
      </div></el-col>
      <el-col :span="8" align='center'><div class="grid-content bg-purple-light">
        <el-alert
          title="使用LOGO+名称风格(自动缩放100*100,并显示名称)"
          center
          :closable="false"
          type="success"
          effect="dark"
        />
        <el-upload
          class="avatar-uploader"
          action="/api/login/smallogo"
          :headers="myHeaders"
          :show-file-list="false"
          :on-success="handleAvatarSuccess3"
          :before-upload="beforeAvatarUpload"
        >
          <img v-if="imageUrl3" :src="imageUrl3" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon" />
        </el-upload>
        <br><el-button type="primary" @click="setresmall">恢复默认LOGO风格</el-button>
      </div></el-col>
    </el-row><br>
    <el-divider><i class="el-icon-s-promotion" />展示名称</el-divider>
    <el-form :inline="true" :model="formtitle" class="demo-form-inline">
      <el-form-item>
        <span slot="label">
          <span class="span-box">
            &nbsp;&nbsp;<span>登录页名称</span>
            <el-tooltip style="diaplay:inline" effect="dark" content="登录页面展示的名称,仅在LOGO风格的时候会展示名称。" placement="top">
              <i class="el-icon-info" />
            </el-tooltip>
          </span>
        </span>
        <el-input v-model="formtitle.title" placeholder="默认显示:TenSunS" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setitle">设置名称</el-button>
      </el-form-item>
      <el-form-item>
        &nbsp;&nbsp;&nbsp;&nbsp;<el-button type="info" icon="el-icon-refresh-left" @click="setretitle">恢复默认名称</el-button>
      </el-form-item>
      <el-divider><i class="el-icon-s-promotion" />壁纸模式</el-divider>
      <el-form-item>
        <span slot="label">
          <span class="span-box">
            &nbsp;&nbsp;<span>登录框位置</span>
            <el-tooltip style="diaplay:inline" effect="dark" content="登录框位置仅壁纸模式可用，默认位置的值是450，增大该值，登录框位置下移。" placement="top">
              <i class="el-icon-info" />
            </el-tooltip>
          </span>
        </span>
        <el-input v-model="formtitle.height" placeholder="壁纸模式默认位置值:450" />
      </el-form-item>
      <el-form-item>
        <el-button type="warning" icon="el-icon-magic-stick" @click="setnologo">设置并进入壁纸模式</el-button>
      </el-form-item>
    </el-form>

  </div>
</template>

<script>
import { postitle, postnologo, rebig, resmall, rebgimg, retitle } from '@/api/login'

export default {
  data() {
    return {
      myHeaders: { Authorization: this.$store.getters.token },
      imageUrl1: '',
      imageUrl2: '',
      imageUrl3: '',
      formtitle: { title: '', height: '' }
    }
  },
  methods: {
    setrebig() {
      rebig().then(response => {
        this.$message.success(response.data)
      })
    },
    setresmall() {
      resmall().then(response => {
        this.$message.success(response.data)
      })
    },
    setrebgimg() {
      rebgimg().then(response => {
        this.$message.success(response.data)
      })
    },
    setretitle() {
      retitle().then(response => {
        this.$message.success(response.data)
      })
    },

    setnologo() {
      postnologo(this.formtitle.height).then(response => {
        this.$message.success(response.data)
      })
    },
    setitle() {
      postitle(this.formtitle.title).then(response => {
        this.$message.success(response.data)
      })
    },
    handleAvatarSuccess1(res, file) {
      this.imageUrl1 = URL.createObjectURL(file.raw)
      if (res.code === 20000) {
        this.$message.success(res.data)
      } else {
        this.$message.error(res.data)
      }
    },
    handleAvatarSuccess2(res, file) {
      this.imageUrl2 = URL.createObjectURL(file.raw)
      if (res.code === 20000) {
        this.$message.success(res.data)
      } else {
        this.$message.error(res.data)
      }
    },
    handleAvatarSuccess3(res, file) {
      this.imageUrl3 = URL.createObjectURL(file.raw)
      if (res.code === 20000) {
        this.$message.success(res.data)
      } else {
        this.$message.error(res.data)
      }
    },
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 < 380
      if (!isJPG) {
        this.$message.error('上传LOGO图片只能是 JPG/PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传LOGO图片大小不能超过 380KB!')
      }
      return isJPG && isLt2M
    }
  }
}
</script>

<style>
  .avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .avatar-uploader .el-upload:hover {
    border-color: #409EFF;
  }
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    line-height: 178px;
    text-align: center;
  }
  .avatar {
    width: 178px;
    height: 178px;
    display: block;
  }
</style>
