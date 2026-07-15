<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Color scheme */
:root {
  --primary: #2563eb;          
  --primary-hover: #1d4ed8;
  --success: #10b981;          
  --danger: #ef4444;            
  --warning: #f59e0b;           
  --bg-light: #f8fafc;          
  --text-dark: #0f172a;         
  --text-muted: #334155;        
  --border-color: #e2e8f0;      
  --border-radius: 12px;
}

/* Global styling */
body {
  background-color: var(--bg-light) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--text-dark) !important;
  -webkit-font-smoothing: antialiased;
}

/* Cards */
.card {
  border: 1px solid var(--border-color) !important;
  border-radius: var(--border-radius) !important;
  background: #ffffff !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05) !important;
  overflow: hidden; 
}

/* Glowing outline highlighting on hover */
.interactive-card {
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.interactive-card:hover {
  transform: scale(1.01);
  border-color: var(--primary) !important;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.08) !important;
}

/* Input fields */
.form-control, .form-select {
  border-radius: 8px !important;
  border: 1px solid var(--border-color) !important;
  padding: 10px 16px !important;
  font-size: 0.9rem !important;
  color: var(--text-dark);
  transition: all 0.15s ease-in-out !important;
}

.form-control:focus, .form-select:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15) !important;
}

/* Buttons */
.btn {
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  transition: all 0.15s ease-in-out !important;
}

/* Tables */
.table {
  border-collapse: separate !important;
  border-spacing: 0 8px !important;
}

.table th, .table td {
  text-align: center !important; 
  vertical-align: middle !important;
}

.table thead th {
  border-bottom: none !important;
  color: var(--text-muted) !important; 
  font-weight: 600 !important;
  text-transform: uppercase !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.05em !important;
}

.table tbody tr {
  background-color: #ffffff !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
  transition: all 0.15s ease-in-out;
}

.table-hover-rows tbody tr:hover {
  background-color: #f1f5f9 !important; 
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.04) !important;
}

.table td {
  border: none !important;
  padding: 14px 16px !important;
  font-size: 0.9rem;
}

.table tbody tr td:first-child {
  border-top-left-radius: 8px !important;
  border-bottom-left-radius: 8px !important;
}

.table tbody tr td:last-child {
  border-top-right-radius: 8px !important;
  border-bottom-right-radius: 8px !important;
}

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-responsive::-webkit-scrollbar {
  height: 6px;
}
.table-responsive::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}

/* Badges & Dropdown badges */
.badge, .badge-select {
  width: 120px !important; 
  display: inline-block !important;
  padding: 6px 12px !important;
  border-radius: 20px !important;
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  border: none !important;
  text-align: center !important;
  text-align-last: center !important; 
}

.badge-select option {
  text-align: center !important;
}

.badge-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e");
  background-position: right 8px center;
  background-repeat: no-repeat;
  padding-right: 20px !important;
}

.dropdown-menu-end {
  right: 0 !important;
  left: auto !important;
}

/* Sticky alerts */
.sticky-alert {
  position: fixed !important;
  top: 24px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 2050 !important;
  width: 90% !important;
  max-width: 480px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) !important;
  border-radius: 10px !important;
}

.bg-success { background-color: var(--success) !important; }
.bg-danger { background-color: var(--danger) !important; }
.bg-warning { background-color: var(--warning) !important; }
.bg-info { background-color: var(--primary) !important; }
</style>