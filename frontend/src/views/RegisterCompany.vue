<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100 py-4">
    <div class="card p-4 shadow-sm" style="width: 100%; max-width: 500px;">
      <h3 class="text-center mb-4 text-primary">Company Registration</h3>

      <!-- Alert banners for feedback -->
      <div v-if="errorMessage" class="alert alert-danger p-2 text-center" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success p-2 text-center" role="alert">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input type="text" v-model="username" id="username" class="form-control" placeholder="Enter username" required />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" v-model="password" id="password" class="form-control" placeholder="Create password" required />
        </div>

        <hr />

        <div class="mb-3">
          <label for="company_name" class="form-label">Company Name</label>
          <input type="text" v-model="company_name" id="company_name" class="form-control" placeholder="Enter official company name" required />
        </div>

        <div class="mb-3">
          <label for="industry" class="form-label">Industry Sector</label>
          <input type="text" v-model="industry" id="industry" class="form-control" placeholder="e.g., Technology, Finance, Healthcare" />
        </div>

        <div class="mb-3">
          <label for="location" class="form-label">Location / Headquarters</label>
          <input type="text" v-model="location" id="location" class="form-control" placeholder="e.g., Mumbai, Bangalore, Remote" />
        </div>

        <div class="mb-3">
          <label for="hr_contact" class="form-label">HR Contact Email</label>
          <input type="email" v-model="hr_contact" id="hr_contact" class="form-control" placeholder="hr@company.com" />
        </div>

        <div class="mb-3">
          <label for="website" class="form-label">Company Website</label>
          <input type="url" v-model="website" id="website" class="form-control" placeholder="https://company.com" />
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Register as Company
        </button>
      </form>

      <div class="text-center mt-2">
        <span class="text-muted small">Already have an account? </span>
        <router-link to="/login" class="text-decoration-none">Login here</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterCompany',
  data() {
    return {
      username: '',
      password: '',
      company_name: '',
      industry: '',
      location: '',
      hr_contact: '',
      website: '',
      errorMessage: '',
      successMessage: '',
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true

      try {
        const response = await axios.post('/api/register/company', {
          username: this.username,
          password: this.password,
          company_name: this.company_name,
          industry: this.industry,
          location: this.location,
          hr_contact: this.hr_contact,
          website: this.website
        })

        this.successMessage = response.data.message
        
        // Waits 2.5 seconds (gives them time to read that they need Admin approval) and redirect
        setTimeout(() => {
          this.$router.push('/login')
        }, 2500)

      } catch (error) {
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