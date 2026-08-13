# OTP 500 Error - Debugging Guide

## Issue
Getting "Internal Server Error" on `/api/auth/otp/request/`

## Common Causes & Solutions

### 1. Email Environment Variables Not Set on Render
**Most likely cause:**

Check Render Dashboard:
```
Environment → Look for EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
```

If missing:
```
KEY: EMAIL_HOST_USER
VALUE: abbasalitmk@gmail.com

KEY: EMAIL_HOST_PASSWORD  
VALUE: fncyzojbvabypzvg
```

Then **Save** and wait 5-10 minutes for redeploy.

---

### 2. Check Render Logs

On Render Dashboard:
```
1. ulsavam_backend service
2. Click "Logs" tab
3. Look for recent error messages
4. Copy the full error and share
```

---

### 3. Test OTP Locally First

```bash
# Test email configuration
python manage.py test_email

# Or diagnose step by step
python manage.py diagnose_email
```

---

### 4. Check Database

```bash
# Test Django shell
python manage.py shell

# Check if OTPRequest model exists
>>> from users.models import OTPRequest
>>> OTPRequest.objects.count()

# Exit
>>> exit()
```

---

### 5. Manual OTP Send Test

```bash
python manage.py shell

from users.models import OTPRequest
from django.utils import timezone
from datetime import timedelta
from core.email_service import send_otp_email

# Generate OTP
code = OTPRequest.generate_code()
print(f"OTP Code: {code}")

# Try sending email
result = send_otp_email('abbasalitmk@gmail.com', code)
print(f"Email sent: {result}")

exit()
```

---

## Quick Checklist

- [ ] EMAIL_HOST_USER set on Render?
- [ ] EMAIL_HOST_PASSWORD set on Render?
- [ ] Service redeployed after env change?
- [ ] Render logs checked for errors?
- [ ] Email works locally (test_email command)?
- [ ] Gmail app password is correct?
- [ ] 2-Factor Authentication enabled on Gmail?

---

## Commands to Run (In Order)

```bash
# 1. Test email locally
python manage.py test_email

# 2. If above works, issue is Render env vars

# 3. Check what Render is using
python manage.py shell
>>> import os
>>> from django.conf import settings
>>> print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
>>> print(f"From env: {bool(os.environ.get('EMAIL_HOST_USER'))}")
>>> exit()

# 4. If from defaults, Render vars not set
# 5. Update Render environment variables
# 6. Wait 5-10 minutes for redeploy
# 7. Test again
```

---

## What to Share for Help

If still broken after trying above:

1. **Render Logs** - Copy the full error message
2. **Local test result** - Does `python manage.py test_email` work?
3. **Environment check** - What does settings show?
4. **Gmail status** - 2FA enabled? App password correct?

---

## Most Likely Fix

99% of the time it's **missing Render environment variables**.

**Action:**
1. Render Dashboard → ulsavam_backend → Environment
2. Add: `EMAIL_HOST_USER` = `abbasalitmk@gmail.com`
3. Add: `EMAIL_HOST_PASSWORD` = `fncyzojbvabypzvg`
4. Save → Wait 5-10 min
5. Test OTP again

That's usually it! ✅
