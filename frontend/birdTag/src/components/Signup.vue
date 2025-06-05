<template>
    <div class="signup">
        <div class = "logo">
            <img src="../assets/theme.png" alt="logo">
            <span class ="theme_title">BIRDTAG</span>
        </div>
        <p class = "title">Welcome Sign up Page!</p>
        <el-form
          :model="form"
          label-position="top"
          class="login-form" 
        >
          <el-form-item 
            style="height: 50px"
            label="First Name">
            <el-input 
              v-model= form.first_name
              placeholder="Please Input Your First Name"
            />
          </el-form-item>
          <el-form-item 
            style="height: 50px; margin-top: 60px"
            label="Last Name">
            <el-input 
              v-model= form.last_name
              placeholder="Please Input Your Last Name"
            />
          </el-form-item>
          <el-form-item 
            style="height: 50px; margin-top: 60px"
            label="Email">
            <el-input 
              v-model= form.email
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
            @click="handleLogin"
          >Save</el-button>
        </el-form>
        <p class="goback"> Go back!! <router-link to="/" class="link-text">Log in</router-link></p>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CognitoUserPool,
  CognitoUserAttribute
} from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: 'us-east-1_nyFLr2L5V',
  ClientId: '4atsi0gdvl985s56h3kcg702nv',
};
const userPool = new CognitoUserPool(poolData);
const router = useRouter()
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  con_password: '',
})

const handleLogin = () => {
  return new Promise((resolve, reject) => {
    const attributeList = [
      new CognitoUserAttribute({ Name: 'email', Value: form.value.email }),
      new CognitoUserAttribute({ Name: 'given_name', Value: form.value.first_name }),
      new CognitoUserAttribute({ Name: 'family_name', Value: form.value.last_name }),
    ]
    userPool.signUp(
      form.value.email, 
      form.value.password,
      attributeList,
      null,
      (err, result) => {
        if (err) {
          console.error('Signup error:', err)
          return reject(err)
        }
        console.log('Signup success:', result)
        resolve(result.user)
        router.push({ name: 'ConfirmSignup', query: { email: form.value.email } })
      }
    )
  });
}
</script>
<style lang="less" scoped>
.signup{
  margin-top: 60px;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 90%;
  margin-left: 5%;

    img {
      width: 24px;
      height: 24px;
    }

    .logo {
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      text-align: start;
      height: 2%;

      .theme_title {
        margin-left: 10px;
        font-weight: 700;
        color: #9EB0EA;
      }
    }

    .title {
        font-weight: 800;
        font-size: 24px;
        height: 2%;
        text-align: left;
        letter-spacing: 2px;
        margin-top: 20px;

        .link-text {
          color: #9EB0EA
        }
    }

    .login-form {
        width: 500px;
        margin-top: 10px;
        margin-left: 35%;
    }

    .goback {
        font-size: 14px;
        letter-spacing: 2px;
        margin-top: 20px;
        padding-left: 60px;

        .link-text {
          color: #9EB0EA;
          font-weight: 800;
        }
    }
}
</style>