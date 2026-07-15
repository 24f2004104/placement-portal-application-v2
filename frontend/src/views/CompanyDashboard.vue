<template>
  <div class="container py-4">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom rounded-3 mb-4 py-3 px-3 shadow-sm">
      <div class="container-fluid">
        <span class="navbar-brand fw-bold text-primary fs-4">Placement Portal<span class="text-secondary">.v2</span></span>
        
        <!-- Interactive Avatar Dropdown Menu -->
        <div class="dropdown">
          <div class="d-flex align-items-center role-dropdown" @click="dropdownOpen = !dropdownOpen" style="cursor: pointer;">
            <div class="me-3 text-end d-none d-sm-block">
              <div class="fw-semibold small text-muted">Welcome!</div>
              <div class="text-primary fw-bold small text-capitalize">{{ username }}</div>
            </div>
            <div class="avatar-badge bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 40px; height: 40px; text-transform: uppercase;">
              {{ username ? username.charAt(0) : 'C' }}
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

    <!-- Sticky alerts -->
    <div v-if="alertMessage" class="alert alert-info text-center sticky-alert" role="alert">
      {{ alertMessage }}
    </div>

    <div class="row">
      <!-- Left Column: Placement form & Profile update form tabs -->
      <div class="col-12 col-lg-5 mb-4">
        <div class="card p-4">
          <!-- Form tab navigation -->
          <ul class="nav nav-tabs mb-4 border-bottom-0 text-center" id="formTab" role="tablist">
            <li class="nav-item flex-fill" role="presentation">
              <button 
                class="nav-link w-100 py-2" 
                @click="formTab = 'drive'" 
                :class="{ active: formTab === 'drive' }"
                type="button"
              >
                Placement Drive
              </button>
            </li>
            <li class="nav-item flex-fill" role="presentation">
              <button 
                class="nav-link w-100 py-2" 
                @click="formTab = 'profile'" 
                :class="{ active: formTab === 'profile' }"
                type="button"
              >
                Profile
              </button>
            </li>
          </ul>

          <!-- Form tab content -->
          <div class="tab-content" id="formTabContent">
            <!-- Form tab 1: Placement drive creation/modification -->
            <div v-if="formTab === 'drive'">
              <h5 class="mb-3 text-secondary fw-bold">{{ editMode ? 'Modify Placement Drive' : 'Create Placement Drive' }}</h5>
              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="title" class="form-label fw-semibold text-muted small">Job Title</label>
                  <input type="text" v-model="newDrive.title" id="title" class="form-control" placeholder="e.g., Software Engineer" required />
                </div>

                <div class="mb-3">
                  <label for="description" class="form-label fw-semibold text-muted small">Job Description</label>
                  <textarea v-model="newDrive.description" id="description" class="form-control" rows="3" placeholder="Describe the job role..." required></textarea>
                </div>

                <div class="mb-3">
                  <label for="salary" class="form-label fw-semibold text-muted small">Annual Salary (INR)</label>
                  <input type="number" v-model="newDrive.salary" id="salary" class="form-control" placeholder="e.g., 600000" />
                </div>

                <div class="mb-3">
                  <label for="criteria" class="form-label fw-semibold text-muted small">Eligibility Criteria</label>
                  <input type="text" v-model="newDrive.criteria" id="criteria" class="form-control" placeholder="e.g., CGPA > 8.0, CSE only" />
                </div>

                <div class="mb-3">
                  <label for="deadline" class="form-label fw-semibold text-muted small">Application Deadline</label>
                  <input type="datetime-local" v-model="newDrive.deadline" id="deadline" class="form-control" required />
                </div>

                <div class="mb-3" v-if="editMode">
                  <label for="status" class="form-label fw-semibold text-muted small">Status</label>
                  <select v-model="newDrive.status" id="status" class="form-select">
                    <option value="Pending">Pending Admin Approval</option>
                    <option value="Approved">Approved / Active</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>

                <button type="submit" class="btn btn-primary w-100 mb-2" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editMode ? 'Save Modifications' : 'Submit for Admin Approval' }}
                </button>
                <button v-if="editMode" type="button" @click="cancelEdit" class="btn btn-outline-secondary w-100">
                  Cancel Edit
                </button>
              </form>
            </div>

            <!-- Form tab 2: Manage company profile -->
            <div v-if="formTab === 'profile'">
              <h5 class="mb-3 text-secondary fw-bold">Manage Company Profile</h5>
              <form @submit.prevent="saveProfile">
                <div class="mb-3">
                  <label for="coName" class="form-label fw-semibold text-muted small">Company Name</label>
                  <input type="text" v-model="profile.company_name" id="coName" class="form-control" required />
                </div>

                <div class="mb-3">
                  <label for="coIndustry" class="form-label fw-semibold text-muted small">Industry Sector</label>
                  <input type="text" v-model="profile.industry" id="coIndustry" class="form-control" />
                </div>

                <div class="mb-3">
                  <label for="coLocation" class="form-label fw-semibold text-muted small">Location / HQ</label>
                  <input type="text" v-model="profile.location" id="coLocation" class="form-control" />
                </div>

                <div class="mb-3">
                  <label for="coContact" class="form-label fw-semibold text-muted small">HR Contact Email</label>
                  <input type="email" v-model="profile.hr_contact" id="coContact" class="form-control" />
                </div>

                <div class="mb-3">
                  <label for="coWebsite" class="form-label fw-semibold text-muted small">Website Link</label>
                  <input type="url" v-model="profile.website" id="coWebsite" class="form-control" />
                </div>

                <button type="submit" class="btn btn-primary w-100" :disabled="savingProfile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
                  Save Profile Changes
                </button>
              </form>
            </div>

          </div>
        </div>
      </div>

      <!-- Right column: Lists -->
      <div class="col-12 col-lg-7 mb-4">
        <!-- Posted drives table -->
        <div class="card p-4 mb-4">
          <h4 class="mb-3 text-secondary fw-bold" style="font-size: 1.15rem;">Your Posted Placement Drives</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
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
                    <div class="d-flex flex-wrap gap-2 justify-content-end">
                      <button @click="viewApplicants(drive.id)" class="btn btn-sm btn-outline-primary">Applicants</button>
                      <button @click="enableEditMode(drive)" class="btn btn-sm btn-outline-secondary">Edit</button>
                      <button @click="deleteDrive(drive.id)" class="btn btn-sm btn-outline-danger">Delete</button>
                    </div>
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
        <div class="card p-4 mb-4 position-relative" v-if="activeDriveTitle">
          <button @click="closeApplicants" class="btn-close position-absolute" style="top: 20px; right: 20px;" aria-label="Close"></button>
          
          <h4 class="mb-3 text-secondary fw-bold" style="font-size: 1.15rem; max-width: 90%;">Applicants for: <span class="text-primary">{{ activeDriveTitle }}</span></h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
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
        <div class="card p-4 shadow-sm">
          <h4 class="mb-3 text-secondary fw-bold border-bottom pb-2" style="font-size: 1.15rem;">Successful Placements & Joining Dates</h4>
          <div class="table-responsive">
            <table class="table table-hover-rows align-middle">
              <thead>
                <tr>
                  <th>Selected Student</th>
                  <th>Job Position</th>
                  <th>Salary</th>
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
      username: '',
      dropdownOpen: false, 
      companyId: null,
      formTab: 'drive', 
      drives: [],
      applicants: [],
      placements: [],
      profile: {
        company_name: '',
        industry: '',
        location: '',
        hr_contact: '',
        website: ''
      },
      activeDriveId: null,
      activeDriveTitle: '',
      alertMessage: '',
      loading: false,
      savingProfile: false,
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
    this.username = localStorage.getItem('username') || 'Company'
    this.companyId = localStorage.getItem('profile_id')
    this.fetchDrives()
    this.fetchPlacements()
    this.fetchProfile()
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
    async fetchProfile() {
      try {
        const response = await axios.get(`/api/company/${this.companyId}/profile`)
        this.profile = response.data
      } catch (error) {
        console.error("Error fetching company profile details:", error)
      }
    },
    async saveProfile() {
      this.savingProfile = true
      this.alertMessage = ''
      try {
        const response = await axios.put(`/api/company/${this.companyId}/profile`, this.profile)
        this.showAlert(response.data.message)
        this.fetchProfile()
        localStorage.setItem('username', this.profile.company_name)
        this.username = this.profile.company_name
      } catch (error) {
        this.showAlert("Failed to update company profile.")
      } finally {
        this.savingProfile = false
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
      this.formTab = 'drive' 
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
        this.fetchPlacements()
        if (this.activeDriveId === driveId) {
          this.closeApplicants()
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
    closeApplicants() {
      this.applicants = []
      this.activeDriveId = null
      this.activeDriveTitle = ''
    },
    async updateApplicantStatus(applicationId, newStatus) {
      try {
        const response = await axios.post(`/api/company/application/${applicationId}/status`, {
          status: newStatus
        })
        this.showAlert(response.data.message)
        this.viewApplicants(this.activeDriveId)
        this.fetchPlacements()
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