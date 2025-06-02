<template>
    <div class="person">
        <p class = "title">Person Profile</p>
        <el-form
          :model="form"
          label-position="top"
          class="login-form" 
        >
          <el-form-item 
            style="height: 50px"
            label="Your Name">
            <el-input 
              v-model= form.your_name
              disabled
              placeholder="Please Input Your First Name"
            />
          </el-form-item>
          <el-form-item 
            style="height: 50px; margin-top: 60px"
            label="Email">
            <el-input 
              v-model= form.username
              disabled
              placeholder="Please Input Email"
            />
          </el-form-item>
          <el-form-item 
              style="height: 50px; margin-top: 60px"
              label="Password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="Please Input Password"
              />
          </el-form-item>
          <el-form-item 
              style="height: 50px; margin-top: 60px"
              label="Confirm Password">
              <el-input
                v-model="form.con_password"
                type="password"
                placeholder="Please Input Password"
              />
          </el-form-item>
          <el-button 
            style="
              color: #ffffff; 
              background-color: #8699DA; 
              border-radius: 80px;
              margin-top: 50px;
              text-align: center;
              font-weight: 800;
              padding-left: 220px;
              font-size: 18px;
              height: 50px"
          >Save</el-button>
          <el-button 
            style="
              color: #ffffff; 
              background-color: #C7696A; 
              border-radius: 80px;
              margin-top: 35px;
              text-align: center;
              font-weight: 800;
              font-size: 18px;
              margin-left: 0;
              padding-left: 165px;
              height: 50px"
          >Log out of account</el-button>
        </el-form>
    </div>
</template>
<script setup>
import { ref } from 'vue'
const form = ref({
  your_name: 'Yao Zhang',
  username: '123456@gmail',
  password: '',
  con_password: '',
})
</script>

<style lang="less" scoped>
.person {
    width: 90%;
    height: 650px;
    margin-left: 5%;
    background-color: #fff;
    border-radius: 20px;
    overflow: hidden;
    padding: 20px;
        img {
        width: 24px;
        height: 24px;
        }

    .title {
        font-weight: 700;
        font-size: 20px;
        height: 2%;
        text-align: left;
        letter-spacing: 3px;

        .link-text {
          color: #9EB0EA
        }
    }

    .login-form {
        width: 500px;
        margin-top: 30px;
        margin-left: 25%;
    }
}
</style>