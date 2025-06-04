<template>
    <div class="signup">
        <div class = "logo">
            <img src="../assets/theme.png" alt="logo">
            <span class ="theme_title">BIRDTAG</span>
        </div>
        <p class = "title">We've sent a verification code to <strong>{{ email }}</strong>.</p>
        <el-form
          :model="form"
          label-position="top"
          class="login-form" 
        >
          <el-form-item 
            style="height: 50px"
            label="Verify Code">
            <el-input 
              v-model = code
              placeholder="Please Input Code From Your Email"
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
            @click="handleConfirm"
          >Save</el-button>
        </el-form>
        <a class="goback" @click="handleResend"> Resend verification code </a>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { CognitoUser } from 'amazon-cognito-identity-js'
import { useRoute, useRouter } from 'vue-router'
import { userPool } from '../cognito'

const route = useRoute()
const router = useRouter()

const email = ref("")
const code = ref('')
const errorMessage = ref('')

onMounted(() => {
  email.value = route.query.email || ''
})

const handleConfirm = () => {
  const userData = {
    Username: email.value,
    Pool: userPool,
  }

  const cognitoUser = new CognitoUser(userData)

  cognitoUser.confirmRegistration(code.value, true, (err, result) => {
    if (err) {
      errorMessage.value = err.message || JSON.stringify(err)
      alert("You are Already Exit!!")
      return
    }
    alert('confirmation success')

    router.push('/')
  })
}
const handleResend = () => {
  const userData = {
    Username: email.value,
    Pool: userPool,
  }

  const cognitoUser = new CognitoUser(userData)

  cognitoUser.resendConfirmationCode((err, result) => {
    if (err) {
      errorMessage.value = err.message || JSON.stringify(err)
      return
    }
    alert('The verification code has been resent to your email address')
  })
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
        margin-top: 60px;
        margin-left: 35%;
    }

    .goback {
        font-size: 14px;
        letter-spacing: 2px;
        cursor: pointer;
        padding-left: 4%;
        margin-top: -20%;


        .link-text {
          color: #9EB0EA;
          font-weight: 800;
        }
    }
}
</style>