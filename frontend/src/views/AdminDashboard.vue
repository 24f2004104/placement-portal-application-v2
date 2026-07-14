<template>
  <div class="container py-4">
    <!-- Navigation bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom rounded-3 mb-4 py-3 px-3 shadow-sm">
      <div class="container-fluid">
        <span class="navbar-brand fw-bold text-primary fs-4">Placement Portal<span class="text-secondary">.v2</span></span>
        
        <!-- Avatar dropdown menu -->
        <div class="dropdown">
          <div class="d-flex align-items-center role-dropdown" @click="dropdownOpen = !dropdownOpen" style="cursor: pointer;">
            <div class="me-3 text-end d-none d-sm-block">
              <div class="fw-semibold small text-muted">Welcome!</div>
              <div class="text-primary fw-bold small text-capitalize">{{ username }}</div>
            </div>
            <div class="avatar-badge bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 40px; height: 40px; text-transform: uppercase;">
              {{ username ? username.charAt(0) : 'A' }}
            </div>
          </div>
          <ul class="dropdown-menu dropdown-menu-end shadow border-0 p-2 mt-2 show" style="display: block;" v-if="dropdownOpen">
            <li>
              <button @click="handleLogout" class="dropdown-item text-danger fw-semibold rounded-2 py-2">
                Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Metrics cards row -->
    <div class="row g-3 mb-4" v-if="metrics">
      <div class="col-6 col-md-3">
        <div class="card p-3 shadow-sm border-start border-primary border-4 text-center">
          <p class="text-muted small mb-1">Total Students</p>
          <h3 class="mb-0 fw-bold text-primary">{{ metrics.total_students }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card p-3 shadow-sm border-start border-success border-4 text-center">
          <p class="text-muted small mb-1">Total Companies</p>
          <h3 class="mb-0 fw-bold text-success">{{ metrics.total_companies }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card p-3 shadow-sm border-start border-warning border-4 text-center">
          <p class="text-muted small mb-1">Placement Drives</p>
          <h3 class="mb-0 fw-bold text-warning">{{ metrics.total_drives }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card p-3 shadow-sm border-start border-info border-4 text-center">
          <p class="text-muted small mb-1">Total Applications</p>
          <h3 class="mb-0 fw-bold text-info">{{ metrics.total_applications }}</h3>
        </div>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alertMessage" class="alert alert-info text-center rounded-3 p-2 mb-3" role="alert">
      {{ alertMessage }}
    </div>

    <!-- Management tables -->
    <div class="row">
      <!-- 1. Registered students table -->
      <div class="col-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-dark fw-bold border-bottom pb-2" style="font-size: 1.25rem;">Registered Students Management</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Education</th>
                  <th>Key Skills</th>
                  <th>Account Status</th>         
                  <th class="text-end">Remove</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in students" :key="student.id">
                  <td><strong>{{ student.name }}</strong></td>
                  <td>{{ student.education || 'N/A' }}</td>
                  <td>{{ student.skills || 'N/A' }}</td>
                  <td>
                    <select 
                      class="form-select form-select-sm badge-select text-white text-center"
                      :class="student.is_active ? 'bg-info' : 'bg-danger'"
                      @change="toggleUserStatus(student.user_id)"
                    >
                      <option value="Active" :selected="student.is_active">Active</option>
                      <option value="Deactivated" :selected="!student.is_active">Deactivated</option>
                    </select>
                  </td>
                  <td class="text-end">
                    <button @click="removeStudent(student.id)" class="btn btn-sm btn-outline-danger">Remove</button>
                  </td>
                </tr>
                <tr v-if="students.length === 0">
                  <td colspan="5" class="text-center text-muted">No registered students found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 2. Registered companies table -->
      <div class="col-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-dark fw-bold border-bottom pb-2" style="font-size: 1.25rem;">Registered Companies Management</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Location</th>
                  <th>Industry</th>
                  <th>Registration Approval</th> 
                  <th>Account Status</th>         
                  <th class="text-end">Remove</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in companies" :key="company.id">
                  <td><strong>{{ company.company_name }}</strong></td>
                  <td>{{ company.location || 'N/A' }}</td>
                  <td>{{ company.industry || 'N/A' }}</td>
                  <td>
                    <!-- If pending, show the interactive dropdown. Once approved, show a clean static badge -->
                    <select 
                      v-if="!company.is_approved"
                      class="form-select form-select-sm badge-select text-center bg-warning text-dark"
                      @change="approveCompany(company.id)"
                    >
                      <option value="Pending" selected>Pending</option>
                      <option value="Approved">Approved</option>
                    </select>
                    <span v-else class="badge bg-success">Approved</span>
                  </td>
                  <td>
                    <select 
                      class="form-select form-select-sm badge-select text-white text-center"
                      :class="company.is_active ? 'bg-info' : 'bg-danger'"
                      @change="toggleUserStatus(company.user_id)"
                    >
                      <option value="Active" :selected="company.is_active">Active</option>
                      <option value="Deactivated" :selected="!company.is_active">Deactivated</option>
                    </select>
                  </td>
                  <td class="text-end">
                    <button @click="removeCompany(company.id)" class="btn btn-sm btn-outline-danger">Remove</button>
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

      <!-- 3. Placement drives management table -->
      <div class="col-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-dark fw-bold border-bottom pb-2" style="font-size: 1.25rem;">Placement Drives Management</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Salary Package</th>
                  <th>Deadline</th>
                  <th>Drive Approval Status</th> 
                  <th class="text-end">Remove</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td><strong>{{ drive.title }}</strong></td>
                  <td>{{ drive.company_name }}</td>
                  <td>{{ drive.salary ? 'INR ' + drive.salary : 'N/A' }}</td>
                  <td>{{ drive.deadline }}</td>
                  <td>
                    <select 
                      class="form-select form-select-sm badge-select text-center"
                      :class="getDriveStatusBadgeClass(drive.status)"
                      @change="updateDriveStatus(drive.id, $event.target.value)"
                    >
                      <option value="Pending" :selected="drive.status === 'Pending'">Pending</option>
                      <option value="Approved" :selected="drive.status === 'Approved'">Approved</option>
                      <option value="Rejected" :selected="drive.status === 'Rejected'">Rejected</option>
                      <option value="Closed" :selected="drive.status === 'Closed'">Closed</option>
                    </select>
                  </td>
                  <td class="text-end">
                    <button @click="removeDrive(drive.id)" class="btn btn-sm btn-outline-danger">Remove</button>
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

      <!-- 4. Student applications tracking log -->
      <div class="col-12 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-dark fw-bold border-bottom pb-2" style="font-size: 1.25rem;">Student Applications Tracking Log</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Education</th>
                  <th>Target Company</th>
                  <th>Job Title</th>
                  <th>Applied Date</th>
                  <th>Application Status</th> 
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
                  <td colspan="6" class="text-center text-muted">No job applications submitted yet.</td>
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
      username: '',
      dropdownOpen: false, 
      metrics: null,
      students: [],
      companies: [],
      drives: [],
      applications: [],
      alertMessage: ''
    }
  },
  async mounted() {
    this.username = localStorage.getItem('username') || 'Admin'
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const metricsRes = await axios.get('/api/admin/metrics')
        this.metrics = metricsRes.data

        const usersRes = await axios.get('/api/admin/users')
        this.companies = usersRes.data.companies
        this.students = usersRes.data.students 

        const drivesRes = await axios.get('/api/admin/drives')
        this.drives = drivesRes.data.drives

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
      if (!confirm("Are you sure you want to completely remove this company and all its credentials?")) return
      try {
        const response = await axios.delete(`/api/admin/company/${companyId}`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error removing company:", error)
      }
    },
    async removeStudent(studentId) {
      if (!confirm("Are you sure you want to completely remove this student profile?")) return
      try {
        const response = await axios.delete(`/api/admin/student/${studentId}`)
        this.showAlert(response.data.message)
        this.fetchData()
      } catch (error) {
        console.error("Error removing student:", error)
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
    getDriveStatusBadgeClass(status) {
      if (status === 'Approved') return 'bg-success text-white'
      if (status === 'Rejected') return 'bg-danger text-white'
      if (status === 'Closed') return 'bg-secondary text-white' 
      return 'bg-warning text-dark'
    },
    getDriveStatusBadge(status) {
      if (status === 'Approved') return 'badge bg-success'
      if (status === 'Rejected') return 'badge bg-danger'
      if (status === 'Closed') return 'badge bg-secondary' 
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

<style scoped>
.badge-select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e");
}
</style>