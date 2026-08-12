# Email OTP Troubleshooting Guide

## 🔍 Diagnose the Issue

### Step 1: Test Email Configuration Locally

Run the email test command:
```bash
python manage.py test_email
```

This will:
- ✅ Check your email settings
- ✅ Verify environment variables
- ✅ Attempt to send a test email
- ✅ Provide specific error messages

---

## ❌ Common Issues & Solutions

### Issue 1: "Authentication failed" / "535" Error

**Problem:** Gmail rejected the credentials

**Solutions:**

1. **Verify App Password is Correct**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Scroll to "App passwords"
   - Make sure you have the EXACT 16-character code
   - It should look like: `ekyg xkml rdtl ddyp` (without dashes)

2. **Ensure 2-Factor Authentication is Enabled**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Find "2-Step Verification"
   - Click to enable it (if not already enabled)
   - You may need to verify with phone

3. **Regenerate App Password**
   - Remove the old app password
   - Generate a new one
   - Copy the 16-character code (no spaces)
   - Update on Render

### Issue 2: Environment Variables Not Set on Render

**Problem:** Settings default to local credentials that don't work on Render

**Solution:**

On Render Dashboard:
1. Go to your **ulsavam_backend** web service
2. Click **Environment** in left sidebar
3. Add/Update these variables:
   ```
   EMAIL_HOST_USER = abbasalitmk@gmail.com
   EMAIL_HOST_PASSWORD = ekyg xkml rdtl ddyp
   ```
4. Click **Save**
5. Service auto-redeploys (5-10 minutes)
6. Test again

**Verify they're set:**
```bash
# Local development (check if vars exist)
echo $EMAIL_HOST_USER
echo $EMAIL_HOST_PASSWORD
```

### Issue 3: "Connection refused" / "timed out"

**Problem:** Cannot connect to Gmail SMTP server

**Solutions:**

1. **Check Settings are Correct**
   ```python
   EMAIL_HOST = 'smtp.gmail.com'  # Must be exactly this
   EMAIL_PORT = 587               # Must be 587 (not 465 or 25)
   EMAIL_USE_TLS = True           # Must be True
   ```

2. **Check Internet Connection**
   - Verify you can reach smtp.gmail.com
   - ```bash
     ping smtp.gmail.com
     telnet smtp.gmail.com 587
     ```

3. **Check Firewall/Network**
   - Some networks block port 587
   - Try from mobile hotspot to test
   - VPN might interfere (try disabling)

4. **Test with Telnet**
   ```bash
   telnet smtp.gmail.com 587
   ```
   Should show: `220 smtp.google.com ESMTP...`

### Issue 4: "SMTPAuthenticationError: string index out of range"

**Problem:** Gmail app password has issues or spaces/formatting wrong

**Solution:**

1. **Remove Spaces from App Password**
   - App password might be: `ekyg xkml rdtl ddyp`
   - Remove all spaces: `eygxkmlrdtlddyp` ❌ (this is wrong)
   - Actually use with spaces: `ekyg xkml rdtl ddyp` ✅

2. **Use Exactly as Provided**
   - Don't modify or shorten the password
   - Copy all 16 characters (including spaces)
   - Paste into Render environment variable

3. **Regenerate if Unsure**
   - Delete the old app password
   - Generate new one
   - Use immediately (before expiry)

### Issue 5: Email Goes to Spam

**Problem:** Emails arrive but in spam/junk folder

**Solutions:**

1. **Mark as Not Spam**
   - Check spam folder
   - Right-click email → "Mark as not spam"
   - Gmail will learn to send future emails to inbox

2. **Add to Contacts**
   - Add `noreply@ulsavam.com` to your contacts
   - Gmail prioritizes known senders

3. **Check SPF/DKIM Records**
   - If using custom domain, configure SPF/DKIM
   - For now, Gmail-to-Gmail usually works fine

4. **Use Corporate Domain Email**
   - Instead of personal Gmail
   - Corporate Google Workspace accounts more trusted

### Issue 6: Emails Sending But Users Not Receiving

**Problem:** No error but emails don't arrive

**Solutions:**

1. **Check Recipients Typo**
   - Verify email addresses are spelled correctly
   - Check test email address in test_email command

2. **Check OTP Email Service Logic**
   - Verify `send_otp_email()` is being called
   - Check Django logs for send_mail calls
   - Test with test_email command first

3. **Verify User Email is Set**
   - User must have valid email in database
   - Check: `SELECT email FROM users_user WHERE id=1;`

4. **Check Rate Limiting**
   - Gmail has rate limits (per IP/account)
   - If sending 100s of emails, might be throttled
   - Space out requests or use SendGrid

---

## 🚀 Complete Fix (Step by Step)

### If Nothing Works, Follow This:

**Step 1: Generate Fresh App Password**
```
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if needed)
3. Go to "App passwords"
4. Select Mail & Windows Computer
5. Copy the 16-character code (e.g., "ekyg xkml rdtl ddyp")
```

**Step 2: Update Render Environment**
```
1. Render Dashboard → ulsavam_backend
2. Environment → Edit Variables
3. Set: EMAIL_HOST_USER = abbasalitmk@gmail.com
4. Set: EMAIL_HOST_PASSWORD = ekyg xkml rdtl ddyp
5. Save → Auto-redeploy
```

**Step 3: Test Locally First**
```bash
# Make sure you have the same environment variables
export EMAIL_HOST_USER="abbasalitmk@gmail.com"
export EMAIL_HOST_PASSWORD="ekyg xkml rdtl ddyp"

# Test email
python manage.py test_email

# If successful, proceed to Step 4
```

**Step 4: Test on Render**
```bash
# After Render redeploys (5-10 min)
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "your-email@gmail.com", "method": "email"}'

# Check your email inbox
# Look for OTP code
```

**Step 5: Verify OTP Works**
```bash
# Once you receive email with OTP
OTP="123456"  # Replace with code from email

curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "your-email@gmail.com", "code": "'$OTP'"}'

# Should return access token
```

---

## 📊 Debug Checklist

Go through this checklist:

- [ ] Email backend is SMTP: `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
- [ ] EMAIL_HOST = 'smtp.gmail.com'
- [ ] EMAIL_PORT = 587
- [ ] EMAIL_USE_TLS = True
- [ ] EMAIL_HOST_USER is set (in env or defaults)
- [ ] EMAIL_HOST_PASSWORD is set (in env or defaults)
- [ ] App password is 16 characters (with spaces)
- [ ] 2-Factor Authentication is enabled on Gmail
- [ ] Environment variables updated on Render
- [ ] Render service redeployed after env change
- [ ] test_email command runs without errors
- [ ] Test email received in inbox (or spam folder)
- [ ] OTP email template renders correctly

---

## 🧪 Alternative Testing Methods

### Method 1: Using Django Shell

```bash
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

# Test send
send_mail(
    subject='Test Email',
    message='This is a test.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@gmail.com'],
)

# Exit
exit()
```

### Method 2: Using Python SMTP Direct

```python
import smtplib
from email.mime.text import MIMEText

# Test SMTP connection
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('abbasalitmk@gmail.com', 'ekyg xkml rdtl ddyp')
    
    msg = MIMEText('Test message')
    msg['Subject'] = 'Test'
    msg['From'] = 'abbasalitmk@gmail.com'
    msg['To'] = 'your-email@gmail.com'
    
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Method 3: Using Gmail Web Portal

1. Go to Gmail → Settings → Forwarding and POP/IMAP
2. Enable IMAP
3. Try logging in with app password in email client
4. If that works, Django will work too

---

## 🔒 Gmail Security Settings

Make sure these are configured:

1. **2-Step Verification**: ENABLED
2. **Less secure apps**: DISABLED (app passwords are more secure)
3. **App passwords**: ENABLED & CONFIGURED
4. **Recent security events**: No suspicious activity
5. **Connected apps & sites**: Review if needed

**Link:** https://myaccount.google.com/security

---

## 📧 Alternative Email Services

If Gmail doesn't work, use alternatives:

### Option 1: SendGrid (Recommended)
- Free tier: 100 emails/day
- Reliable for transactional emails
- Better deliverability

Setup:
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'your-sendgrid-key'
```

### Option 2: Mailgun
- Free tier: 5,000 emails/month
- Great for startups
- Easy integration

### Option 3: AWS SES
- Free tier: 62,000 emails/month
- Professional grade
- More setup required

### Option 4: Render Email Service
- Coming soon on Render
- Native integration

---

## 📋 Render Environment Setup (Screenshots)

1. Go to Render Dashboard
2. Select your **ulsavam_backend** service
3. Click **Environment** tab
4. Add new variable:
   - **Key**: `EMAIL_HOST_USER`
   - **Value**: `abbasalitmk@gmail.com`
5. Add another:
   - **Key**: `EMAIL_HOST_PASSWORD`
   - **Value**: `ekyg xkml rdtl ddyp` (your app password)
6. Click **Save**
7. Service auto-redeploys (5-10 minutes)
8. Status changes to "Live" when ready

---

## 🆘 Still Not Working?

### Check These Logs

**Render Logs:**
1. Render Dashboard → ulsavam_backend
2. Click **Logs** tab
3. Look for errors starting with "SMTPException" or "AuthenticationError"
4. Copy full error message

**Local Logs:**
```bash
tail -f /var/log/mail.log  # Linux
```

### Get Help

**Share these details when asking for help:**
1. Full error message from `test_email` command
2. Environment variables you've set (don't share passwords!)
3. Whether you're testing locally or on Render
4. Screenshot of Gmail security settings

---

## ✅ Success Indicators

When it's working:
1. ✅ `test_email` command completes without errors
2. ✅ Test email arrives in inbox within seconds
3. ✅ OTP request returns 200 OK
4. ✅ Email with OTP arrives within a minute
5. ✅ OTP verification returns access token
6. ✅ Users can login with OTP flow

---

## 📞 Support

**Test Command:**
```bash
python manage.py test_email
```

**Live Testing:**
```bash
# On Render (after deployment)
curl -X POST https://ulsavam-backend.onrender.com/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "test@gmail.com", "method": "email"}'
```

**Next Step:** Once you fix this, OTP emails will work perfectly! 🎉
