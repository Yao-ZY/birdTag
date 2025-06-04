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
              label="Old Password">
              <el-input
                v-model="form.oldpassword"
                type="password"
                placeholder="Please Input Password"
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
            @click="handleSave"
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
              padding-left: 210px;
              margin-bottom: 30px;
              height: 50px"
            @click="handleLogout"
          >Sign out</el-button>
        </el-form>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter()
const props = defineProps({
  cognitoUser: {
    type: Object,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
})

onMounted(() => {
  props.cognitoUser.getUserAttributes((err, attributes) => {
    if (err) {
      ElMessage.error(`Error loading user info: ${err.message}`);
      return;
    }

    const nameAttr = attributes.find(attr => attr.getName() === 'name');
    if (nameAttr) {
      form.value.your_name = nameAttr.getValue();
    }
  });
});

const form = ref({
  your_name: 'Yao Zhang',
  username: props.email,
  oldpassword: '',
  password: '',
  con_password: '',
})

const handleSave = () => {
  if (form.value.password) {
    if (form.value.password !== form.value.con_password) {
      ElMessage.error('Passwords do not match');
      return;
    }

    props.cognitoUser.changePassword(
      form.value.oldpassword,
      form.value.password, 
      (err) => {
        if (err) {
          ElMessage.error(`Password change failed: ${err.message}`);
        } else {
          ElMessage.success('Password updated successfully!');
          form.value.password = '';
          form.value.con_password = '';
        }
      }
    );
  } else {
    ElMessage.success('Profile saved (no password change)');
  }
};

const handleLogout = () => {
  props.cognitoUser.signOut();
  router.push('/');
  ElMessage.success('Sign out successful!');
};
</script>

<style lang="less" scoped>
.person {
    width: 90%;
    height: 650px;
    margin-left: 5%;
    background-color: #fff;
    border-radius: 20px;
    overflow-y:scroll;
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

:deep(.el-message-box) {
  width: 400px !important; 
  min-height: auto !important; 

  .el-message-box__content {
    padding: 20px; 
  }

  .el-message-box__message {
    font-size: 14px; 
    margin-bottom: 20px; 
  }

  .el-message-box__btns {
    justify-content: flex-end;
  }
}
</style>