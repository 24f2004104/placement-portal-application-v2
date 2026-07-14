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
              {{ username ? username.charAt(0) : 'S' }}
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

    <!-- Alert Messages -->
    <div v-if="alertMessage" :class="alertClass" role="alert">
      {{ alertMessage }}
    </div>

    <!-- Tab navigation -->
    <div class="nav-container mb-4">
      <ul class="nav nav-tabs border-bottom-0 d-flex flex-wrap text-center" id="studentTab" role="tablist">
        <li class="nav-item tab-item" role="presentation">
          <button class="nav-link py-3 w-100" @click="activeTab = 'drives'" :class="{ active: activeTab === 'drives' }" type="button">Active Placement Drives</button>
        </li>
        <li class="nav-item tab-item" role="presentation">
          <button class="nav-link py-3 w-100" @click="activeTab = 'applications'" :class="{ active: activeTab === 'applications' }" type="button">My Applications History</button>
        </li>
        <li class="nav-item tab-item" role="presentation">
          <button class="nav-link py-3 w-100" @click="activeTab = 'placements'" :class="{ active: activeTab === 'placements' }" type="button">My Placements</button>
        </li>
        <li class="nav-item tab-item" role="presentation">
          <button class="nav-link py-3 w-100" @click="activeTab = 'profile'" :class="{ active: activeTab === 'profile' }" type="button">My Profile</button>
        </li>
      </ul>
    </div>

    <!-- Tab content -->
    <div class="tab-content" id="studentTabContent">
      
      <!-- Tab1: Active placement drives -->
      <div v-if="activeTab === 'drives'">
        <div class="card shadow-sm p-4">
          <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3 mb-3">
            <h4 class="text-dark fw-bold mb-0" style="font-size: 1.25rem;">Explore Job Openings</h4>
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="fetchDrives" 
              class="form-control w-auto" 
              placeholder="Search by job title..."
            />
          </div>

          <div class="row g-3">
            <div class="col-md-6" v-for="drive in drives" :key="drive.id">
              <div class="card h-100 border-light shadow-sm interactive-card">
                <div class="card-body d-flex flex-column justify-content-between">
                  <div>
                    <h5 class="card-title text-primary fw-bold">{{ drive.title }}</h5>
                    <h6 class="card-subtitle mb-2 text-muted fw-semibold">{{ drive.company_name }}</h6>
                    <p class="card-text text-truncate-3 small text-muted">{{ drive.description }}</p>
                    
                    <ul class="list-unstyled mb-3 small text-muted">
                      <li><strong>Salary Package:</strong> {{ drive.salary ? 'INR ' + drive.salary : 'To be discussed' }}</li>
                      <li><strong>Eligibility:</strong> {{ drive.eligibility_criteria || 'Open to all' }}</li>
                      <li><strong>Deadline:</strong> {{ drive.deadline }}</li>
                    </ul>
                  </div>

                  <button 
                    @click="applyToJob(drive.id)" 
                    class="btn btn-sm btn-primary w-100 mt-2"
                    :disabled="applying"
                  >
                    Apply Now
                  </button>
                </div>
              </div>
            </div>
            <div class="col-12 text-center text-muted py-4" v-if="drives.length === 0">
              No active placement drives found.
            </div>
          </div>
        </div>
      </div>

      <!-- Tab2: Application history -->
      <div v-if="activeTab === 'applications'">
        <div class="card shadow-sm p-4">
          <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3 mb-3">
            <h4 class="text-dark fw-bold mb-0" style="font-size: 1.25rem;">Your Job Application Status</h4>
            <button @click="triggerCSVExport" class="btn btn-sm btn-outline-success align-self-start align-self-sm-center" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
              Export Application History (CSV)
            </button>
          </div>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Applied Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.application_id">
                  <td><strong>{{ app.drive_title }}</strong></td>
                  <td>{{ app.company_name }}</td>
                  <td>{{ app.applied_date }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(app.status)">
                      {{ app.status }}
                    </span>
                  </td>
                </tr>
                <tr v-if="applications.length === 0">
                  <td colspan="4" class="text-center text-muted">You haven't applied to any drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab3: Placement results -->
      <div v-if="activeTab === 'placements'">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary fw-bold">Successful Job Placements</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Salary Package (INR)</th>
                  <th>Joining Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in placements" :key="p.placement_id">
                  <td><strong class="text-success">{{ p.job_title }}</strong></td>
                  <td>{{ p.company_name }}</td>
                  <td>{{ p.salary }}</td>
                  <td>{{ p.joining_date }}</td>
                </tr>
                <tr v-if="placements.length === 0">
                  <td colspan="4" class="text-center text-muted">No placement records found. Keep applying!</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab4: My profile-->
      <div v-if="activeTab === 'profile'">
        <div class="card shadow-sm p-4" style="max-width: 600px; margin: 0 auto;">
          <h4 class="mb-3 text-secondary border-bottom pb-2 fw-bold">Manage Your Profile Details</h4>
          <form @submit.prevent="saveProfile">
            <div class="mb-3">
              <label for="profileName" class="form-label fw-semibold text-muted small">Full Name</label>
              <input type="text" v-model="profile.name" id="profileName" class="form-control" required />
            </div>

            <div class="mb-3">
              <label for="profileEd" class="form-label fw-semibold text-muted small">Education / Branch</label>
              <input type="text" v-model="profile.education" id="profileEd" class="form-control" />
            </div>

            <div class="mb-3">
              <label for="profileSkills" class="form-label fw-semibold text-muted small">Key Skills</label>
              <input type="text" v-model="profile.skills" id="profileSkills" class="form-control" />
            </div>

            <div class="mb-3">
              <label for="profileExp" class="form-label fw-semibold text-muted small">Experience</label>
              <textarea v-model="profile.experience" id="profileExp" class="form-control" rows="3"></textarea>
            </div>

            <button type="submit" class="btn btn-success w-100" :disabled="savingProfile">
              <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
              Save Changes
            </button>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      username: '',
      dropdownOpen: false, 
      studentId: null,
      activeTab: 'drives',
      searchQuery: '',
      drives: [],
      applications: [],
      placements: [],
      profile: {
        name: '',
        education: '',
        skills: '',
        experience: ''
      },
      alertMessage: '',
      alertClass: 'alert alert-info text-center',
      applying: false,
      savingProfile: false,
      exporting: false,
      exportTaskID: null
    }
  },
  mounted() {
    this.username = localStorage.getItem('username') || 'Student'
    this.studentId = localStorage.getItem('profile_id')
    this.fetchDrives()
    this.fetchApplications()
    this.fetchPlacements()
    this.fetchProfile()
  },
  methods: {
    async fetchDrives() {
      try {
        const response = await axios.get(`/api/student/drives?q=${this.searchQuery}`)
        this.drives = response.data.drives
      } catch (error) {
        console.error("Error fetching approved drives:", error)
      }
    },
    async fetchApplications() {
      try {
        const response = await axios.get(`/api/student/${this.studentId}/applications`)
        this.applications = response.data.applications
      } catch (error) {
        console.error("Error fetching applications:", error)
      }
    },
    async fetchPlacements() {
      try {
        const response = await axios.get(`/api/student/${this.studentId}/placements`)
        this.placements = response.data.placements
      } catch (error) {
        console.error("Error fetching placements:", error)
      }
    },
    async fetchProfile() {
      try {
        const response = await axios.get(`/api/student/${this.studentId}/profile`)
        this.profile = response.data
      } catch (error) {
        console.error("Error fetching profile details:", error)
      }
    },
    async saveProfile() {
      this.savingProfile = true
      this.alertMessage = ''
      try {
        const response = await axios.put(`/api/student/${this.studentId}/profile`, this.profile)
        this.alertClass = 'alert alert-success text-center'
        this.alertMessage = response.data.message
        this.fetchProfile()
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } catch (error) {
        this.alertClass = 'alert alert-danger text-center'
        this.alertMessage = "Failed to update profile details."
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } finally {
        this.savingProfile = false
      }
    },
    async applyToJob(driveId) {
      this.applying = true
      this.alertMessage = ''
      try {
        const response = await axios.post('/api/student/apply', {
          student_id: this.studentId,
          drive_id: driveId
        })
        
        this.alertClass = 'alert alert-success text-center'
        this.alertMessage = response.data.message
        this.fetchApplications()
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } catch (error) {
        this.alertClass = 'alert alert-danger text-center'
        if (error.response && error.response.data) {
          this.alertMessage = error.response.data.message
        } else {
          this.alertMessage = "Failed to submit application."
        }
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } finally {
        this.applying = false
      }
    },
    async triggerCSVExport() {
      this.exporting = true
      this.alertMessage = ''
      try {
        const response = await axios.post(`/api/student/${this.studentId}/export-csv`)
        this.exportTaskID = response.data.task_id
        this.alertClass = 'alert alert-info text-center'
        this.alertMessage = response.data.message
        this.pollTaskStatus()
      } catch (error) {
        this.alertClass = 'alert alert-danger text-center'
        this.alertMessage = "Failed to start export job."
        this.exporting = false
      }
    },
    async pollTaskStatus() {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/task-status/${this.exportTaskID}`)
          
          if (response.data.state === 'SUCCESS') {
            clearInterval(interval)
            this.exporting = false
            this.alertClass = 'alert alert-success text-center'
            this.alertMessage = "CSV exported successfully! Downloading..."
            
            window.open(response.data.result, '_blank')
            setTimeout(() => { this.alertMessage = '' }, 3000)
          } else if (response.data.state === 'FAILURE') {
            clearInterval(interval)
            this.exporting = false
            this.alertClass = 'alert alert-danger text-center'
            this.alertMessage = "Background export failed."
          }
        } catch (error) {
          clearInterval(interval)
          this.exporting = false
        }
      }, 1000)
    },
    getStatusBadgeClass(status) {
      if (status === 'Selected') return 'badge bg-success'
      if (status === 'Shortlisted') return 'badge bg-info'
      if (status === 'Rejected') return 'badge bg-danger'
      return 'badge bg-secondary'
    },
    handleLogout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>

.tab-item {
  width: 25%; 
}

@media (max-width: 992px) {
  .tab-item {
    width: 50%; 
  }
}

@media (max-width: 576px) {
  .tab-item {
    width: 100%; 
  }
}

/* Truncate descriptions cleanly for cards */
.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
</style>