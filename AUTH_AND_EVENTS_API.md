# Ulsavam API — Auth, Profile & Events (Mobile App Guide)

Base URL (production): `https://ulsavam-backend.onrender.com`
Base URL (local dev): `http://localhost:8000`

All endpoints below are under `/api/`. All request/response bodies are JSON **unless a file is being uploaded**, in which case use `multipart/form-data` (this is required whenever `profile_pic` or `images` fields are present).

## Authentication header

Every authenticated endpoint requires:
```
Authorization: Bearer <access_token>
```

Access tokens expire after **15 minutes**. Refresh tokens last **30 days**. Use `/api/auth/token/refresh/` to get a new access token without re-logging in.

---

## 1. Register

Creates a new account. **Either `email` or `phone_number` must be provided** (at least one — both is fine too). Returns JWT tokens immediately, so the user is logged in right after registering — no separate login call needed.

```
POST /api/auth/register/
Content-Type: multipart/form-data
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string | conditional | Must be unique if provided |
| `phone_number` | string | conditional | Must be unique if provided |
| `name` | string | **yes** | Maps to the user's display name |
| `password` | string | **yes** | Min 6 characters |
| `date_of_birth` | date (`YYYY-MM-DD`) | **yes** | |
| `gender` | string | **yes** | One of: `male`, `female`, `other`, `prefer_not_to_say` |
| `district` | integer | **yes** | District ID — see [District list](#6-district-list-for-dropdown) |
| `profile_pic` | file (image) | no | JPG/PNG etc. |

At least one of `email` / `phone_number` is required — omitting both returns a 400.

### Example (email registration)
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/register/ \
  -F "email=raj@example.com" \
  -F "name=Raj Kumar" \
  -F "password=SecurePass123" \
  -F "date_of_birth=1995-06-15" \
  -F "gender=male" \
  -F "district=10" \
  -F "profile_pic=@/path/to/photo.jpg"
```

### Example (phone-only registration, no picture)
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/register/ \
  -F "phone_number=9876543210" \
  -F "name=Priya Sharma" \
  -F "password=SecurePass456" \
  -F "date_of_birth=1998-03-20" \
  -F "gender=female" \
  -F "district=6"
```

### Success response — `201 Created`
```json
{
  "message": "Registration successful.",
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user": {
    "id": 25,
    "phone_number": null,
    "email": "raj@example.com",
    "display_name": "Raj Kumar",
    "avatar": null,
    "profile_pic_url": "https://ulsavam-backend.onrender.com/media/profile_pics/photo.jpg",
    "date_of_birth": "1995-06-15",
    "gender": "male",
    "district": 10,
    "district_details": { "id": 10, "name": "Kozhikode", "slug": "kozhikode" },
    "is_info_revealed": false,
    "preferred_language": "en",
    "created_at": "2026-08-13T10:15:07.091838+05:30"
  }
}
```

### Errors — `400 Bad Request`
```json
{ "error": ["Either email or phone_number must be provided."] }
```
```json
{ "email": ["This email is already registered."] }
```
```json
{ "phone_number": ["This phone number is already registered."] }
```

---

## 2. Login with username + password

`username` accepts **either** an email or a phone number — the API detects which one you sent (presence of `@` means email).

```
POST /api/auth/login/
Content-Type: application/json
```

| Field | Type | Required |
|---|---|---|
| `username` | string (email or phone) | yes |
| `password` | string | yes |

### Example
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "raj@example.com", "password": "SecurePass123"}'
```
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "9876543210", "password": "SecurePass456"}'
```

### Success response — `200 OK`
```json
{
  "message": "Login successful.",
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user": { "...": "same shape as register response" }
}
```

### Error — `400 Bad Request`
```json
{ "error": "Invalid username or password." }
```
Same generic message whether the account doesn't exist, the password is wrong, or the account has no password set (e.g. it was only ever used via OTP login) — this is intentional, to avoid leaking which accounts exist.

**Rate limit:** 10 attempts/hour per username+IP combination.

---

## 3. Login with Email OTP

Two-step flow. **The account must already be registered** — OTP login does not create new accounts (use [Register](#1-register) for that).

### Step 3a — Request OTP
```
POST /api/auth/otp/request/
Content-Type: application/json
```

| Field | Type | Required |
|---|---|---|
| `identifier` | string (email or phone) | yes |
| `method` | string: `"email"` or `"phone"` | yes |

```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "raj@example.com", "method": "email"}'
```

**Success — `200 OK`**
```json
{ "message": "OTP sent successfully to raj@example.com.", "validity": "Valid for 10 minutes" }
```

**No account found — `404 Not Found`**
```json
{ "error": "No account found with this identifier. Please register first." }
```

**Rate limit:** 5 requests/hour per identifier+IP.

> Note: `method: "phone"` currently logs the OTP server-side (SMS delivery isn't wired up yet) — email delivery via Resend is fully live.

### Step 3b — Verify OTP
```
POST /api/auth/otp/verify/
Content-Type: application/json
```

| Field | Type | Required |
|---|---|---|
| `identifier` | string | yes |
| `code` | string, 6 digits | yes |

```bash
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "raj@example.com", "code": "123456"}'
```

**Success — `200 OK`** — same shape as login (`access`, `refresh`, `user`).

**Errors:**
- `400` — `{"error": "Invalid or expired OTP code."}`
- `404` — `{"error": "No account found with this identifier. Please register first."}`

---

## 4. Get / Update Profile

```
GET  /api/auth/me/      — fetch the logged-in user's profile
PATCH /api/auth/me/     — partially update (send only the fields you're changing)
```
Requires `Authorization: Bearer <access_token>`. Use `multipart/form-data` whenever uploading `profile_pic`; plain JSON is fine otherwise.

### Editable fields
`display_name`, `profile_pic` (file), `date_of_birth`, `gender`, `district`, `preferred_language` (`en`/`ml`), `is_info_revealed`.

`email` and `phone_number` are **read-only** here (changing them isn't supported yet — would need re-verification).

### Example — update name + upload/replace picture
```bash
curl -X PATCH https://ulsavam-backend.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "display_name=Raj K." \
  -F "profile_pic=@/path/to/new_photo.jpg"
```

### Example — update text fields only (JSON)
```bash
curl -X PATCH https://ulsavam-backend.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"district": 6, "preferred_language": "ml"}'
```

### Response — `200 OK`
```json
{
  "id": 25,
  "phone_number": null,
  "email": "raj@example.com",
  "display_name": "Raj K.",
  "avatar": null,
  "profile_pic_url": "https://ulsavam-backend.onrender.com/media/profile_pics/new_photo.jpg",
  "date_of_birth": "1995-06-15",
  "gender": "male",
  "district": 6,
  "district_details": { "id": 6, "name": "Ernakulam", "slug": "ernakulam" },
  "is_info_revealed": false,
  "preferred_language": "ml",
  "created_at": "2026-08-13T10:15:07.091838+05:30"
}
```

`profile_pic_url` is always an absolute URL, ready to load directly in an `<Image>`/`ImageView` — falls back to `avatar` (legacy external URL field) if no uploaded picture exists, else `null`.

---

## 5. Token refresh & logout

```
POST /api/auth/token/refresh/
Content-Type: application/json
Body: {"refresh": "<refresh_token>"}
```
Returns `{"access": "<new_access_token>"}`.

```
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json
Body: {"refresh": "<refresh_token>"}
```
Blacklists the refresh token. Returns `205 Reset Content`.

---

## 6. District list (for dropdown)

```
GET /api/districts/
```
No auth required. Returns all 14 Kerala districts with `id`, `name`, `slug` — use `id` when registering/updating profile/creating events.

```bash
curl https://ulsavam-backend.onrender.com/api/districts/
```

---

## 7. Create Event (with multiple image uploads)

```
POST /api/events/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```
New events are created with `status: "pending"` and need 3 user confirmations (or admin verification) before they show up publicly. The creator is automatically set as `organizer`.

| Field | Type | Required |
|---|---|---|
| `title` | string | yes |
| `description` | string | yes |
| `category` | string | yes — see [categories](#event-categories) |
| `district` | integer | yes |
| `venue_name` | string | yes |
| `address` | string | yes |
| `latitude` | float | no (default `10.0`) |
| `longitude` | float | no (default `76.0`) |
| `event_date` | date `YYYY-MM-DD` | yes |
| `start_time` | time `HH:MM:SS` | no |
| `cover_image` | string (URL) | no — legacy external-image field |
| `images` | file, **repeatable** | no — attach multiple files under the same `images` key |

### Example — multiple images in one request
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/events/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "title=Kozhikode Beach Cleanup Drive" \
  -F "description=Community beach cleanup, all volunteers welcome." \
  -F "category=community" \
  -F "district=10" \
  -F "venue_name=Kozhikode Beach" \
  -F "address=Beach Road, Kozhikode" \
  -F "latitude=11.2588" \
  -F "longitude=75.7704" \
  -F "event_date=2026-09-01" \
  -F "start_time=07:00:00" \
  -F "images=@/path/photo1.jpg" \
  -F "images=@/path/photo2.jpg" \
  -F "images=@/path/photo3.jpg"
```

### Response — `201 Created`
```json
{
  "id": 61,
  "title": "Kozhikode Beach Cleanup Drive",
  "description": "Community beach cleanup, all volunteers welcome.",
  "category": "community",
  "district": 10,
  "district_details": { "id": 10, "name": "Kozhikode", "slug": "kozhikode" },
  "venue_name": "Kozhikode Beach",
  "address": "Beach Road, Kozhikode",
  "latitude": 11.2588,
  "longitude": 75.7704,
  "event_date": "2026-09-01",
  "start_time": "07:00:00",
  "cover_image": null,
  "images": [
    { "id": 1, "image_url": "https://ulsavam-backend.onrender.com/media/event_images/photo1.jpg", "order": 0, "created_at": "..." },
    { "id": 2, "image_url": "https://ulsavam-backend.onrender.com/media/event_images/photo2.jpg", "order": 1, "created_at": "..." },
    { "id": 3, "image_url": "https://ulsavam-backend.onrender.com/media/event_images/photo3.jpg", "order": 2, "created_at": "..." }
  ],
  "organizer": 25,
  "organizer_name": "Raj K.",
  "status": "pending",
  "is_featured": false,
  "confirmations_count": 0,
  "going_count": 0,
  "is_going": false,
  "is_confirmed_by_user": false,
  "created_at": "2026-09-01T07:00:00+05:30"
}
```

---

## 8. Update Event (add/remove images, edit fields)

```
PATCH /api/events/{id}/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```
**Only the event's organizer or an admin/staff account can update or delete it** — anyone else gets `403 Forbidden`.

Send only the fields you're changing. To manage images in the same request:
- `images` — new files to **add** (repeatable field, same as create)
- `remove_image_ids` — image IDs to **delete** (repeatable field, e.g. send `remove_image_ids=3` and `remove_image_ids=5` for two separate images)

### Example — change title, add 1 image, remove 1 image
```bash
curl -X PATCH https://ulsavam-backend.onrender.com/api/events/61/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "title=Kozhikode Beach Cleanup Drive (Updated)" \
  -F "images=@/path/new_photo.jpg" \
  -F "remove_image_ids=1"
```
Response: same shape as create, reflecting the new `images` list.

### Alternative: dedicated image endpoints
If you'd rather manage images outside of the main update call:

**Add images to an existing event:**
```
POST /api/events/{id}/upload-images/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```
```bash
curl -X POST https://ulsavam-backend.onrender.com/api/events/61/upload-images/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "images=@/path/photo4.jpg"
```
Returns `201` with the list of newly created image objects.

**Remove a single image:**
```
DELETE /api/events/{id}/images/{image_id}/
Authorization: Bearer <access_token>
```
```bash
curl -X DELETE https://ulsavam-backend.onrender.com/api/events/61/images/2/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```
Returns `200 {"message": "Image removed successfully."}` or `404` if that image doesn't belong to the event.

### Permission error — `403 Forbidden`
```json
{ "detail": "You do not have permission to perform this action." }
```

---

## 9. Other existing event endpoints (unchanged)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/events/` | GET | no | List events (filterable — see below) |
| `/api/events/{id}/` | GET | no | Event detail, includes `images` |
| `/api/events/{id}/` | DELETE | organizer/staff | Delete event |
| `/api/events/{id}/going/` | POST | yes | Toggle "I'm going" |
| `/api/events/{id}/confirm/` | POST | yes | Confirm event is real (3 confirmations auto-verifies it) |
| `/api/events/{id}/attendees/` | GET | no | List of users marked "going" |
| `/api/events/happening-now/` | GET | no | Today's verified events, optional `?district=` |
| `/api/events/calendar/` | GET | no | Verified events, optional `?district=&month=YYYY-MM` |

### List filters (`GET /api/events/?...`)
| Param | Example | Notes |
|---|---|---|
| `district` | `?district=kozhikode` | matches district **slug** |
| `district_id` | `?district_id=10` | matches district **id** |
| `category` | `?category=temple` | exact match |
| `date` | `?date=2026-08-15` | exact event date |
| `date_from` / `date_to` | `?date_from=2026-08-13&date_to=2026-08-19` | date range |
| `is_featured` | `?is_featured=true` | |
| `verified_only` | `?verified_only=true` | only `status=verified` |
| `search` | `?search=beach` | matches title/description/venue/address |

---

## Event categories

| Value | Label |
|---|---|
| `temple` | Temple Festival |
| `church` | Church Feast |
| `mosque` | Mosque Heritage |
| `dj_music` | DJ & Music Show |
| `beach_meetup` | Beach Meetup |
| `arts_culture` | Arts & Culture |
| `food_fest` | Food Festival |
| `sports` | Sports & Games |
| `community` | Community Gathering |
| `literature` | Literature & Reading |
| `heritage_walk` | Heritage Walk |
| `market` | Local Market |
| `nature_park` | Nature & Park |

## Gender choices

| Value | Label |
|---|---|
| `male` | Male |
| `female` | Female |
| `other` | Other |
| `prefer_not_to_say` | Prefer not to say |

---

## Quick reference — all auth endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/auth/register/` | POST | no | Create account (email and/or phone + password) |
| `/api/auth/login/` | POST | no | Login with username (email/phone) + password |
| `/api/auth/otp/request/` | POST | no | Send login OTP (existing accounts only) |
| `/api/auth/otp/verify/` | POST | no | Verify OTP, get tokens (existing accounts only) |
| `/api/auth/token/refresh/` | POST | no | Refresh access token |
| `/api/auth/logout/` | POST | yes | Blacklist refresh token |
| `/api/auth/me/` | GET/PATCH | yes | View/update own profile, upload picture |

## Quick reference — event image endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/events/` | POST | yes | Create event, optionally with multiple `images` |
| `/api/events/{id}/` | PATCH | organizer/staff | Update event, add/remove images |
| `/api/events/{id}/upload-images/` | POST | organizer/staff | Add images to existing event |
| `/api/events/{id}/images/{image_id}/` | DELETE | organizer/staff | Remove one image |

---

## Notes for mobile app implementation

- **Always use `multipart/form-data`** when the request includes any file field (`profile_pic`, `images`) — don't base64-encode images into JSON.
- For the `images` repeatable field, attach each file under the **same field name** `images` (this is standard multipart array behavior — e.g. in Android's OkHttp/Retrofit use multiple `MultipartBody.Part` entries named `"images"`; in iOS/Swift's `URLSession`, append multiple parts with the same field name; in Flutter's `http.MultipartRequest`, call `files.add(...)` multiple times with `field: 'images'`).
- Store `access` and `refresh` tokens securely (Keychain/Keystore, not plain SharedPreferences/UserDefaults).
- On `401 Unauthorized` from any endpoint, attempt a silent token refresh via `/api/auth/token/refresh/` before forcing re-login.
- `profile_pic_url` and event `images[].image_url` are always absolute URLs — safe to load directly.
