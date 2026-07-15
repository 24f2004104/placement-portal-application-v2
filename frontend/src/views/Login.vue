<template>
  <div class="login-wrapper d-flex justify-content-center align-items-center min-vh-100">
    <div class="card p-5 shadow-lg border-0 login-card" style="width: 100%; max-width: 440px;">
      
      <!-- Header -->
      <div class="text-center mb-4">
        <div class="logo-icon bg-primary text-white rounded-3 mx-auto mb-2 d-flex align-items-center justify-content-center">
          <span class="fw-bold fs-4">P</span>
        </div>
        <h3 class="fw-bold text-dark mb-1">{{ resetMode ? 'Reset Password' : 'Placement Portal' }}</h3>
        <p class="text-muted small">{{ resetMode ? 'Create a new login password' : 'Access your account and dashboard' }}</p>
      </div>
      
      <!-- Sticky alert banner -->
      <div v-if="errorMessage" class="alert alert-danger p-2 text-center small rounded-3" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success p-2 text-center small rounded-3" role="alert">
        {{ successMessage }}
      </div>

      <!-- Sign in form -->
      <form v-if="!resetMode" @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label fw-semibold small text-muted">Username</label>
          <input type="text" v-model="username" id="username" class="form-control" placeholder="Enter username" required />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label fw-semibold small text-muted">Password</label>
          <input type="password" v-model="password" id="password" class="form-control" placeholder="Enter password" required />
        </div>

        <!-- Forgot password -->
        <div class="text-end mb-3">
          <a href="#" @click.prevent="enableResetMode" class="text-primary text-decoration-none small fw-semibold">Forgot Password?</a>
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>
      </form>

      <!-- Password reset form -->
      <form v-else @submit.prevent="handleReset">
        <div class="mb-3">
          <label for="resetUsername" class="form-label fw-semibold small text-muted">Confirm Username</label>
          <input type="text" v-model="username" id="resetUsername" class="form-control" placeholder="Enter username" required />
        </div>

        <div class="mb-3">
          <label for="newPassword" class="form-label fw-semibold small text-muted">New Password</label>
          <input type="password" v-model="newPassword" id="newPassword" class="form-control" placeholder="Create new password" required />
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2 mb-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Update Password
        </button>

        <button type="button" @click="cancelReset" class="btn btn-outline-secondary w-100 py-2">
          Cancel
        </button>
      </form>

      <div class="text-center mt-4 border-top pt-3" v-if="!resetMode">
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
      newPassword: '', 
      errorMessage: '',
      successMessage: '',
      loading: false,
      resetMode: false  
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.successMessage = ''
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
    },
    async handleReset() {
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true
      try {
        const response = await axios.post('/api/reset-password', {
          username: this.username,
          new_password: this.newPassword
        })

        this.successMessage = response.data.message
        
        // Waits 1.5 seconds and returns to standard login mode
        setTimeout(() => {
          this.cancelReset()
        }, 1500)

      } catch (error) {
        this.errorMessage = error.response?.data?.message || "Failed to reset password."
      } finally {
        this.loading = false
      }
    },
    enableResetMode() {
      this.resetMode = true
      this.errorMessage = ''
      this.successMessage = ''
      this.username = ''
      this.password = ''
      this.newPassword = ''
    },
    cancelReset() {
      this.resetMode = false
      this.errorMessage = ''
      this.successMessage = ''
      this.username = ''
      this.password = ''
      this.newPassword = ''
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 40%, #f1f5f9 100%);
}

.login-card {
  border-radius: 20px !important;
  border: 1px solid #cbd5e1 !important;
}

.logo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: var(--primary) !important;
}
</style>