import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import RegisterStudent from '../views/RegisterStudent.vue'
import RegisterCompany from '../views/RegisterCompany.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register/student', component: RegisterStudent },
  { path: '/register/company', component: RegisterCompany }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router