<template>
  <div class="login">
    <div class="header">
      <div class = "logo">
        <img src="../assets/theme.png" alt="logo">
        <span class ="theme_title">BIRDTAG</span>
      </div>
      <div class = "home">
        <div class="title">
          <router-link to="/signup" class="link-text">Sign Up</router-link>
        </div>
        <img src="../assets/home.png" alt="home">
      </div>
    </div>
    <div class="main">
      <div class = "main-left">
        <p class = "title">WELCOME BACK!</p>
        <p class = "subTitle">
          Don't have a account, <router-link to="/signup" class="link-text">Sign Up</router-link>
        </p>
        <el-form
          :model="form"
          label-position="top"
          class="login-form" 
        >
          <el-form-item 
            style="height: 50px"
            label="Email">
            <el-input 
              v-model= form.username
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
          <el-button 
            @click="handleLogin"
            style="
              color: #ffffff; 
              background-color: #8699DA; 
              border-radius: 80px;
              margin-top: 80px;
              text-align: center;
              font-weight: 800;
              padding-left: 200px;
              font-size: 18px;
              height: 50px"
          >Sign In</el-button>
        </el-form>
      </div>
      <img src="../assets/Image.png" alt="image">
    </div>
  </div>
</template>
<!-- components/Login.vue -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = ref({
  username: '',
  password: '',
  isRemember: '',
})

const handleLogin = () => {
  console.log('data:', form.value)
  router.push('/home')
}
</script>
<style lang="less" scoped>
.login {
  margin-top: 60px;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 90%;
  margin-left: 5%;

  .header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    flex: 1;

    img {
      width: 24px;
      height: 24px;
    }

    .logo {
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      text-align: start;

      .theme_title {
        margin-left: 10px;
        font-weight: 700;
        color: #9EB0EA;
      }
    }

    .home {
      display: flex;
      flex-direction: row;
      justify-content: flex-end;
      text-align: end;

      .title {
        margin-right: 10px;
        font-weight: 700;
        font-size: 14px;
        line-height: 28px;

        .link-text {
          color: #9EB0EA
        }
      }
    }
  }

  .main {
    flex: 2;
    display: flex;
    flex-direction: row;
    margin-top: 40px;

    .main-left {
      flex: 6;
      margin-top:50px;

      .title {
        font-weight: 800;
        font-size: 24px;
        height: 30px;
        text-align: left;
        letter-spacing: 2px;
      }

      .subTitle {
        font-size: 14px;
        text-align: left;
        height: 28px;
        letter-spacing: 2px;
        margin-top: 20px;

        .link-text {
          color: #9EB0EA
        }
      }

      .login-form {
        width: 500px;
        margin-top: 20px;
      }
    }

    img {
      flex: 1;
      max-width: 100%;
      max-height: 70%;
    }

  }
}


</style>