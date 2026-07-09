<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100 py-4">
    <div class="card p-4 shadow-sm" style="width: 100%; max-width: 500px;">
      <h3 class="text-center mb-4 text-primary">Student Registration</h3>

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
          <label for="name" class="form-label">Full Name</label>
          <input type="text" v-model="name" id="name" class="form-control" placeholder="Enter your full name" required />
        </div>

        <div class="mb-3">
          <label for="education" class="form-label">Education / Branch</label>
          <input type="text" v-model="education" id="education" class="form-control" placeholder="e.g., B.Tech Computer Science" />
        </div>

        <div class="mb-3">
          <label for="skills" class="form-label">Key Skills</label>
          <input type="text" v-model="skills" id="skills" class="form-control" placeholder="e.g., Python, SQL, VueJS" />
        </div>

        <div class="mb-3">
          <label for="experience" class="form-label">Experience (Optional)</label>
          <textarea v-model="experience" id="experience" class="form-control" rows="2" placeholder="Describe past internships/projects"></textarea>
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Register as Student
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
  name: 'RegisterStudent',
  data() {
    return {
      username: '',
      password: '',
      name: '',
      education: '',
      skills: '',
      experience: '',
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
        const response = await axios.post('/api/register/student', {
          username: this.username,
          password: this.password,
          name: this.name,
          education: this.education,
          skills: this.skills,
          experience: this.experience
        })

        this.successMessage = response.data.message
        
        // Waits 1.5 seconds and then redirect to login page
        setTimeout(() => {
          this.$router.push('/login')
        }, 1500)

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