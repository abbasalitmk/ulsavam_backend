// Admin Panel JavaScript

let authToken = localStorage.getItem('adminToken');
const API_BASE = '/api/admin';

// Check if user is authenticated
document.addEventListener('DOMContentLoaded', function() {
    if (!authToken) {
        window.location.href = '/superadmin/login/';
        return;
    }

    // Load initial dashboard
    loadDashboard();
    setupNavigation();
});

// Navigation Setup
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            showPage(page);
        });
    });
}

function showPage(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');

    // Show selected page
    const pageElement = document.getElementById(page + 'Page');
    if (pageElement) {
        pageElement.style.display = 'block';
    }

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    // Load page content
    if (page === 'dashboard') loadDashboard();
    else if (page === 'events') loadEvents();
    else if (page === 'users') loadUsers();
    else if (page === 'districts') loadDistricts();
}

// Shortcut functions
function showDashboard() { showPage('dashboard'); }
function showEvents() { showPage('events'); }
function showUsers() { showPage('users'); }
function showDistricts() { showPage('districts'); }
function showSettings() { showPage('settings'); }

// API Helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            showAlert(result.error || 'An error occurred', 'error');
            throw new Error(result.error || 'API Error');
        }

        return result;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
}

// Alert System
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button style="background: none; border: none; cursor: pointer; font-size: 1.2rem;" onclick="this.parentElement.remove()">×</button>
    `;

    alertContainer.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}

// Dashboard
async function loadDashboard() {
    try {
        const stats = await apiCall('/events/stats/');

        document.getElementById('totalEvents').textContent = stats.total_events || 0;
        document.getElementById('verifiedEvents').textContent = stats.status_breakdown?.verified || 0;
        document.getElementById('pendingEvents').textContent = stats.status_breakdown?.pending || 0;
        document.getElementById('featuredEvents').textContent = stats.featured_events || 0;

        // Load users stats
        const userStats = await apiCall('/users/stats/');
        document.getElementById('totalUsers').textContent = userStats.total_users || 0;

        // Load districts
        const districts = await apiCall('/districts/');
        document.getElementById('totalDistricts').textContent = districts.count || 0;

        // Load recent events
        const events = await apiCall('/events/?ordering=-created_at&limit=5');
        loadRecentEvents(events.results);

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function loadRecentEvents(events) {
    const container = document.getElementById('recentEventsContainer');

    if (!events || events.length === 0) {
        container.innerHTML = '<p style="padding: 2rem; text-align: center;">No events yet</p>';
        return;
    }

    let html = '<div class="table-container"><table style="width: 100%;"><thead><tr><th>Title</th><th>District</th><th>Status</th><th>Date</th></tr></thead><tbody>';

    events.forEach(event => {
        html += `<tr>
            <td><strong>${event.title}</strong></td>
            <td>${event.district_name || '-'}</td>
            <td><span class="badge ${event.status}">${event.status}</span></td>
            <td>${event.event_date || '-'}</td>
        </tr>`;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Events Management
async function loadEvents() {
    try {
        const response = await apiCall('/events/');
        renderEventsTable(response.results);
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function renderEventsTable(events) {
    const tbody = document.getElementById('eventsTableBody');

    if (!events || events.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No events found</td></tr>';
        return;
    }

    tbody.innerHTML = events.map(event => `
        <tr>
            <td><strong>${event.title}</strong></td>
            <td>${event.category}</td>
            <td>${event.event_date}</td>
            <td><span class="badge ${event.status}">${event.status}</span></td>
            <td>${event.confirmation_count}</td>
            <td>
                <div class="actions">
                    <button class="btn btn-sm btn-primary" onclick="editEvent(${event.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${event.status === 'pending' ? `
                        <button class="btn btn-sm btn-success" onclick="verifyEvent(${event.id})" title="Verify">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="deleteEvent(${event.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterEvents() {
    const search = document.getElementById('eventSearch').value;
    const status = document.getElementById('eventStatus').value;
    const category = document.getElementById('eventCategory').value;

    let url = '/events/?';
    if (search) url += `search=${search}&`;
    if (status) url += `status=${status}&`;
    if (category) url += `category=${category}&`;

    apiCall(url).then(response => renderEventsTable(response.results));
}

async function verifyEvent(eventId) {
    if (!confirm('Verify this event?')) return;

    try {
        await apiCall(`/events/${eventId}/verify/`, 'POST');
        showAlert('Event verified successfully!', 'success');
        loadEvents();
    } catch (error) {
        console.error('Error verifying event:', error);
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Delete this event? This action cannot be undone.')) return;

    try {
        await apiCall(`/events/${eventId}/`, 'DELETE');
        showAlert('Event deleted successfully!', 'success');
        loadEvents();
    } catch (error) {
        console.error('Error deleting event:', error);
    }
}

function openCreateEventModal() {
    document.getElementById('eventModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function saveEvent(event) {
    event.preventDefault();
    // Implementation for saving event
    closeModal('eventModal');
    loadEvents();
}

// Users Management
async function loadUsers() {
    try {
        const response = await apiCall('/users/');
        renderUsersTable(response.results);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');

    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.display_name}</strong></td>
            <td>${user.email}</td>
            <td>${user.district_name || '-'}</td>
            <td><span class="badge ${user.is_staff ? 'featured' : ''}">${user.is_staff ? 'Staff' : 'User'}</span></td>
            <td>${user.confirmation_count || 0}</td>
            <td>
                <div class="actions">
                    <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${!user.is_staff ? `
                        <button class="btn btn-sm btn-success" onclick="makeStaff(${user.id})" title="Make Staff">
                            <i class="fas fa-crown"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function filterUsers() {
    const search = document.getElementById('userSearch').value;
    const staff = document.getElementById('userStaff').value;

    let url = '/users/?';
    if (search) url += `search=${search}&`;
    if (staff === 'staff') url += 'is_staff=true&';
    else if (staff === 'regular') url += 'is_staff=false&';

    apiCall(url).then(response => renderUsersTable(response.results));
}

async function makeStaff(userId) {
    if (!confirm('Make this user a staff member?')) return;

    try {
        await apiCall(`/users/${userId}/make_staff/`, 'POST');
        showAlert('User promoted to staff!', 'success');
        loadUsers();
    } catch (error) {
        console.error('Error promoting user:', error);
    }
}

function openCreateUserModal() {
    // Implementation for creating user
}

// Districts Management
async function loadDistricts() {
    try {
        const response = await apiCall('/districts/');
        renderDistrictsTable(response.results);
    } catch (error) {
        console.error('Error loading districts:', error);
    }
}

function renderDistrictsTable(districts) {
    const tbody = document.getElementById('districtsTableBody');

    if (!districts || districts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem;">No districts found</td></tr>';
        return;
    }

    tbody.innerHTML = districts.map(district => `
        <tr>
            <td><strong>${district.name}</strong></td>
            <td>${district.event_count}</td>
            <td>${district.user_count}</td>
            <td>
                <div class="actions">
                    <button class="btn btn-sm btn-primary" onclick="editDistrict(${district.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteDistrict(${district.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openCreateDistrictModal() {
    // Implementation for creating district
}

// Logout
function logout() {
    localStorage.removeItem('adminToken');
    window.location.href = '/superadmin/login/';
}
