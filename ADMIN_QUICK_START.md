# Admin Dashboard - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Get Admin Token
```bash
# Use admin account credentials
EMAIL="admin@ulsavam.com"
PASSWORD="admin123"

# Request OTP
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$EMAIL\", \"method\": \"email\"}"

# Check email for OTP code, then verify
OTP="123456"  # Replace with actual OTP from email
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$EMAIL\", \"code\": \"$OTP\"}" \
  | jq '.access'

# Save token
TOKEN="your_access_token_here"
```

### Step 2: You're Ready!
All admin endpoints now accessible with:
```bash
-H "Authorization: Bearer $TOKEN"
```

---

## 📊 Dashboard Overview

```
Admin Dashboard (/api/admin/)
├── Users Management
│   ├── List all users
│   ├── Search & filter
│   ├── Create/edit/delete users
│   ├── Make staff members
│   └── View activity
├── Districts Management
│   ├── List districts
│   ├── View events per district
│   ├── View users per district
│   └── Statistics
└── Events Management
    ├── List events (45+ festivals)
    ├── Verify pending events
    ├── Reject events
    ├── Toggle featured status
    ├── View confirmations & attendees
    └── Statistics & analytics
```

---

## 🔧 Common Admin Tasks

### Task: Review Pending Events

**View all pending events:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/pending/
```

**Verify an event (approve it):**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/verify/
```

**Reject an event:**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/reject/ \
  -d '{"reason": "Insufficient details provided"}'
```

---

### Task: Manage Featured Events

**Get all featured events:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?is_featured=true"
```

**Make an event featured:**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/toggle_featured/
```

---

### Task: View Event Details & Engagement

**Get complete event information:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/
```

**See who confirmed for an event:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/confirmations/
```

**See who's attending:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/{event_id}/attendees/
```

---

### Task: User Administration

**Find a user:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/users/?search=raj"
```

**Make someone a staff member (moderator):**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/users/{user_id}/make_staff/
```

**View user activity:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/users/{user_id}/activity/
```

---

### Task: District Management

**View all events in Thrissur:**
```bash
# First, get Thrissur district ID (usually 7)
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/districts/?search=thrissur"

# Then get events
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/districts/7/events/
```

**View all users in a district:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/districts/1/users/
```

---

### Task: Get Dashboard Statistics

**System overview:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/stats/
```

**User statistics:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/users/stats/
```

**District statistics:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/districts/stats/
```

---

## 🔍 Advanced Filtering

### Filter Verified Events Only
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?status=verified"
```

### Filter by Category
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?category=temple"
```

### Search & Filter Combined
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?search=pooram&category=temple&status=verified&is_featured=true"
```

### Get Upcoming Events (Next 7 days)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/upcoming/?days=7"
```

### Order Results
```bash
# By date (ascending)
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?ordering=event_date"

# By date (descending)
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?ordering=-event_date"

# By creation date
curl -H "Authorization: Bearer $TOKEN" \
  "https://ulsavam-backend.onrender.com/api/admin/events/?ordering=-created_at"
```

---

## 📈 Dashboard Response Examples

### Events Statistics Response
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
    "Ernakulam": 6
  },
  "engagement": {
    "total_confirmations": 250,
    "total_attendees": 180
  }
}
```

### Event with Engagement Data
```json
{
  "id": 1,
  "title": "Thrissur Pooram",
  "category": "temple",
  "district_name": "Thrissur",
  "event_date": "2026-04-26",
  "status": "verified",
  "is_featured": true,
  "confirmation_count": 45,
  "attendance_count": 32,
  "confirmations": [
    {
      "user_id": 5,
      "user_name": "Raj Kumar",
      "user_email": "raj@example.com",
      "confirmed_at": "2026-08-15T14:20:00Z"
    }
  ],
  "attendees": [
    {
      "user_id": 6,
      "user_name": "Priya Sharma",
      "user_email": "priya@example.com",
      "marked_at": "2026-08-16T09:45:00Z"
    }
  ]
}
```

---

## 🎯 Keyboard Shortcuts (for API testing tools like Postman)

**Set up in Postman/Insomnia:**
1. Create collection "Ulsavam Admin"
2. Add authorization header in collection settings
3. Copy any endpoint and replace `{id}` with actual ID

**Headers to include in all requests:**
```
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json
```

---

## ⚠️ Important Notes

### Authentication
- Admin token expires after 15 minutes
- Use refresh token to get new access token
- Share tokens securely (never in git/logs)

### Permissions
- Only `is_staff=true` users can access admin endpoints
- Superusers have full access
- Regular users get permission denied error

### Data Management
- Deleting events will remove confirmations/attendance
- Cascading deletes are enabled
- No undo functionality - be careful!

### Rate Limiting
- No strict rate limits on admin (trusted users)
- OTP requests limited to 5/hour per identifier
- Database throttling applies to large queries

---

## 🚀 Production Checklist

Before going live:
- [ ] Change admin password from default
- [ ] Set strong EMAIL_HOST_PASSWORD on Render
- [ ] Review all staff user permissions
- [ ] Test verification workflow
- [ ] Set up admin alerts/notifications
- [ ] Document custom admin workflows
- [ ] Train team on admin dashboard

---

## 📱 Testing the Dashboard

### Quick Test: Verify Everything Works
```bash
# 1. Get token
TOKEN="your_token_here"

# 2. Test Users endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/users/

# 3. Test Districts endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/districts/

# 4. Test Events endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/

# 5. Test Stats
curl -H "Authorization: Bearer $TOKEN" \
  https://ulsavam-backend.onrender.com/api/admin/events/stats/
```

---

## 🆘 Troubleshooting

### "Authentication credentials were not provided"
- Check token format: `Authorization: Bearer TOKEN`
- Verify token hasn't expired (request new one)
- Confirm user is staff member (`is_staff=true`)

### "Permission denied"
- Ensure user has `is_staff=true`
- Request new admin token
- Check if superuser privileges needed

### "Not found" on endpoints
- Verify correct resource ID
- Check if resource was deleted
- Try listing all resources first

### CORS Errors
- Add origin to Django CORS settings
- Check if frontend origin is in ALLOWED_ORIGINS
- Verify request includes Authorization header

---

## 📚 Full Documentation

See `ADMIN_DASHBOARD.md` for complete API documentation with:
- All endpoints detailed
- All query parameters explained
- All response formats documented
- Real-world examples
- Best practices

---

**Admin Dashboard Ready! 🎉**

Start managing festivals, users, and districts today!
