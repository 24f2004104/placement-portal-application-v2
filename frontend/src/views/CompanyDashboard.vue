<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-primary">Company Dashboard</h2>
      <button @click="handleLogout" class="btn btn-outline-danger">Logout</button>
    </div>

    <!-- Alert messages -->
    <div v-if="alertMessage" class="alert alert-info text-center" role="alert">
      {{ alertMessage }}
    </div>

    <div class="row">
      <!-- Left column: To create a new placement drive -->
      <div class="col-md-5 mb-4">
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary">Create Placement Drive</h4>
          <form @submit.prevent="createDrive">
            <div class="mb-3">
              <label for="title" class="form-label">Job Title</label>
              <input type="text" v-model="newDrive.title" id="title" class="form-control" placeholder="e.g., Software Engineer" required />
            </div>

            <div class="mb-3">
              <label for="description" class="form-label">Job Description</label>
              <textarea v-model="newDrive.description" id="description" class="form-control" rows="3" placeholder="Describe the job role and responsibilities..." required></textarea>
            </div>

            <div class="mb-3">
              <label for="salary" class="form-label">Annual Salary (INR)</label>
              <input type="number" v-model="newDrive.salary" id="salary" class="form-control" placeholder="e.g., 600000" />
            </div>

            <div class="mb-3">
              <label for="criteria" class="form-label">Eligibility Criteria</label>
              <input type="text" v-model="newDrive.criteria" id="criteria" class="form-control" placeholder="e.g., CGPA > 8.0, CSE only" />
            </div>

            <div class="mb-3">
              <label for="deadline" class="form-label">Application Deadline</label>
              <input type="datetime-local" v-model="newDrive.deadline" id="deadline" class="form-control" required />
            </div>

            <button type="submit" class="btn btn-success w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Submit for Admin Approval
            </button>
          </form>
        </div>
      </div>

      <!-- Right column: list of posted Drives & applicant lists -->
      <div class="col-md-7 mb-4">
        <div class="card shadow-sm p-4 mb-4">
          <h4 class="mb-3 text-secondary">Your Posted Placement Drives</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Salary (INR)</th>
                  <th>Deadline Status</th>
                  <th>Admin Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td><strong>{{ drive.title }}</strong></td>
                  <td>{{ drive.salary || 'N/A' }}</td>
                  <td>{{ drive.deadline }}</td>
                  <td>
                    <span :class="drive.status === 'Approved' ? 'badge bg-success' : 'badge bg-warning text-dark'">
                      {{ drive.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button @click="viewApplicants(drive.id)" class="btn btn-sm btn-outline-primary">
                      Applicants
                    </button>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="5" class="text-center text-muted">You haven't posted any placement drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Student applicants panel (It appears when "Applicants" is clicked) -->
        <div class="card shadow-sm p-4" v-if="activeDriveTitle">
          <h4 class="mb-3 text-secondary">Applicants for: <span class="text-primary">{{ activeDriveTitle }}</span></h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Education</th>
                  <th>Skills</th>
                  <th>Status</th>
                  <th class="text-end">Update Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.application_id">
                  <td><strong>{{ app.student_name }}</strong></td>
                  <td>{{ app.education || 'N/A' }}</td>
                  <td>{{ app.skills || 'N/A' }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(app.status)">
                      {{ app.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <!-- Dropdown select menu to update candidate application status -->
                    <select 
                      class="form-select form-select-sm d-inline-block w-auto"
                      @change="updateApplicantStatus(app.application_id, $event.target.value)"
                      :value="app.status"
                    >
                      <option value="Applied">Applied</option>
                      <option value="Shortlisted">Shortlisted</option>
                      <option value="Selected">Selected</option>
                      <option value="Rejected">Rejected</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="applicants.length === 0">
                  <td colspan="5" class="text-center text-muted">No applications received yet.</td>
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
  name: 'CompanyDashboard',
  data() {
    return {
      companyId: null,
      drives: [],
      applicants: [],
      activeDriveId: null,
      activeDriveTitle: '',
      alertMessage: '',
      loading: false,
      newDrive: {
        title: '',
        description: '',
        salary: null,
        criteria: '',
        deadline: ''
      }
    }
  },
  mounted() {
    this.companyId = localStorage.getItem('profile_id')
    this.fetchDrives()
  },
  methods: {
    async fetchDrives() {
      try {
        const response = await axios.get(`/api/company/${this.companyId}/drives`)
        this.drives = response.data.drives
      } catch (error) {
        console.error("Error fetching company drives:", error)
      }
    },
    async createDrive() {
      this.loading = true
      try {
        // Converting the HTML datetime value (YYYY-MM-DDTHH:MM) to backend format (YYYY-MM-DD HH:MM)
        const formattedDeadline = this.newDrive.deadline.replace('T', ' ')
        
        const response = await axios.post('/api/company/drive', {
          company_id: this.companyId,
          title: this.newDrive.title,
          description: this.newDrive.description,
          salary: this.newDrive.salary,
          eligibility_criteria: this.newDrive.criteria,
          deadline: formattedDeadline
        })

        this.alertMessage = response.data.message
        this.fetchDrives() // Refreshing drives list
        
        // Resetting form fields
        this.newDrive = { title: '', description: '', salary: null, criteria: '', deadline: '' }
        setTimeout(() => { this.alertMessage = '' }, 3000)

      } catch (error) {
        if (error.response && error.response.data) {
          this.alertMessage = "Error: " + error.response.data.message
        } else {
          this.alertMessage = "Failed to create placement drive."
        }
      } finally {
        this.loading = false
      }
    },
    async viewApplicants(driveId) {
      try {
        const response = await axios.get(`/api/company/drive/${driveId}/applications`)
        this.applicants = response.data.applications
        this.activeDriveId = driveId
        this.activeDriveTitle = response.data.drive_title
      } catch (error) {
        console.error("Error fetching applicants:", error)
      }
    },
    async updateApplicantStatus(applicationId, newStatus) {
      try {
        const response = await axios.post(`/api/company/application/${applicationId}/status`, {
          status: newStatus
        })
        this.alertMessage = response.data.message
        this.viewApplicants(this.activeDriveId) // Refresh applicants list
        setTimeout(() => { this.alertMessage = '' }, 3000)
      } catch (error) {
        console.error("Error updating status:", error)
      }
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