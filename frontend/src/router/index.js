import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import RegisterStudent from '../views/RegisterStudent.vue'
import RegisterCompany from '../views/RegisterCompany.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register/student', component: RegisterStudent },
  { path: '/register/company', component: RegisterCompany },
  
  // Protected dashboard routes
  { 
    path: '/admin-dashboard', 
    component: AdminDashboard, 
    meta: { requiresRole: 'admin' } 
  },
  { 
    path: '/company-dashboard', 
    component: CompanyDashboard, 
    meta: { requiresRole: 'company' } 
  },
  { 
    path: '/student-dashboard', 
    component: StudentDashboard, 
    meta: { requiresRole: 'student' } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')

  if (to.meta.requiresRole) {
    if (!token) {
      // No token? Redirects to login
      next('/login')
    } else if (to.meta.requiresRole !== userRole) {
      // Role not matching? Forcefully redirects to login
      next('/login')
    } else {
      next() // Lets them proceed
    }
  } else {
    next() // Always allows public routes (login/register)
  }
})

export default router