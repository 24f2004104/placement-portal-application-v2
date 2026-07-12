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
      <!-- Left column: Dual-mode form -->
      <div class="col-md-5 mb-4">
        <div class="card shadow-sm p-4 border-primary">
          <h4 class="mb-3 text-secondary">{{ editMode ? 'Modify Placement Drive' : 'Create Placement Drive' }}</h4>
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="title" class="form-label">Job Title</label>
              <input type="text" v-model="newDrive.title" id="title" class="form-control" placeholder="e.g., Software Engineer" required />
            </div>

            <div class="mb-3">
              <label for="description" class="form-label">Job Description</label>
              <textarea v-model="newDrive.description" id="description" class="form-control" rows="3" placeholder="Describe the job role..." required></textarea>
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

            <div class="mb-3" v-if="editMode">
              <label for="status" class="form-label">Status</label>
              <select v-model="newDrive.status" id="status" class="form-select">
                <option value="Pending">Pending Admin Approval</option>
                <option value="Approved">Approved / Active</option>
                <option value="Closed">Closed</option>
              </select>
            </div>

            <button type="submit" class="btn btn-success w-100 mb-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ editMode ? 'Save Modifications' : 'Submit for Admin Approval' }}
            </button>
            <button v-if="editMode" type="button" @click="cancelEdit" class="btn btn-outline-secondary w-100">
              Cancel Edit
            </button>
          </form>
        </div>
      </div>

      <!-- Right column: Lists -->
      <div class="col-md-7 mb-4">
        <div class="card shadow-sm p-4 mb-4">
          <h4 class="mb-3 text-secondary">Your Posted Placement Drives</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Salary (INR)</th>
                  <th>Admin Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td><strong>{{ drive.title }}</strong></td>
                  <td>{{ drive.salary || 'N/A' }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(drive.status)">
                      {{ drive.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button @click="viewApplicants(drive.id)" class="btn btn-sm btn-outline-primary me-1">
                      Applicants
                    </button>
                    <button @click="enableEditMode(drive)" class="btn btn-sm btn-outline-secondary me-1">
                      Edit
                    </button>
                    <button @click="deleteDrive(drive.id)" class="btn btn-sm btn-outline-danger">
                      Delete
                    </button>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="4" class="text-center text-muted">You haven't posted any placement drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Student applicants sub-panel -->
        <div class="card shadow-sm p-4 mb-4" v-if="activeDriveTitle">
          <h4 class="mb-3 text-secondary">Applicants for: <span class="text-primary">{{ activeDriveTitle }}</span></h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Education</th>
                  <th>Status</th>
                  <th class="text-end">Update Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.application_id">
                  <td><strong>{{ app.student_name }}</strong></td>
                  <td>{{ app.education || 'N/A' }}</td>
                  <td>
                    <span :class="getAppStatusBadgeClass(app.status)">
                      {{ app.status }}
                    </span>
                  </td>
                  <td class="text-end">
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
                  <td colspan="4" class="text-center text-muted">No applications received yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Successful placements & joining date management -->
        <div class="card shadow-sm p-4">
          <h4 class="mb-3 text-secondary border-bottom pb-2">Successful Placements & Joining Dates</h4>
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Selected Student</th>
                  <th>Job Position</th>
                  <th>Salary Package</th>
                  <th>Joining Date</th>
                  <th class="text-end">Update Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in placements" :key="p.id">
                  <td><strong>{{ p.student_name }}</strong></td>
                  <td>{{ p.job_title }}</td>
                  <td>{{ p.salary ? 'INR ' + p.salary : 'N/A' }}</td>
                  <td>
                    <input 
                      type="date" 
                      class="form-control form-control-sm"
                      v-model="p.joining_date"
                    />
                  </td>
                  <td class="text-end">
                    <button 
                      @click="saveJoiningDate(p.id, p.joining_date)" 
                      class="btn btn-sm btn-success"
                    >
                      Save Date
                    </button>
                  </td>
                </tr>
                <tr v-if="placements.length === 0">
                  <td colspan="5" class="text-center text-muted">No hired placement records found. Select candidates to hire them!</td>
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
      placements: [], // Placements array
      activeDriveId: null,
      activeDriveTitle: '',
      alertMessage: '',
      loading: false,
      editMode: false,
      editingDriveId: null,
      newDrive: {
        title: '',
        description: '',
        salary: null,
        criteria: '',
        deadline: '',
        status: 'Pending'
      }
    }
  },
  mounted() {
    this.companyId = localStorage.getItem('profile_id')
    this.fetchDrives()
    this.fetchPlacements()
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
    async fetchPlacements() {
      try {
        const response = await axios.get(`/api/company/${this.companyId}/placements`)
        this.placements = response.data.placements
      } catch (error) {
        console.error("Error fetching company placements:", error)
      }
    },
    handleSubmit() {
      if (this.editMode) {
        this.saveEdit()
      } else {
        this.createDrive()
      }
    },
    async createDrive() {
      this.loading = true
      try {
        const formattedDeadline = this.newDrive.deadline.replace('T', ' ')
        const response = await axios.post('/api/company/drive', {
          company_id: this.companyId,
          title: this.newDrive.title,
          description: this.newDrive.description,
          salary: this.newDrive.salary,
          eligibility_criteria: this.newDrive.criteria,
          deadline: formattedDeadline
        })

        this.showAlert(response.data.message)
        this.fetchDrives()
        this.resetForm()
      } catch (error) {
        this.showAlert(error.response?.data?.message || "Failed to create drive.")
      } finally {
        this.loading = false
      }
    },
    enableEditMode(drive) {
      this.editMode = true
      this.editingDriveId = drive.id
      this.newDrive = {
        title: drive.title,
        description: drive.description || '',
        salary: drive.salary,
        criteria: drive.eligibility_criteria || '',
        deadline: drive.deadline.replace(' ', 'T'),
        status: drive.status
      }
      const matched = this.drives.find(d => d.id === drive.id)
      if (matched) this.newDrive.description = matched.description
    },
    async saveEdit() {
      this.loading = true
      try {
        const formattedDeadline = this.newDrive.deadline.replace('T', ' ')
        const response = await axios.put(`/api/company/drive/${this.editingDriveId}`, {
          title: this.newDrive.title,
          description: this.newDrive.description,
          salary: this.newDrive.salary,
          eligibility_criteria: this.newDrive.criteria,
          deadline: formattedDeadline,
          status: this.newDrive.status
        })

        this.showAlert(response.data.message)
        this.fetchDrives()
        this.cancelEdit()
      } catch (error) {
        this.showAlert(error.response?.data?.message || "Failed to save edits.")
      } finally {
        this.loading = false
      }
    },
    cancelEdit() {
      this.editMode = false
      this.editingDriveId = null
      this.resetForm()
    },
    async deleteDrive(driveId) {
      if (!confirm("Are you sure you want to delete this placement drive?")) return
      try {
        const response = await axios.delete(`/api/company/drive/${driveId}`)
        this.showAlert(response.data.message)
        this.fetchDrives()
        this.fetchPlacements() // Refresh placements if drive is deleted
        if (this.activeDriveId === driveId) {
          this.applicants = []
          this.activeDriveTitle = ''
        }
      } catch (error) {
        console.error("Error deleting drive:", error)
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
        this.showAlert(response.data.message)
        this.viewApplicants(this.activeDriveId)
        this.fetchPlacements() // Refresh placements list dynamically 
      } catch (error) {
        console.error("Error updating status:", error)
      }
    },
    async saveJoiningDate(placementId, dateVal) {
      try {
        const response = await axios.post(`/api/company/placement/${placementId}/joining-date`, {
          joining_date: dateVal
        })
        this.showAlert(response.data.message)
        this.fetchPlacements()
      } catch (error) {
        console.error("Error saving joining date:", error)
      }
    },
    getStatusBadgeClass(status) {
      if (status === 'Approved') return 'badge bg-success'
      if (status === 'Closed') return 'badge bg-secondary'
      return 'badge bg-warning text-dark'
    },
    getAppStatusBadgeClass(status) {
      if (status === 'Selected') return 'badge bg-success'
      if (status === 'Shortlisted') return 'badge bg-info'
      if (status === 'Rejected') return 'badge bg-danger'
      return 'badge bg-secondary'
    },
    showAlert(msg) {
      this.alertMessage = msg
      setTimeout(() => { this.alertMessage = '' }, 3000)
    },
    resetForm() {
      this.newDrive = { title: '', description: '', salary: null, criteria: '', deadline: '', status: 'Pending' }
    },
    handleLogout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>