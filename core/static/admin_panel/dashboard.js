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

        if (response.status === 401) {
            localStorage.removeItem('adminToken');
            window.location.href = '/superadmin/login/';
            throw new Error('Session expired');
        }

        const result = await response.json();

        if (!response.ok) {
            showAlert(result.error || result.detail || 'An error occurred', 'error');
            throw new Error(result.error || result.detail || 'API Error');
        }

        return result;
    } catch (error) {
        if (error.message !== 'Session expired') {
            showAlert(error.message, 'error');
        }
        throw error;
    }
}

// Multipart API Helper (for file uploads - profile pics / event images)
async function apiCallMultipart(endpoint, method, formData) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
            body: formData
        });

        if (response.status === 401) {
            localStorage.removeItem('adminToken');
            window.location.href = '/superadmin/login/';
            throw new Error('Session expired');
        }

        const result = await response.json();

        if (!response.ok) {
            const message = result.error || result.detail ||
                Object.entries(result).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ') ||
                'An error occurred';
            showAlert(message, 'error');
            throw new Error(message);
        }

        return result;
    } catch (error) {
        if (error.message !== 'Session expired') {
            showAlert(error.message, 'error');
        }
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

// Districts cache (shared by event form dropdown)
let districtsCache = null;

async function loadDistrictsForSelect() {
    if (districtsCache) return districtsCache;
    const response = await fetch('/api/districts/', {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    const data = await response.json();
    districtsCache = Array.isArray(data) ? data : data.results;
    return districtsCache;
}

async function populateDistrictSelect(selectedId) {
    const districts = await loadDistrictsForSelect();
    const select = document.getElementById('eventDistrictSelect');
    select.innerHTML = districts.map(d =>
        `<option value="${d.id}" ${d.id === selectedId ? 'selected' : ''}>${d.name}</option>`
    ).join('');
}

function resetEventForm() {
    document.getElementById('eventForm').reset();
    document.getElementById('eventId').value = '';
    document.getElementById('existingImagesGroup').style.display = 'none';
    document.getElementById('existingImagesContainer').innerHTML = '';
}

async function openCreateEventModal() {
    document.getElementById('eventModalTitle').textContent = 'Create Event';
    resetEventForm();
    await populateDistrictSelect(null);
    document.getElementById('eventModal').classList.add('active');
}

async function editEvent(id) {
    let evt;
    try {
        evt = await apiCall(`/events/${id}/`);
    } catch (error) {
        console.error('Error loading event:', error);
        return;
    }

    document.getElementById('eventModalTitle').textContent = 'Edit Event';
    document.getElementById('eventId').value = evt.id;
    document.getElementById('eventTitle').value = evt.title || '';
    document.getElementById('eventDescription').value = evt.description || '';
    document.getElementById('eventCategorySelect').value = evt.category;
    document.getElementById('eventVenueName').value = evt.venue_name || '';
    document.getElementById('eventAddress').value = evt.address || '';
    document.getElementById('eventLatitude').value = evt.latitude ?? '';
    document.getElementById('eventLongitude').value = evt.longitude ?? '';
    document.getElementById('eventDate').value = evt.event_date || '';
    document.getElementById('eventStartTime').value = evt.start_time ? evt.start_time.slice(0, 5) : '';
    document.getElementById('eventStatusSelect').value = evt.status;
    document.getElementById('eventIsFeatured').checked = !!evt.is_featured;
    document.getElementById('eventImages').value = '';

    await populateDistrictSelect(evt.district);

    const container = document.getElementById('existingImagesContainer');
    container.innerHTML = '';
    if (evt.images && evt.images.length > 0) {
        document.getElementById('existingImagesGroup').style.display = 'block';
        evt.images.forEach(img => {
            const wrapper = document.createElement('div');
            wrapper.dataset.imageId = img.id;
            wrapper.dataset.remove = 'false';
            wrapper.style.cssText = 'position: relative; width: 80px; height: 80px;';
            wrapper.innerHTML = `
                <img src="${img.image_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px; border: 1px solid var(--border);">
                <button type="button" onclick="toggleRemoveImage(this)" title="Remove"
                    style="position: absolute; top: -6px; right: -6px; background: #ef4444; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; line-height: 1;">×</button>
            `;
            container.appendChild(wrapper);
        });
    } else {
        document.getElementById('existingImagesGroup').style.display = 'none';
    }

    document.getElementById('eventModal').classList.add('active');
}

function toggleRemoveImage(button) {
    const wrapper = button.parentElement;
    const img = wrapper.querySelector('img');
    const marked = wrapper.dataset.remove === 'true';

    if (marked) {
        wrapper.dataset.remove = 'false';
        img.style.opacity = '1';
        button.textContent = '×';
        button.style.background = '#ef4444';
    } else {
        wrapper.dataset.remove = 'true';
        img.style.opacity = '0.3';
        button.textContent = '↺';
        button.style.background = '#6b7280';
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

async function saveEvent(event) {
    event.preventDefault();

    const eventId = document.getElementById('eventId').value;
    const submitBtn = document.getElementById('eventSubmitBtn');
    const originalText = submitBtn.textContent;

    const formData = new FormData();
    formData.append('title', document.getElementById('eventTitle').value);
    formData.append('description', document.getElementById('eventDescription').value);
    formData.append('category', document.getElementById('eventCategorySelect').value);
    formData.append('district', document.getElementById('eventDistrictSelect').value);
    formData.append('venue_name', document.getElementById('eventVenueName').value);
    formData.append('address', document.getElementById('eventAddress').value);

    const latitude = document.getElementById('eventLatitude').value;
    const longitude = document.getElementById('eventLongitude').value;
    if (latitude) formData.append('latitude', latitude);
    if (longitude) formData.append('longitude', longitude);

    formData.append('event_date', document.getElementById('eventDate').value);
    const startTime = document.getElementById('eventStartTime').value;
    if (startTime) formData.append('start_time', startTime);

    formData.append('status', document.getElementById('eventStatusSelect').value);
    formData.append('is_featured', document.getElementById('eventIsFeatured').checked);

    const imageFiles = document.getElementById('eventImages').files;
    for (let i = 0; i < imageFiles.length; i++) {
        formData.append('images', imageFiles[i]);
    }

    if (eventId) {
        document.querySelectorAll('#existingImagesContainer > div').forEach(wrapper => {
            if (wrapper.dataset.remove === 'true') {
                formData.append('remove_image_ids', wrapper.dataset.imageId);
            }
        });
    }

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        if (eventId) {
            await apiCallMultipart(`/events/${eventId}/`, 'PATCH', formData);
            showAlert('Event updated successfully!', 'success');
        } else {
            await apiCallMultipart('/events/', 'POST', formData);
            showAlert('Event created successfully!', 'success');
        }

        closeModal('eventModal');
        loadEvents();
    } catch (error) {
        console.error('Error saving event:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
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
