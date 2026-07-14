<template>
  <div class="login-wrapper d-flex justify-content-center align-items-center min-vh-100">
    <div class="card p-5 shadow-lg border-0 login-card" style="width: 100%; max-width: 440px;">
      <!-- Modern logo icon -->
      <div class="text-center mb-4">
        <div class="logo-icon bg-primary text-white rounded-3 mx-auto mb-2 d-flex align-items-center justify-content-center">
          <span class="fw-bold fs-4">P</span>
        </div>
        <h3 class="fw-bold text-dark mb-1">Placement Portal</h3>
        <p class="text-muted small">Access your account and dashboard</p>
      </div>
      
      <!-- Error alerts -->
      <div v-if="errorMessage" class="alert alert-danger p-2 text-center small rounded-3" role="alert">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label fw-semibold small text-muted">Username</label>
          <input 
            type="text" 
            v-model="username" 
            id="username" 
            class="form-control" 
            placeholder="Enter username" 
            required 
          />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label fw-semibold small text-muted">Password</label>
          <input 
            type="password" 
            v-model="password" 
            id="password" 
            class="form-control" 
            placeholder="Enter password" 
            required 
          />
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2 mt-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>
      </form>

      <div class="text-center mt-4 border-top pt-3">
        <p class="mb-2 text-muted small">Don't have an account?</p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/register/student" class="text-primary text-decoration-none fw-semibold small">Student Register</router-link>
          <span class="text-muted">|</span>
          <router-link to="/register/company" class="text-primary text-decoration-none fw-semibold small">Company Register</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.loading = true
      try {
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password
        })

        localStorage.setItem('token', response.data.token)
        localStorage.setItem('role', response.data.role)
        localStorage.setItem('username', response.data.username)
        localStorage.setItem('profile_id', response.data.profile_id)

        if (response.data.role === 'admin') {
          this.$router.push('/admin-dashboard')
        } else if (response.data.role === 'company') {
          this.$router.push('/company-dashboard')
        } else if (response.data.role === 'student') {
          this.$router.push('/student-dashboard')
        }

      } catch (error) {
        this.errorMessage = error.response?.data?.message || "An unexpected error occurred."
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Mesh background gradient  */
.login-wrapper {
  background: radial-gradient(at 18% 18%, hsla(243, 75%, 97%, 1) 0px, transparent 50%),
              radial-gradient(at 97% 96%, hsla(243, 75%, 95%, 1) 0px, transparent 50%),
              #f8fafc;
}

.login-card {
  border-radius: 20px !important;
  border: 1px solid #e2e8f0 !important;
}

.logo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: var(--primary-color) !important;
}
</style>