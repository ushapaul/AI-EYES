# 🔐 SendGrid New Account Setup Guide

## 📋 Overview
This guide will help you create a new SendGrid account and update your AI Eyes system configuration.

---

## 🆕 Step 1: Create New SendGrid Account

### 1.1 Sign Up
1. Go to: **https://signup.sendgrid.com/**
2. Fill in your details:
   - Email address (use the same: `praveenkumarnaik14@gmail.com`)
   - Password (create a strong password)
   - Company name: "AI Eyes Security" or your choice
   - Website: Leave blank or use any placeholder
3. Click **"Create Account"**
4. Verify your email address (check inbox for verification email)

### 1.2 Complete Account Setup
1. Login to SendGrid dashboard: **https://app.sendgrid.com/**
2. You might see an onboarding wizard - complete it or skip

---

## 🔑 Step 2: Create API Key

### 2.1 Navigate to API Keys
1. In SendGrid dashboard, go to: **Settings** → **API Keys**
   - Direct link: https://app.sendgrid.com/settings/api_keys
2. Click **"Create API Key"** button

### 2.2 Configure API Key
1. **API Key Name**: Enter a name like `AI_Eyes_Security_System`
2. **API Key Permissions**: Select **"Full Access"** (recommended for ease)
   - Alternatively, select "Restricted Access" and enable only:
     - ✅ Mail Send (Full Access)
3. Click **"Create & View"**

### 2.3 Copy Your API Key
⚠️ **IMPORTANT**: Copy the API key **NOW**! It looks like:
```
SG.xxxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```
You will **NEVER** be able to see it again after closing this window!

📋 Save it in a secure location temporarily (like Notepad)

---

## ✉️ Step 3: Verify Sender Email

### 3.1 Single Sender Verification (Recommended for Testing)
1. Go to: **Settings** → **Sender Authentication** → **Single Sender Verification**
   - Direct link: https://app.sendgrid.com/settings/sender_auth/senders
2. Click **"Create New Sender"**
3. Fill in the form:
   - **From Name**: `AI Eyes Security System`
   - **From Email Address**: `praveenkumarnaik14@gmail.com` (or your email)
   - **Reply To**: Same as above
   - **Company Address**: Enter any address
   - **City, State, Zip, Country**: Fill as required
4. Click **"Create"**

### 3.2 Verify Email
1. Check your email inbox (`praveenkumarnaik14@gmail.com`)
2. Open email from SendGrid: "Please Verify Your Sender Email Address"
3. Click the **verification link**
4. Confirm on the verification page
5. Status should show **"Verified"** in SendGrid dashboard

---

## 🔧 Step 4: Update Environment Files

### 4.1 Files to Update
You need to update **2 files**:
1. `backend\.env`
2. `.env` (in root folder)

### 4.2 Update SendGrid Configuration

Replace these lines with your **NEW** values:

```env
# SendGrid API Configuration
SENDGRID_API_KEY=SG.your_new_api_key_here
SENDGRID_FROM_EMAIL=praveenkumarnaik14@gmail.com
SENDGRID_FROM_NAME=AI Eyes Security System

# Alert Recipients (comma-separated email addresses)
ALERT_RECIPIENTS=praveenkumarnaik14@gmail.com

# Email Alerts Configuration
ENABLE_EMAIL_ALERTS=true
```

---

## ✅ Step 5: Test Your Configuration

### 5.1 Test Script
Run the test script to verify SendGrid is working:

```powershell
cd backend
python test_sendgrid_email.py
```

### 5.2 Expected Output
```
✅ Test email sent successfully!
Check your inbox: praveenkumarnaik14@gmail.com
```

### 5.3 Check Your Email
- Check inbox (should arrive in 30-60 seconds)
- Check Spam/Junk folder if not in inbox
- Email subject: "AI Eyes Security Test"

---

## 🚨 Troubleshooting

### Issue: API Key Not Working
- ✅ Make sure you copied the **entire** API key (starts with `SG.`)
- ✅ No extra spaces before or after the key
- ✅ API key has **Mail Send** permissions

### Issue: Email Not Received
- ✅ Verify sender email is **verified** in SendGrid
- ✅ Check spam/junk folder
- ✅ Wait 1-2 minutes (SendGrid can be slow initially)

### Issue: "Unauthorized" Error
- ✅ API key is correct and has Full Access or Mail Send permission
- ✅ Restart your Python application after updating .env

### Issue: "From email does not match verified sender"
- ✅ `SENDGRID_FROM_EMAIL` in .env must exactly match your verified sender email
- ✅ Email is verified in SendGrid dashboard (green checkmark)

---

## 📊 SendGrid Free Tier Limits

✅ **Free Forever Plan**:
- 100 emails per day
- 2,000 contacts
- Perfect for your AI Eyes system!

---

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| SendGrid Login | https://app.sendgrid.com/ |
| API Keys | https://app.sendgrid.com/settings/api_keys |
| Sender Verification | https://app.sendgrid.com/settings/sender_auth/senders |
| Email Activity | https://app.sendgrid.com/email_activity |
| Documentation | https://docs.sendgrid.com/ |

---

## 📝 Quick Checklist

- [ ] Create SendGrid account
- [ ] Verify email address
- [ ] Create API key (Full Access)
- [ ] Copy API key to safe location
- [ ] Verify sender email in SendGrid
- [ ] Update `backend\.env` with new API key
- [ ] Update `.env` (root) with new API key
- [ ] Run test script: `python test_sendgrid_email.py`
- [ ] Verify test email received
- [ ] Delete old API key from old account (if accessible)

---

## 🎯 Next Steps After Setup

Once SendGrid is configured and tested:

1. **Start your surveillance system**:
   ```powershell
   cd backend
   python run_live_surveillance.py
   ```

2. **Email alerts will be sent automatically** when:
   - Unknown person detected
   - Suspicious activity detected
   - Manual alert triggered from dashboard

---

## 💡 Tips

1. **Save your API key securely** - use a password manager
2. **Don't share your API key** - it's like a password
3. **Monitor your usage** in SendGrid dashboard
4. **Check Email Activity** tab to debug delivery issues
5. **Add to contacts** - Add no-reply@sendgrid.net to contacts to avoid spam

---

**Created**: October 18, 2025  
**Status**: Ready to use ✅
