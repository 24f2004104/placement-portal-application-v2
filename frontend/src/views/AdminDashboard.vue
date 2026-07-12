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
      <!-- 1. Registered companies panel -->
      <div class="col-md-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary border-bottom pb-2">Registered Companies Management</h4>
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
                    <button 
                      v-if="!company.is_approved" 
                      @click="approveCompany(company.id)" 
                      class="btn btn-sm btn-success me-2"
                    >
                      Approve
                    </button>
                    <button 
                      @click="toggleUserStatus(company.user_id)" 
                      :class="company.is_active ? 'btn btn-sm btn-outline-warning me-2' : 'btn btn-sm btn-outline-success me-2'"
                    >
                      {{ company.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button 
                      @click="removeCompany(company.id)" 
                      class="btn btn-sm btn-outline-danger"
                    >
                      Remove
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

      <!-- 2. Placement drives management panel -->
      <div class="col-md-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary border-bottom pb-2">Placement Drives Management</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Salary Package</th>
                  <th>Deadline</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td><strong>{{ drive.title }}</strong></td>
                  <td>{{ drive.company_name }}</td>
                  <td>{{ drive.salary ? 'INR ' + drive.salary : 'N/A' }}</td>
                  <td>{{ drive.deadline }}</td>
                  <td>
                    <span :class="getDriveStatusBadge(drive.status)">
                      {{ drive.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button 
                      v-if="drive.status === 'Pending' || drive.status === 'Rejected'" 
                      @click="updateDriveStatus(drive.id, 'Approved')" 
                      class="btn btn-sm btn-success me-2"
                    >
                      Approve
                    </button>
                    <button 
                      v-if="drive.status === 'Pending' || drive.status === 'Approved'" 
                      @click="updateDriveStatus(drive.id, 'Rejected')" 
                      class="btn btn-sm btn-warning me-2"
                    >
                      Reject
                    </button>
                    <button 
                      @click="removeDrive(drive.id)" 
                      class="btn btn-sm btn-outline-danger"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="6" class="text-center text-muted">No placement drives found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 3. Student applications management log  -->
      <div class="col-md-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary border-bottom pb-2">Student Applications Tracking Log</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Education</th>
                  <th>Target Company</th>
                  <th>Job Title</th>
                  <th>Applied Date</th>
                  <th>Current Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.id">
                  <td><strong>{{ app.student_name }}</strong></td>
                  <td>{{ app.education || 'N/A' }}</td>
                  <td>{{ app.company_name }}</td>
                  <td>{{ app.drive_title }}</td>
                  <td>{{ app.applied_date }}</td>
                  <td>
                    <span :class="getApplicationStatusBadge(app.status)">
                      {{ app.status }}
                    </span>
                  </td>
                </tr>
                <tr v-if="applications.length === 0">
                  <td colspan="6" class="text-center text-muted">No job applications submitted yet in the system.</td>
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
      drives: [],
      applications: [], // Applications log array
      alertMessage: ''
    }
  },
  async mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const metricsRes = await axios.get('/api/admin/metrics')
        this.metrics = metricsRes.data

        const usersRes = await axios.get('/api/admin/users')
        this.companies = usersRes.data.companies

        const drivesRes = await axios.get('/api/admin/drives')
        this.drives = drivesRes.data.drives

        // Fetching applications log 
        const appsRes = await axios.get('/api/admin/applications')
        this.applications = appsRes.data.applications
      } catch (error) {
        console.error("Error fetching admin dashboard data:", error)
      }
    },
    async approveCompany(companyId) {
      try {
        const response = await axios.post(`/api/admin/company/${companyId}/approve`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error approving company:", error)
      }
    },
    async toggleUserStatus(userId) {
      try {
        const response = await axios.post(`/api/admin/user/${userId}/toggle-status`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error toggling user status:", error)
      }
    },
    async removeCompany(companyId) {
      if (!confirm("Are you sure you want to completely remove this company and all its login credentials?")) return
      try {
        const response = await axios.delete(`/api/admin/company/${companyId}`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error removing company:", error)
      }
    },
    async updateDriveStatus(driveId, status) {
      try {
        const response = await axios.post(`/api/admin/drive/${driveId}/status`, { status })
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error updating drive status:", error)
      }
    },
    async removeDrive(driveId) {
      if (!confirm("Are you sure you want to completely remove this placement drive?")) return
      try {
        const response = await axios.delete(`/api/admin/drive/${driveId}`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error removing drive:", error)
      }
    },
    getDriveStatusBadge(status) {
      if (status === 'Approved') return 'badge bg-success'
      if (status === 'Rejected') return 'badge bg-danger'
      return 'badge bg-warning text-dark'
    },
    getApplicationStatusBadge(status) {
      if (status === 'Selected') return 'badge bg-success'
      if (status === 'Shortlisted') return 'badge bg-info'
      if (status === 'Rejected') return 'badge bg-danger'
      return 'badge bg-secondary'
    },
    showAlert(msg) {
      this.alertMessage = msg
      setTimeout(() => { this.alertMessage = '' }, 3000)
    },
    handleLogout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>