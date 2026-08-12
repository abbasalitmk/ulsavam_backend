# Email Testing: Is it Render or Local Issue?

## Quick Diagnostic Flow

```
Does email work locally?
├─ YES → Issue is with RENDER environment
│        └─ Fix: Add EMAIL variables to Render
│        └─ Action: Go to Render dashboard → Environment
│
└─ NO → Issue is with LOCAL setup
         ├─ Gmail credentials wrong?
         │  └─ Fix: Regenerate app password
         │
         ├─ Python SMTP can't reach Gmail?
         │  └─ Fix: Check network/firewall
         │
         └─ Django backend misconfigured?
            └─ Fix: Check settings.py email config
```

---

## Test 1: Check If It's Render Issue (DO THIS FIRST)

### A. Test Gmail Credentials Directly (No Django)

This tests if Gmail app password is correct:

```bash
python3 << 'EOF'
import smtplib

email = "abbasalitmk@gmail.com"
password = "ekyg xkml rdtl ddyp"  # Your app password

try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    print("✓ Connected to Gmail SMTP")
    
    server.starttls()
    print("✓ TLS enabled")
    
    server.login(email, password)
    print("✓ LOGIN SUCCESSFUL - Credentials are correct!")
    
    # Send test email
    from email.mime.text import MIMEText
    msg = MIMEText("Test email")
    msg['Subject'] = 'Gmail Auth Test'
    msg['From'] = email
    msg['To'] = 'abbasalitmk@gmail.com'
    
    server.sendmail(email, ['abbasalitmk@gmail.com'], msg.as_string())
    print("✓ EMAIL SENT - Everything works!")
    
    server.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ LOGIN FAILED: {e}")
    print("   → Check your app password")
    print("   → Regenerate at https://myaccount.google.com/security")
    
except ConnectionError as e:
    print(f"❌ CANNOT REACH GMAIL: {e}")
    print("   → Check internet connection")
    print("   → Check firewall/VPN")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

EOF
```

**Result:**
- ✅ If it prints "✓ EMAIL SENT" → Gmail setup is CORRECT
- ❌ If it fails → The Gmail credentials are WRONG

---

### B. Test Django Email Backend Locally

If Step A worked, test Django:

```bash
python manage.py diagnose_email
```

This will:
1. Show all email settings
2. Test raw SMTP connection
3. Test Django backend
4. Show users in database

**Result:**
- ✅ If it sends successfully → LOCAL is working fine
- ❌ If it fails → RENDER might have wrong variables

---

## Test 2: Determine Root Cause

### Case 1: Python SMTP works, Django doesn't

**Problem:** Django email configuration issue

**Check:**
```bash
cat ulsavam_backend/settings.py | grep -A10 "^EMAIL"
```

Should show:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'abbasalitmk@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ekyg xkml rdtl ddyp')
```

**Fix:**
- Verify settings.py is exactly as above
- Restart Django: `Ctrl+C` then `python manage.py runserver`

---

### Case 2: Everything works locally, fails on Render

**Problem:** Render environment variables not set

**Evidence:**
- ✅ `python manage.py diagnose_email` works
- ❌ OTP doesn't arrive when testing on Render
- ❌ Django shell works locally but not on Render

**Fix:**

On Render Dashboard:
1. Go to **ulsavam_backend** service
2. Click **Environment**
3. Add these variables:
   ```
   EMAIL_HOST_USER = abbasalitmk@gmail.com
   EMAIL_HOST_PASSWORD = ekyg xkml rdtl ddyp
   ```
4. Click **Save**
5. Wait 5-10 minutes for redeploy
6. Test again

**Verify on Render:**
```bash
# After redeploy, check logs
# Render Dashboard → Logs → Search for "EMAIL"
```

---

### Case 3: Gmail app password is wrong

**Evidence:**
- ❌ Python SMTP test shows "LOGIN FAILED"
- ❌ All settings correct but authentication fails
- ❌ Error message: "535-5.7.8 Username and password not accepted"

**Fix:**

1. Go to: https://myaccount.google.com/security
2. Find **App passwords** section
3. Check if 2-Step Verification is enabled
   - If NOT → Enable it first
   - If YES → Continue
4. Click **App passwords**
5. Select: **Mail** & **Windows Computer**
6. Google generates NEW 16-character code
7. Copy it exactly (with spaces): `xxxx xxxx xxxx xxxx`
8. Test with Python SMTP script above
9. If works, update on Render

---

### Case 4: Network/Firewall blocked

**Evidence:**
- ❌ Error: "Connection refused"
- ❌ Error: "Operation timed out"
- ❌ Error: "Host unreachable"

**Fix:**

Test if Gmail is reachable:
```bash
# Test 1: Ping Gmail
ping smtp.gmail.com

# Test 2: Telnet to SMTP port
telnet smtp.gmail.com 587

# Should show something like:
# Connected to gmail-smtp-msa.l.google.com.
# Escape character is '^]'.
# 220 smtp.google.com ESMTP
```

**Solutions:**
- Try from different network (mobile hotspot)
- Disable VPN if using one
- Check company firewall settings
- For Render: Not a common issue (Render has outbound)

---

## Complete Test Sequence

Run these in order:

```bash
# 1. Test raw Python + Gmail
python3 << 'EOF'
import smtplib
try:
    s = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    s.starttls()
    s.login('abbasalitmk@gmail.com', 'ekyg xkml rdtl ddyp')
    print("✓ PYTHON SMTP WORKS")
    s.quit()
except Exception as e:
    print(f"✗ PYTHON SMTP FAILED: {e}")
EOF

# 2. Test Django local
python manage.py diagnose_email

# 3. Test environment variables
echo "EMAIL_HOST_USER: $EMAIL_HOST_USER"
echo "EMAIL_HOST_PASSWORD: $EMAIL_HOST_PASSWORD"

# 4. Check if vars from defaults or env
python manage.py shell << 'EOF'
from django.conf import settings
import os
print(f"From env: {bool(os.environ.get('EMAIL_HOST_USER'))}")
print(f"Value: {settings.EMAIL_HOST_USER}")
EOF

# 5. If all above work, issue is Render
# → Go to Render dashboard and add environment variables
```

---

## Render Environment Variable Setup

**If local works but Render doesn't:**

```
Render Dashboard
  ↓
ulsavam_backend (service)
  ↓
Environment (tab)
  ↓
+ Add Environment Variable
  ├─ Key: EMAIL_HOST_USER
  └─ Value: abbasalitmk@gmail.com
  ↓
+ Add Environment Variable
  ├─ Key: EMAIL_HOST_PASSWORD
  └─ Value: ekyg xkml rdtl ddyp
  ↓
Save
  ↓
Wait 5-10 minutes (status: "Updating...")
  ↓
Status changes to "Live"
  ↓
TEST: curl -X POST https://...
```

---

## Decision Tree

```
Test Python SMTP?
├─ ✓ WORKS
│  └─ Test Django locally?
│     ├─ ✓ WORKS
│     │  └─ ISSUE IS RENDER
│     │     Fix: Add env vars to Render
│     │
│     └─ ✗ FAILS
│        └─ ISSUE IS DJANGO CONFIG
│           Fix: Check settings.py
│
└─ ✗ FAILS
   └─ ISSUE IS GMAIL CREDENTIALS
      └─ Regenerate app password
         OR
         Check 2-FA enabled
```

---

## Quick Commands Reference

```bash
# Test 1: Python SMTP (copy-paste ready)
python3 << 'EOF'
import smtplib
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('abbasalitmk@gmail.com', 'ekyg xkml rdtl ddyp')
print("✓ OK")
s.quit()
EOF

# Test 2: Django diagnose
python manage.py diagnose_email

# Test 3: Check env vars exist
printenv | grep EMAIL

# Test 4: Django shell check
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST_USER)
>>> print(settings.EMAIL_HOST_PASSWORD)
>>> exit()

# Test 5: Render curl test (after deploying)
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "test@gmail.com", "method": "email"}'
```

---

## Most Common Fixes (In Order)

1. **Regenerate Gmail app password** (40% of issues)
   - https://myaccount.google.com/security → App passwords

2. **Add environment variables to Render** (35% of issues)
   - Render Dashboard → Environment → Add EMAIL_HOST_USER & EMAIL_HOST_PASSWORD

3. **Enable 2-Step Verification on Gmail** (15% of issues)
   - https://myaccount.google.com/security → 2-Step Verification

4. **Check settings.py is correct** (5% of issues)
   - Verify EMAIL_BACKEND, HOST, PORT, TLS

5. **Network/Firewall issue** (5% of issues)
   - Test from mobile hotspot / disable VPN

---

**Next Step:** Run `python manage.py diagnose_email` and tell me what error you get! 🚀
