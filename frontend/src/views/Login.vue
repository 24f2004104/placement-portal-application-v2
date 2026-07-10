<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="card p-4 shadow-sm" style="width: 100%; max-width: 400px;">
      <h3 class="text-center mb-4 text-primary">Placement Portal</h3>
      
      <!-- Error alert bar -->
      <div v-if="errorMessage" class="alert alert-danger p-2 text-center" role="alert">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
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
          <label for="password" class="form-label">Password</label>
          <input 
            type="password" 
            v-model="password" 
            id="password" 
            class="form-control" 
            placeholder="Enter password" 
            required 
          />
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Login
        </button>
      </form>

      <div class="text-center mt-3">
        <p class="mb-1 text-mutedSmall">Don't have an account?</p>
        <router-link to="/register/student" class="d-block text-decoration-none mb-1">Register as Student</router-link>
        <router-link to="/register/company" class="d-block text-decoration-none">Register as Company</router-link>
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
        // Sending our request to the backend (/api/login is proxied to our Flask app)
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password
        })

        // Storing secure token and session details in localStorage for authentication persistence 
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('role', response.data.role)
        localStorage.setItem('username', response.data.username)
        localStorage.setItem('profile_id', response.data.profile_id)

        // Logging the successful response to verify
        console.log("Login successful! Role:", response.data.role)

        // Redirecting user based on their specific role 
        if (response.data.role === 'admin') {
          this.$router.push('/admin-dashboard')
        } else if (response.data.role === 'company') {
          this.$router.push('/company-dashboard')
        } else if (response.data.role === 'student') {
          this.$router.push('/student-dashboard')
        }

      } catch (error) {
        // Extracting error message from backend 
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message
        } else {
          this.errorMessage = "An unexpected error occurred. Please try again."
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>