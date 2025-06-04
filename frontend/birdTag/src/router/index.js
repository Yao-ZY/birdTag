import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import Signup from '../components/Signup.vue'
import Home from '../components/Home.vue'
import MainPage from '../components/homepages/MainPage.vue'
import PersonPage from '../components/homepages/PersonPage.vue'
import UploadPage from '../components/homepages/UploadPage.vue'
import ConfirmSignup from '../components/ConfirmSignup.vue'
const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup
  },
  {
    path: '/confirmsignup',
    name: 'ConfirmSignup',
    component: ConfirmSignup
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    children: [
    {
      path: '',
      name: 'MainPage',
      component: MainPage
    },
    {
      path: 'person',
      name: 'PersonPage',
      component: PersonPage
    },
    {
      path: 'upload',
      name: 'UploadPage',
      component: UploadPage
    }]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router