# Ulsavam Backend API Documentation

This document lists the available API endpoints, required request bodies, authentication rules, and expected response structures for the current Django REST Framework backend.

Base URL:
- Local: http://localhost:8000
- Production: depends on deployment environment

## Authentication

The API uses JWT authentication via DRF SimpleJWT.

Headers for authenticated requests:

```http
Authorization: Bearer <access_token>
```

The app exposes these auth endpoints under `/api/auth/`.

---

## 1. OpenAPI / Documentation

### 1.1 Get OpenAPI schema
- Method: GET
- URL: `/api/schema/`
- Auth: No
- Response: raw OpenAPI schema JSON

### 1.2 Swagger UI
- Method: GET
- URL: `/api/docs/`
- Auth: No
- Response: Swagger interactive UI

### 1.3 Redoc UI
- Method: GET
- URL: `/api/redoc/`
- Auth: No
- Response: Redoc documentation UI

---

## 2. Authentication APIs

### 2.1 Request OTP
- Method: POST
- URL: `/api/auth/otp/request/`
- Auth: No
- Body:

```json
{
  "identifier": "9876543210",
  "method": "phone"
}
```

or

```json
{
  "identifier": "user@example.com",
  "method": "email"
}
```

Expected success response:

```json
{
  "message": "OTP sent successfully to 9876543210.",
  "dev_hint": 123456
}
```

Notes:
- `method` must be either `phone` or `email`
- OTP is also printed in the server console for local testing (`dev_hint` is included in the response)
- Rate-limited: `5/hour`

Error response example:

```json
{
  "identifier": [
    "This field is required."
  ],
  "method": [
    ""method" is not a valid choice."
  ]
}
```

### 2.2 Verify OTP and login
- Method: POST
- URL: `/api/auth/otp/verify/`
- Auth: No
- Body:

```json
{
  "identifier": "9876543210",
  "code": "123456"
}
```

Expected success response:

```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": 1,
    "phone_number": "9876543210",
    "email": null,
    "display_name": "User_3210",
    "avatar": null,
    "district": null,
    "district_details": null,
    "is_info_revealed": false,
    "preferred_language": "en",
    "created_at": "2026-08-12T10:00:00Z"
  }
}
```

Error response examples:

```json
{
  "error": "No OTP request found for this identifier."
}
```

```json
{
  "error": "Invalid or expired OTP code."
}
```

### 2.3 Refresh access token
- Method: POST
- URL: `/api/auth/token/refresh/`
- Auth: No
- Body:

```json
{
  "refresh": "<refresh_token>"
}
```

Expected success response:

```json
{
  "access": "<new_access_token>"
}
```

### 2.4 Logout
- Method: POST
- URL: `/api/auth/logout/`
- Auth: Required (`IsAuthenticated`)
- Body:

```json
{
  "refresh": "<refresh_token>"
}
```

Expected success response:

```json
{
  "message": "Successfully logged out."
}
```

Status code: `205 RESET CONTENT`

Error response:

```json
{
  "error": "Invalid or expired refresh token."
}
```

### 2.5 Get current user
- Method: GET
- URL: `/api/auth/me/`
- Auth: Required
- Response:

```json
{
  "id": 1,
  "phone_number": "9876543210",
  "email": null,
  "display_name": "User_3210",
  "avatar": null,
  "district": 2,
  "district_details": {
    "id": 2,
    "name": "Kozhikode",
    "slug": "kozhikode"
  },
  "is_info_revealed": false,
  "preferred_language": "en",
  "created_at": "2026-08-12T10:00:00Z"
}
```

This endpoint also supports update via `PUT`/`PATCH` because it uses `RetrieveUpdateAPIView`.

---

## 3. District APIs

### 3.1 List districts
- Method: GET
- URL: `/api/districts/`
- Auth: No
- Response:

```json
[
  {
    "id": 1,
    "name": "Thiruvananthapuram",
    "slug": "thiruvananthapuram"
  },
  {
    "id": 2,
    "name": "Kozhikode",
    "slug": "kozhikode"
  }
]
```

Note:
- This is a `ReadOnlyModelViewSet`
- `pagination_class = None`, so it returns all districts without pagination

---

## 4. Event APIs

### 4.1 List events
- Method: GET
- URL: `/api/events/`
- Auth: Not required
- Optional query params:
  - `district` — district slug, example: `district=kozhikode`
  - `district_id` — numeric district id, example: `district_id=2`
  - `category` — event category
  - `date` — exact date, format: `YYYY-MM-DD`
  - `date_from` — start date, `YYYY-MM-DD`
  - `date_to` — end date, `YYYY-MM-DD`
  - `is_featured` — `true` / `false`
  - `verified_only` — `true` to return only verified events
  - `search` — search by title, description, venue name, or address

Example:

```http
GET /api/events/?district=kozhikode&category=temple&verified_only=true
```

Response format (paginated by default):

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "title": "Ayyappa Temple Festival",
      "category": "temple",
      "district": 2,
      "district_name": "Kozhikode",
      "district_slug": "kozhikode",
      "venue_name": "Sree Ayyappa Temple",
      "event_date": "2026-08-15",
      "start_time": "18:00:00",
      "cover_image": null,
      "status": "verified",
      "is_featured": false,
      "confirmations_count": 0,
      "going_count": 2,
      "is_going": false,
      "is_confirmed_by_user": false,
      "created_at": "2026-08-12T10:15:00Z"
    }
  ]
}
```

### 4.2 Create event
- Method: POST
- URL: `/api/events/`
- Auth: Required (`IsAuthenticated`)
- Body:

```json
{
  "title": "Onam Celebrations",
  "description": "Community cultural festival with music and food.",
  "category": "community",
  "district": 2,
  "venue_name": "City Square Grounds",
  "address": "Kozhikode Main Road",
  "latitude": 11.2588,
  "longitude": 75.7804,
  "event_date": "2026-09-06",
  "start_time": "18:30:00",
  "cover_image": "https://example.com/image.jpg",
  "is_featured": false
}
```

Expected response:

```json
{
  "id": 11,
  "title": "Onam Celebrations",
  "category": "community",
  "district": 2,
  "district_name": "Kozhikode",
  "district_slug": "kozhikode",
  "venue_name": "City Square Grounds",
  "event_date": "2026-09-06",
  "start_time": "18:30:00",
  "cover_image": "https://example.com/image.jpg",
  "status": "pending",
  "is_featured": false,
  "confirmations_count": 0,
  "going_count": 0,
  "is_going": false,
  "is_confirmed_by_user": false,
  "created_at": "2026-08-12T10:30:00Z"
}
```

Notes:
- Event is created with `organizer = request.user`
- Event status defaults to `pending`
- If 3 users confirm it, it can auto-flip to `verified`

### 4.3 Get event details
- Method: GET
- URL: `/api/events/{id}/`
- Auth: No
- Response:

```json
{
  "id": 10,
  "title": "Ayyappa Temple Festival",
  "description": "A vibrant temple festival with cultural events.",
  "category": "temple",
  "district": 2,
  "district_details": {
    "id": 2,
    "name": "Kozhikode",
    "slug": "kozhikode"
  },
  "venue_name": "Sree Ayyappa Temple",
  "address": "Temple Road, Kozhikode",
  "latitude": 11.2588,
  "longitude": 75.7804,
  "event_date": "2026-08-15",
  "start_time": "18:00:00",
  "cover_image": null,
  "organizer": 7,
  "organizer_name": "Anonymous Organizer",
  "status": "verified",
  "is_featured": false,
  "confirmations_count": 3,
  "going_count": 12,
  "is_going": true,
  "is_confirmed_by_user": false,
  "created_at": "2026-08-10T12:00:00Z"
}
```

### 4.4 Update event
- Method: PUT / PATCH
- URL: `/api/events/{id}/`
- Auth: Required for creator or authenticated user depending on project policies
- Body: same structure as create event, partial or full JSON allowed

### 4.5 Delete event
- Method: DELETE
- URL: `/api/events/{id}/`
- Auth: Required
- Response: empty body with HTTP `204 No Content`

### 4.6 Happening now
- Method: GET
- URL: `/api/events/happening-now/`
- Auth: No
- Optional query params:
  - `district` — district slug or district id

Example:

```http
GET /api/events/happening-now/?district=2
```

Expected response:

```json
[
  {
    "id": 15,
    "title": "Evening Drum Performance",
    "category": "community",
    "district": 2,
    "district_name": "Kozhikode",
    "district_slug": "kozhikode",
    "venue_name": "Beach Square",
    "event_date": "2026-08-12",
    "start_time": "19:00:00",
    "cover_image": "",
    "status": "verified",
    "is_featured": true,
    "confirmations_count": 2,
    "going_count": 9,
    "is_going": false,
    "is_confirmed_by_user": false,
    "created_at": "2026-08-10T08:00:00Z"
  }
]
```

### 4.7 Event calendar
- Method: GET
- URL: `/api/events/calendar/`
- Auth: No
- Optional query params:
  - `district`
  - `month` — format `YYYY-MM`

Example:

```http
GET /api/events/calendar/?district=kozhikode&month=2026-09
```

Expected response:

```json
[
  {
    "id": 11,
    "title": "Onam Celebrations",
    "category": "community",
    "district": 2,
    "district_name": "Kozhikode",
    "district_slug": "kozhikode",
    "venue_name": "City Square Grounds",
    "event_date": "2026-09-06",
    "start_time": "18:30:00",
    "cover_image": "https://example.com/image.jpg",
    "status": "verified",
    "is_featured": false,
    "confirmations_count": 0,
    "going_count": 0,
    "is_going": false,
    "is_confirmed_by_user": false,
    "created_at": "2026-08-12T10:30:00Z"
  }
]
```

### 4.8 Toggle “Going” status
- Method: POST
- URL: `/api/events/{id}/going/`
- Auth: Required
- Body: no body required

Expected first-time response:

```json
{
  "message": "Marked as Going!",
  "is_going": true,
  "going_count": 1
}
```

Expected second toggle response:

```json
{
  "message": "Removed from Going list.",
  "is_going": false,
  "going_count": 0
}
```

### 4.9 Confirm event
- Method: POST
- URL: `/api/events/{id}/confirm/`
- Auth: Required
- Body: no body required

Expected first response:

```json
{
  "message": "Event confirmation recorded successfully!",
  "confirmations_count": 1,
  "status": "pending"
}
```

If the same user confirms again:

```json
{
  "message": "You have already verified this event.",
  "confirmations_count": 1,
  "status": "pending"
}
```

If 3 confirmations are reached and the event is pending, status may change to:

```json
"status": "verified"
```

### 4.10 Get attendees of an event
- Method: GET
- URL: `/api/events/{id}/attendees/`
- Auth: No
- Response:

```json
[
  {
    "id": 3,
    "user_id": 12,
    "display_name": "Festival Goer",
    "avatar": "",
    "created_at": "2026-08-12T10:45:00Z"
  }
]
```

---

## 5. Notification APIs

### 5.1 List notifications for logged-in user
- Method: GET
- URL: `/api/notifications/`
- Auth: Required
- Response:

```json
[
  {
    "id": 1,
    "type": "confirmation_added",
    "message": "A new user confirmed your event.",
    "related_event": 10,
    "event_title": "Ayyappa Temple Festival",
    "is_read": false,
    "created_at": "2026-08-12T11:05:00Z"
  }
]
```

### 5.2 Mark notification as read
- Method: POST
- URL: `/api/notifications/{id}/read/`
- Auth: Required
- Body: no body required
- Success response:

```json
{
  "message": "Notification marked as read."
}
```

- If notification does not exist for this user:

```json
{
  "error": "Notification not found."
}
```

---

## 6. Common Response Patterns

### Success response examples
- `200 OK` for successful GET / POST / PATCH requests
- `201 Created` for successful event creation
- `205 Reset Content` for logout
- `204 No Content` for delete operations

### Validation error response

```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### Authorization error response

```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## 7. Known API Behavior Notes

- `OTPRequestView` is throttled at `5/hour` using the `otp_request` throttle.
- OTP values are printed to the console in development mode for testing.
- Default pagination is enabled for event listings: `PageNumberPagination` with page size `10`.
- `district` is usually represented by `district_id` or `district` in serializers, and event list filtering supports both slug and numeric id.
- Event creation defaults to `status = pending` and uses the authenticated user as organizer.
- Confirmation and attendance actions are toggles: calling the same action again removes the record.

---

## 8. Example Full Flow

### Register/login with OTP
1. `POST /api/auth/otp/request/`
2. Receive OTP from response `dev_hint` or console output
3. `POST /api/auth/otp/verify/`
4. Use returned `access` token in `Authorization` header

### Fetch events
```http
GET /api/events/?verified_only=true
Authorization: Bearer <access_token>
```

### Add event
```http
POST /api/events/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Local Food Fair",
  "description": "Food festival in the district.",
  "category": "food_fest",
  "district": 2,
  "venue_name": "Town Square",
  "address": "Main Road, Kozhikode",
  "latitude": 11.2588,
  "longitude": 75.7804,
  "event_date": "2026-09-10",
  "start_time": "17:00:00",
  "cover_image": "https://example.com/food.jpg",
  "is_featured": false
}
```

---

## 9. Useful URLs

- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`
- Schema: `/api/schema/`

This file reflects the actual backend logic present in the current codebase and is intended as a practical API reference for frontend integration and testing.
