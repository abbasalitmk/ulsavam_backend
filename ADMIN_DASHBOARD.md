# Admin Dashboard API Documentation

## Overview

Comprehensive admin dashboard for managing all Ulsavam backend resources:
- **Users Management** - Create, read, update, delete users
- **Districts Management** - Manage Kerala districts
- **Events Management** - Full event lifecycle management with verification

All endpoints require **staff/admin authentication**.

---

## Authentication

All admin endpoints require:
1. Valid JWT token from `/api/auth/otp/` endpoint
2. User must have `is_staff=true`

### Get Admin Token
```bash
# Request OTP
curl -X POST http://localhost:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@ulsavam.com", "method": "email"}'

# Verify OTP and get token
curl -X POST http://localhost:8000/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@ulsavam.com", "code": "123456"}'

# Use access token for all admin requests
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ...
```

---

## User Management

### Base URL
```
/api/admin/users/
```

### List All Users
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/
```

**Query Parameters:**
- `search=keyword` - Search by email, phone, or display name
- `district=id` - Filter by district
- `is_staff=true/false` - Filter by staff status
- `preferred_language=en/ml` - Filter by language
- `ordering=-created_at` - Order by field (prefix `-` for descending)

**Example with filters:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/users/?search=raj&district=1&is_staff=false&ordering=-created_at"
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "raj@example.com",
      "phone_number": "9876543210",
      "display_name": "Raj Kumar",
      "district": 1,
      "district_name": "Thiruvananthapuram",
      "preferred_language": "en",
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2026-08-12T10:30:00Z",
      "confirmation_count": 5,
      "attendance_count": 3
    }
  ]
}
```

### Get User Details
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/1/
```

### Create New User
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/users/ \
  -d '{
    "email": "newuser@example.com",
    "display_name": "New User",
    "district": 1,
    "preferred_language": "en",
    "phone_number": "9123456789"
  }'
```

### Update User
```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/users/1/ \
  -d '{
    "display_name": "Updated Name",
    "district": 2
  }'
```

### Delete User
```bash
curl -X DELETE -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/1/
```

### Make User Staff
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/1/make_staff/
```

**Response:**
```json
{
  "status": "Raj Kumar is now staff"
}
```

### Remove Staff Privileges
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/1/remove_staff/
```

### Get User Activity
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/1/activity/
```

**Response:**
```json
{
  "user_id": 1,
  "user_name": "Raj Kumar",
  "confirmations": 5,
  "attendances": 3,
  "organized_events": 0,
  "total_interactions": 8
}
```

### Get User Statistics
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/stats/
```

**Response:**
```json
{
  "total_users": 10,
  "staff_members": 2,
  "users_with_event_interests": 8,
  "regular_users": 8
}
```

---

## District Management

### Base URL
```
/api/admin/districts/
```

### List All Districts
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/districts/
```

**Query Parameters:**
- `search=keyword` - Search by name or slug
- `ordering=name` - Order by field

**Response:**
```json
{
  "count": 14,
  "results": [
    {
      "id": 1,
      "name": "Thiruvananthapuram",
      "slug": "thiruvananthapuram",
      "event_count": 8,
      "user_count": 12
    }
  ]
}
```

### Get District Details
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/districts/1/
```

### Create District
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/districts/ \
  -d '{"name": "New District"}'
```

### Update District
```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/districts/1/ \
  -d '{"name": "Updated District Name"}'
```

### Delete District
```bash
curl -X DELETE -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/districts/1/
```

### Get Events in District
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/districts/1/events/?status=verified&featured_only=true"
```

**Query Parameters:**
- `status=verified/pending/rejected` - Filter by status
- `category=temple/church/arts_culture/etc` - Filter by category
- `featured_only=true/false` - Show only featured events

**Response:**
```json
{
  "district": "Thiruvananthapuram",
  "total_events": 8,
  "events": [
    {
      "id": 1,
      "title": "Attukal Pongala",
      "category": "temple",
      "event_date": "2026-03-03",
      "status": "verified",
      "is_featured": true,
      "confirmation_count": 45,
      "attendance_count": 32
    }
  ]
}
```

### Get Users in District
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/districts/1/users/?is_staff=false"
```

### Get District Statistics
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/districts/stats/
```

**Response:**
```json
{
  "total_districts": 14,
  "districts": [
    {
      "district_name": "Thiruvananthapuram",
      "total_events": 8,
      "total_users": 12,
      "verified_events": 8,
      "featured_events": 6
    }
  ]
}
```

---

## Event Management

### Base URL
```
/api/admin/events/
```

### List All Events
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/
```

**Query Parameters:**
- `search=keyword` - Search by title, description, venue
- `district=id` - Filter by district
- `category=temple/church/etc` - Filter by category
- `status=verified/pending/rejected` - Filter by status
- `is_featured=true/false` - Filter by featured status
- `ordering=-event_date` - Order by field

**Example with filters:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/?district=1&status=verified&is_featured=true&ordering=-event_date"
```

**Response:**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "title": "Attukal Pongala",
      "category": "temple",
      "district": 1,
      "district_name": "Thiruvananthapuram",
      "event_date": "2026-03-03",
      "start_time": "10:30:00",
      "status": "verified",
      "is_featured": true,
      "organizer_name": "Admin User",
      "confirmation_count": 45,
      "attendance_count": 32,
      "created_at": "2026-08-12T10:30:00Z"
    }
  ]
}
```

### Get Event Details
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/
```

**Response includes:**
- Full event details
- Organizer information
- All confirmations with user info
- All attendees with user info

```json
{
  "id": 1,
  "title": "Attukal Pongala",
  "description": "World's largest gathering...",
  "category": "temple",
  "district": 1,
  "district_name": "Thiruvananthapuram",
  "venue_name": "Attukal Bhagavathy Temple",
  "address": "Attukal, Thiruvananthapuram, Kerala 695001",
  "latitude": 8.4735,
  "longitude": 76.9537,
  "event_date": "2026-03-03",
  "start_time": "10:30:00",
  "cover_image": "https://...",
  "organizer": 1,
  "organizer_email": "admin@ulsavam.com",
  "organizer_name": "Admin User",
  "status": "verified",
  "is_featured": true,
  "created_at": "2026-08-12T10:30:00Z",
  "confirmation_count": 45,
  "attendance_count": 32,
  "confirmations": [
    {
      "id": 1,
      "user_id": 5,
      "user_name": "Raj Kumar",
      "user_email": "raj@example.com",
      "created_at": "2026-08-15T14:20:00Z"
    }
  ],
  "attendees": [
    {
      "id": 1,
      "user_id": 6,
      "user_name": "Priya Sharma",
      "user_email": "priya@example.com",
      "created_at": "2026-08-16T09:45:00Z"
    }
  ]
}
```

### Create Event
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/events/ \
  -d '{
    "title": "New Festival",
    "description": "Festival description",
    "category": "temple",
    "district": 1,
    "venue_name": "Temple Name",
    "address": "Address details",
    "latitude": 8.5,
    "longitude": 76.9,
    "event_date": "2026-09-15",
    "start_time": "10:00:00",
    "cover_image": "https://...",
    "organizer": 1,
    "status": "verified",
    "is_featured": true
  }'
```

### Update Event
```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/events/1/ \
  -d '{"title": "Updated Title", "status": "verified"}'
```

### Delete Event
```bash
curl -X DELETE -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/
```

### Verify Event
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/verify/
```

**Response:**
```json
{
  "status": "Event \"Festival Name\" verified successfully"
}
```

### Reject Event
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/events/1/reject/ \
  -d '{"reason": "Incomplete details"}'
```

### Toggle Featured Status
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/toggle_featured/
```

**Response:**
```json
{
  "status": "success",
  "event_id": 1,
  "is_featured": true
}
```

### Get Event Confirmations
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/confirmations/
```

**Response:**
```json
{
  "event_id": 1,
  "event_title": "Attukal Pongala",
  "total_confirmations": 45,
  "confirmations": [
    {
      "id": 1,
      "user_id": 5,
      "user_name": "Raj Kumar",
      "user_email": "raj@example.com",
      "user_district": "Thiruvananthapuram",
      "confirmed_at": "2026-08-15T14:20:00Z"
    }
  ]
}
```

### Get Event Attendees
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/attendees/
```

### Get Upcoming Events
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/upcoming/?days=30"
```

**Query Parameters:**
- `days=30` - Number of days to look ahead (default: 30)

### Get Pending Events
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/pending/
```

Returns all events awaiting verification.

### Get Events by Category
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/by_category/?category=temple"
```

### Get Event Statistics
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/stats/
```

**Response:**
```json
{
  "total_events": 45,
  "status_breakdown": {
    "verified": 40,
    "pending": 4,
    "rejected": 1
  },
  "featured_events": 30,
  "by_category": {
    "temple": 17,
    "church": 7,
    "arts_culture": 8,
    "sports": 4,
    "community": 6
  },
  "by_district": {
    "Thiruvananthapuram": 8,
    "Thrissur": 12,
    "Ernakulam": 6,
    "Alappuzha": 5
  },
  "engagement": {
    "total_confirmations": 250,
    "total_attendees": 180
  }
}
```

---

## Filter & Search Examples

### Search for Thrissur Events
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/?search=thrissur&district=7"
```

### Get Pending Temple Festivals
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/?category=temple&status=pending"
```

### Get Featured Events Ending Soon
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/?is_featured=true&ordering=event_date"
```

### Get Staff Members by District
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/users/?district=1&is_staff=true"
```

### Get Events with High Engagement
```bash
# Get pending events and check which have confirmations
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/events/pending/" | \
  jq '.events | sort_by(.confirmation_count) | reverse'
```

---

## Access Control

All admin endpoints check:
1. **Authentication** - Valid JWT token required
2. **Authorization** - User must have `is_staff=true`
3. **Ownership** - Can manage any resources (not limited by ownership)

### Permission Denied Response
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Best Practices

✅ **DO:**
- Use search filters for large datasets
- Paginate through results (default: 20 per page)
- Verify events before they appear in public API
- Archive/reject spam events promptly
- Monitor user engagement metrics

❌ **DON'T:**
- Delete events without verification
- Create duplicate event entries
- Share admin tokens with non-staff
- Modify historical data without reason
- Make events featured without curation

---

## Common Use Cases

### Daily Admin Tasks
```bash
# Check pending verification
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/pending/

# Get stats
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/stats/

# Find events in specific district
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/admin/districts/1/events/"
```

### Event Curation
```bash
# Verify an event
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/verify/

# Make it featured
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/events/1/toggle_featured/
```

### User Management
```bash
# Make user a moderator
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/5/make_staff/

# Check user activity
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/admin/users/5/activity/
```

---

## Support

For API issues:
- Check authentication token validity
- Verify user has `is_staff=true`
- Review error messages for field validation
- Check Render logs for backend errors

All admin endpoints are fully functional and production-ready! 🚀
