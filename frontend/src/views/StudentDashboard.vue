<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-primary">Student Dashboard</h2>
      <button @click="handleLogout" class="btn btn-outline-danger">Logout</button>
    </div>

    <!-- Alert messages -->
    <div v-if="alertMessage" :class="alertClass" role="alert">
      {{ alertMessage }}
    </div>

    <!-- Tab navigation buttons -->
    <ul class="nav nav-tabs mb-4" id="studentTab" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          @click="activeTab = 'drives'" 
          :class="{ active: activeTab === 'drives' }"
          type="button"
        >
          Active Placement Drives
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          @click="activeTab = 'applications'" 
          :class="{ active: activeTab === 'applications' }"
          type="button"
        >
          My Applications History
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          @click="activeTab = 'placements'" 
          :class="{ active: activeTab === 'placements' }"
          type="button"
        >
          My Placements
        </button>
      </li>
      <!-- Profile tab -->
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          @click="activeTab = 'profile'" 
          :class="{ active: activeTab === 'profile' }"
          type="button"
        >
          My Profile
        </button>
      </li>
    </ul>

    <!-- Tab content area -->
    <div class="tab-content" id="studentTabContent">
      
      <!-- TAB 1: ACTIVE PLACEMENT DRIVES -->
      <div v-if="activeTab === 'drives'">
        <div class="card shadow-sm p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="text-secondary mb-0">Explore Job Openings</h4>
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="fetchDrives" 
              class="form-control w-auto d-inline-block" 
              placeholder="Search by job title..."
            />
          </div>

          <div class="row g-3">
            <div class="col-md-6" v-for="drive in drives" :key="drive.id">
              <div class="card h-100 border-light shadow-sm">
                <div class="card-body">
                  <h5 class="card-title text-primary">{{ drive.title }}</h5>
                  <h6 class="card-subtitle mb-2 text-muted">{{ drive.company_name }}</h6>
                  <p class="card-text text-truncate-3">{{ drive.description }}</p>
                  
                  <ul class="list-unstyled mb-3 small text-muted">
                    <li><strong>Salary:</strong> {{ drive.salary ? 'INR ' + drive.salary : 'To be discussed' }}</li>
                    <li><strong>Eligibility:</strong> {{ drive.eligibility_criteria || 'Open to all' }}</li>
                    <li><strong>Deadline:</strong> {{ drive.deadline }}</li>
                  </ul>

                  <button 
                    @click="applyToJob(drive.id)" 
                    class="btn btn-sm btn-primary w-100"
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

      <!-- TAB 2: APPLICATION HISTORY -->
      <div v-if="activeTab === 'applications'">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary">Your Job Application Status</h4>
          <button @click="triggerCSVExport" class="btn btn-sm btn-outline-success mb-3" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
            Export Application History (CSV)
          </button>
          <div class="table-responsive">
            <table class="table align-middle">
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

      <!-- TAB 3: PLACEMENT RESULTS -->
      <div v-if="activeTab === 'placements'">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary">Successful Job Placements</h4>
          <div class="table-responsive">
            <table class="table align-middle">
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

      <!-- TAB4: MY PROFILE (Update profile) -->
      <div v-if="activeTab === 'profile'">
        <div class="card shadow-sm p-4" style="max-width: 600px; margin: 0 auto;">
          <h4 class="mb-3 text-secondary border-bottom pb-2">Manage Your Profile Details</h4>
          <form @submit.prevent="saveProfile">
            <div class="mb-3">
              <label for="profileName" class="form-label">Full Name</label>
              <input type="text" v-model="profile.name" id="profileName" class="form-control" required />
            </div>

            <div class="mb-3">
              <label for="profileEd" class="form-label">Education / Branch</label>
              <input type="text" v-model="profile.education" id="profileEd" class="form-control" />
            </div>

            <div class="mb-3">
              <label for="profileSkills" class="form-label">Key Skills</label>
              <input type="text" v-model="profile.skills" id="profileSkills" class="form-control" />
            </div>

            <div class="mb-3">
              <label for="profileExp" class="form-label">Experience</label>
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
        exportTaskID: null,
    }
  },
  mounted() {
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
     
        //Start polling the server every 1 second to see when the csv is ready
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
         
            //Automatically download the file to the browser 
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

<style>
/* Truncating descriptions to 3 lines cleanly for cards */
.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
</style>