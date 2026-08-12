# Email OTP Setup Guide

## Overview

Your Ulsavam backend now sends professional HTML emails for:
- ✅ OTP (One-Time Password) verification
- ✅ Email verification links
- ✅ Welcome emails for new users

All emails are beautifully designed with gradients, responsive layouts, and brand colors.

## Environment Variables Needed

Add these to your Render web service environment:

```
EMAIL_HOST_USER = abbasalitmk@gmail.com
EMAIL_HOST_PASSWORD = ekyg xkml rdtl ddyp
```

## How to Add Variables to Render

1. Go to Render Dashboard → your **ulsavam_backend** web service
2. Click **"Environment"** in the left sidebar
3. Click **"+ Add Environment Variable"** for each:

### Variable 1: EMAIL_HOST_USER
- **Key:** `EMAIL_HOST_USER`
- **Value:** `abbasalitmk@gmail.com`

### Variable 2: EMAIL_HOST_PASSWORD  
- **Key:** `EMAIL_HOST_PASSWORD`
- **Value:** `ekyg xkml rdtl ddyp`

4. Click **"Save"**
5. Deploy your app (changes take effect immediately)

## Email Templates

### 1. OTP Email (`otp_email.html`)
Sent when user requests OTP for login

**Features:**
- 6-digit OTP code prominently displayed
- 10-minute validity timer
- Security warning for unsolicited OTPs
- Gradient purple header
- Clear instructions

**When sent:**
```
POST /api/auth/otp/request/
{
  "identifier": "user@example.com",
  "method": "email"
}
```

### 2. Email Verification (`verification_email.html`)
Sent when user signs up to verify their email

**Features:**
- Clickable verification button
- Backup link for manual verification
- Brand colors and responsive design

### 3. Welcome Email (`welcome_email.html`)
Sent after successful registration

**Features:**
- Personalized greeting
- Feature highlights (4 columns: Discover, Location, Mark Attendance, Share)
- Getting started tips
- Call-to-action button
- Social links

## Testing Emails Locally

### Option 1: Use Render's PostgreSQL + Emails (Live Testing)

```bash
# Set environment variables locally
export EMAIL_HOST_USER="abbasalitmk@gmail.com"
export EMAIL_HOST_PASSWORD="ekyg xkml rdtl ddyp"
export DATABASE_URL="postgresql://user:password@host:5432/database"

# Run migrations and seed
python manage.py migrate
python manage.py seed_data

# Test OTP endpoint
curl -X POST http://localhost:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "your-email@example.com", "method": "email"}'

# Check your email inbox! 📧
```

### Option 2: Console Backend (Development Mode)

If you want to see emails in console during development:

```python
# In settings.py - temporarily use console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Then emails will print to console instead of sending.

### Option 3: Use Test Email Credentials

For testing without worrying about quota, use a service like:
- **Mailtrap** (free tier: 500 emails/month)
- **SendGrid** (free tier: 100 emails/day)
- **AWS SES** (free tier: 62,000 emails/month)

## Email Service Functions

Located in `core/email_service.py`:

### `send_otp_email(email, otp_code, purpose='login')`
```python
from core.email_service import send_otp_email

send_otp_email('user@example.com', '123456', purpose='login')
# Returns: True/False
```

### `send_verification_email(email, verification_link)`
```python
from core.email_service import send_verification_email

send_verification_email(
    'user@example.com',
    'https://ulsavam.com/verify?token=abc123'
)
```

### `send_welcome_email(display_name, email)`
```python
from core.email_service import send_welcome_email

send_welcome_email('Raj Kumar', 'raj@example.com')
```

## Gmail App Password Setup (Done for You ✅)

The app password `ekyg xkml rdtl ddyp` has been generated for account `abbasalitmk@gmail.com`

**If you need to regenerate or change it:**

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication (if not already enabled)
3. Go to "App passwords"
4. Select "Mail" and "Windows Computer" (or your setup)
5. Copy the generated 16-character password
6. Replace the `EMAIL_HOST_PASSWORD` value on Render

## OTP Flow (Complete)

```
User requests OTP
    ↓
POST /api/auth/otp/request/
    ↓
Backend generates 6-digit code (e.g., 123456)
    ↓
Code is hashed and stored in DB (expires in 10 minutes)
    ↓
Beautiful HTML email sent to user's email
    ↓
User receives email with OTP code
    ↓
User submits: POST /api/auth/otp/verify/
{
    "identifier": "user@example.com",
    "code": "123456"
}
    ↓
Backend verifies OTP and creates/logs in user
    ↓
User receives JWT tokens (access + refresh)
```

## Customizing Email Templates

All templates are in `core/templates/emails/`

To customize:

1. Edit the HTML file you want to change
2. Update email address: `noreply@ulsavam.com` → your email
3. Update social links
4. Change brand colors (look for `#667eea`)
5. Commit and deploy

## Troubleshooting

### "Failed to send OTP email"
- Check that EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set on Render
- Verify Gmail credentials are correct
- Check Render logs: Dashboard → Web Service → "Logs" tab

### "Authentication failed"
- Gmail app password is incorrect
- Make sure you're using the app password, NOT your regular Gmail password
- App passwords only work with 2FA enabled on Gmail account

### "SMTPAuthenticationError"
- Wait a few minutes after setting environment variables
- Email variables need time to propagate
- Try redeploying the service

### Emails going to spam
- Add SPF/DKIM records for your domain
- For testing, use a domain email like `noreply@yourdomain.com`
- Gmail usually trusts other Gmail accounts (our setup)

## Best Practices

✅ **Do:**
- Use app passwords, never your actual Gmail password
- Store credentials in environment variables
- Send emails asynchronously in production (use Celery)
- Include "unsubscribe" links for newsletters
- Test emails before sending to users

❌ **Don't:**
- Commit email credentials to git
- Send OTPs via SMS without email backup
- Send unnecessary emails (bad user experience)
- Use company email for sending (use noreply account)

## Next Steps

1. ✅ Add EMAIL_HOST_USER to Render environment
2. ✅ Add EMAIL_HOST_PASSWORD to Render environment
3. ✅ Deploy your app
4. ✅ Test OTP endpoint with your email
5. ✅ Check inbox for beautifully designed email!

## Support

Email templates are responsive and tested on:
- Gmail
- Outlook
- Apple Mail
- Mobile email clients

If you encounter any issues, check Render's deployment logs or test locally first.

Happy emailing! 📧🚀
