<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-primary">Admin Dashboard</h2>
      <button @click="handleLogout" class="btn btn-outline-danger">Logout</button>
    </div>

    <!-- Metrics cards row -->
    <div class="row g-3 mb-4" v-if="metrics">
      <div class="col-md-3">
        <div class="card p-3 shadow-sm border-start border-primary border-4 text-center">
          <p class="text-muted mb-1">Total Students</p>
          <h3 class="mb-0">{{ metrics.total_students }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card p-3 shadow-sm border-start border-success border-4 text-center">
          <p class="text-muted mb-1">Total Companies</p>
          <h3 class="mb-0">{{ metrics.total_companies }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card p-3 shadow-sm border-start border-warning border-4 text-center">
          <p class="text-muted mb-1">Placement Drives</p>
          <h3 class="mb-0">{{ metrics.total_drives }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card p-3 shadow-sm border-start border-info border-4 text-center">
          <p class="text-muted mb-1">Total Applications</p>
          <h3 class="mb-0">{{ metrics.total_applications }}</h3>
        </div>
      </div>
    </div>

    <!-- Alert messages -->
    <div v-if="alertMessage" class="alert alert-info text-center" role="alert">
      {{ alertMessage }}
    </div>

    <div class="row">
      <!-- Companies approval and blacklisting panel -->
      <div class="col-md-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary">Registered Companies</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Location</th>
                  <th>Industry</th>
                  <th>Approval Status</th>
                  <th>Active Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in companies" :key="company.id">
                  <td><strong>{{ company.company_name }}</strong></td>
                  <td>{{ company.location || 'N/A' }}</td>
                  <td>{{ company.industry || 'N/A' }}</td>
                  <td>
                    <span :class="company.is_approved ? 'badge bg-success' : 'badge bg-warning text-dark'">
                      {{ company.is_approved ? 'Approved' : 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <span :class="company.is_active ? 'badge bg-info' : 'badge bg-secondary'">
                      {{ company.is_active ? 'Active' : 'Deactivated' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <!-- Approve Button (Shows only if company is pending) -->
                    <button 
                      v-if="!company.is_approved" 
                      @click="approveCompany(company.id)" 
                      class="btn btn-sm btn-success me-2"
                    >
                      Approve
                    </button>
                    <!-- Deactivate/Blacklist toggle button -->
                    <button 
                      @click="toggleUserStatus(company.user_id)" 
                      :class="company.is_active ? 'btn btn-sm btn-outline-danger' : 'btn btn-sm btn-outline-success'"
                    >
                      {{ company.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </td>
                </tr>
                <tr v-if="companies.length === 0">
                  <td colspan="6" class="text-center text-muted">No registered companies found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      metrics: null,
      companies: [],
      alertMessage: ''
    }
  },
  async mounted() {
    // Fetching metrics and user details on loading the component
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const metricsRes = await axios.get('/api/admin/metrics')
        this.metrics = metricsRes.data

        const usersRes = await axios.get('/api/admin/users')
        this.companies = usersRes.data.companies
      } catch (error) {
        console.error("Error fetching admin dashboard data:", error)
      }
    },
    async approveCompany(companyId) {
      try {
        const response = await axios.post(`/api/admin/company/${companyId}/approve`)
        this.alertMessage = response.data.message
        this.fetchData() // Refresh view
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } catch (error) {
        console.error("Error approving company:", error)
      }
    },
    async toggleUserStatus(userId) {
      try {
        const response = await axios.post(`/api/admin/user/${userId}/toggle-status`)
        this.alertMessage = response.data.message
        this.fetchData() // Refresh view
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } catch (error) {
        console.error("Error toggling user status:", error)
      }
    },
    handleLogout() {
      // Clearing all session details on logout
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>