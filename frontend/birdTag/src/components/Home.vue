<template>
    <div class="home">
      <el-container>
        <el-header class="header">
            <div class = "logo">
                <img src="../assets/theme.png" alt="logo">
                <span class ="theme_title">BIRDTAG</span>
            </div>
            <div class = "person">
                <span class ="theme_title">
                    {{ email }}
                </span>
            </div>
        </el-header>
        <el-container>
            <el-aside class="sidebar" :width="sidebarWidth">
                <div class="sidebar-content">
                    <img src="../assets/function.png" @click="toggleSidebar" style="margin-top: 10px;">
                    <div class="sidebar-item"  
                        v-for="item in sidebarItems" 
                        :key="item.id"
                        @click="handleItemClick(item.id)"
                        :style="{ backgroundColor: item.id == isSelected? '#F1F4FD' : '#fff'}">
                        <img :src="item.icon" alt="">
                        <div 
                           style="width: 50px;margin-left: 15px;color: #9EB0EA; font-weight: 400;" 
                           v-show="!isSidebarCollapsed">{{ item.label }}</div>
                    </div>
                </div>
            </el-aside>
            <el-main>
                <MainPage v-if="isSelected === 1" />
                <PersonPage v-if="isSelected === 3" 
                :cognito-user="cognitoUser" 
                :email="email"  />
                <UploadPage v-if="isSelected === 2" />
                <div class="bottom_over"> Welcome to the BridTag web application </div>
            </el-main>
        </el-container>
      </el-container>
    </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainPage from '../components/homepages/MainPage.vue';
import PersonPage from '../components/homepages/PersonPage.vue';
import UploadPage from '../components/homepages/UploadPage.vue';
import { userPool } from '../cognito'

const route = useRoute()
const router = useRouter()

const isSidebarCollapsed = ref(true)
const isSelected = ref(1)
const sidebarWidth = ref('86px')
const sidebarItems = reactive([
  { id: 1, icon: '/src/assets/home.png', label: 'Home'},
  { id: 2, icon: '/src/assets/cloudupload.png', label: 'Upload'},
  { id: 3, icon: '/src/assets/person.png', label: 'Profile'}
])
const email = ref("")
const cognitoUser = ref(null) 

onMounted(() => {
  email.value = route.query.email || ''
  const currentUser = userPool.getCurrentUser();
  if (currentUser) {
    currentUser.getSession((err, session) => {
      if (err || !session.isValid()) {
        alert("Invalid session, redirect to login")
        router.push('/')
        return
      }
      cognitoUser.value = currentUser;
    });
  } else {
    alert("No current user, jump to login")
    router.push('/')
  }
})


const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  sidebarWidth.value = isSidebarCollapsed.value ? '86px' : '200px'
}
const handleItemClick = (itemId) => {
  isSelected.value = itemId
}

</script>
<style lang="less" scoped>
.home {
    padding: 0;
    margin: 0;
    background-color: #F1F2F3;

    .header {
        height: 7%;
        padding: 15px 30px;
        background-color: #fff;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        

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

        .person {
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        text-align: end;

        .link-text {
            color: #9EB0EA;
            padding-right: 20px;
        }
    }
    }
    .sidebar {
        background-color: #fff;
        transition: width 0.3s ease;

        img {
            width: 24px;
            height: 24px;
            cursor: pointer;
        }

        .sidebar-item {
            display: flex;
            flex-direction: row;
            padding: 1.3rem 2rem;
            height: 25px;
            cursor: pointer;

            .sidebar-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 1rem;
                font-size: 1rem;
                color: #666;
                cursor: pointer;

                &:hover {
                background-color: #f5f7fa;
                }

                .el-icon {
                font-size: 1.2rem;
                }

                .item-label {
                    transition: opacity 0.3s ease;
                    color: #9EB0EA;
                    font-size: 18px;
                }
            }

            img {
                width: 24px;
                height: 24px;
            }
        }
    }
    .bottom_over {
        color: #9EB0EA;
        letter-spacing: 2px;
        font-weight: 600;
        font-size: 12px;
        height: 8px;
        margin-top: 15px;
    }

}
</style>