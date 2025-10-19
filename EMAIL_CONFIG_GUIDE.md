# Environment Variables Configuration Guide

## Current Email Configuration

All email addresses are currently set to **fyrentech@gmail.com** for testing purposes.

## Files to Update

### 1. Root `.env` File
**Location**: `C:\Users\23rah\OneDrive\Desktop\AI eyes\.env`

```env
# Frontend Environment Variables (VITE_ prefix required)
VITE_MANAGER_PRAJWAL_EMAIL=fyrentech@gmail.com
VITE_FARMER_BASAVA_EMAIL=fyrentech@gmail.com
VITE_OWNER_RAJASEKHAR_EMAIL=fyrentech@gmail.com

# Backend versions (without VITE_ prefix)
MANAGER_PRAJWAL_EMAIL=fyrentech@gmail.com
FARMER_BASAVA_EMAIL=fyrentech@gmail.com
OWNER_RAJASEKHAR_EMAIL=fyrentech@gmail.com
```

### 2. Backend `.env` File
**Location**: `C:\Users\23rah\OneDrive\Desktop\AI eyes\backend\.env`

```env
# Authorized Persons
MANAGER_PRAJWAL_EMAIL=fyrentech@gmail.com
FARMER_BASAVA_EMAIL=fyrentech@gmail.com
OWNER_RAJASEKHAR_EMAIL=fyrentech@gmail.com
```

## How to Update with Real Email Addresses

### Step 1: Get Actual Email Addresses
Contact each person and get their email addresses:
- **Manager Prajwal**: ___________________@_______
- **Farmer Basava**: ___________________@_______
- **Owner Rajasekhar**: ___________________@_______

### Step 2: Update Root `.env`
```env
# Example with real emails
VITE_MANAGER_PRAJWAL_EMAIL=prajwal.manager@farmcompany.com
VITE_FARMER_BASAVA_EMAIL=basava.farmer@farmcompany.com
VITE_OWNER_RAJASEKHAR_EMAIL=rajasekhar.owner@farmcompany.com

MANAGER_PRAJWAL_EMAIL=prajwal.manager@farmcompany.com
FARMER_BASAVA_EMAIL=basava.farmer@farmcompany.com
OWNER_RAJASEKHAR_EMAIL=rajasekhar.owner@farmcompany.com
```

### Step 3: Update Backend `.env`
```env
# Same emails in backend
MANAGER_PRAJWAL_EMAIL=prajwal.manager@farmcompany.com
FARMER_BASAVA_EMAIL=basava.farmer@farmcompany.com
OWNER_RAJASEKHAR_EMAIL=rajasekhar.owner@farmcompany.com
```

### Step 4: Restart Both Servers
After updating `.env` files, restart:

**Frontend:**
```powershell
cd "C:\Users\23rah\OneDrive\Desktop\AI eyes"
npm run dev
```

**Backend:**
```powershell
cd "C:\Users\23rah\OneDrive\Desktop\AI eyes\backend"
python app_simple.py
```

## Testing the Configuration

### Test Each Escalation Button:

1. **Open Dashboard** → Click on any alert → "View Details"

2. **Test Manager Prajwal Button**:
   - Click "Manager Prajwal" button
   - Check if email arrives at Prajwal's address
   - Verify email content shows correct recipient name

3. **Test Farmer Basava Button**:
   - Click "Farmer Basava" button
   - Check if email arrives at Basava's address
   - Verify email content shows correct recipient name

4. **Test Owner Rajasekhar Button**:
   - Click "Owner Rajasekhar" button
   - Check if email arrives at Rajasekhar's address
   - Verify email content shows correct recipient name

## Current Status

✅ **SendGrid Configured**: fyrentech@gmail.com (sending from)
✅ **API Key Active**: SG.-2WoT9NoQbGsoqHcbIN3-w...
⚠️ **All Recipients**: Currently same email (fyrentech@gmail.com) - needs updating
✅ **Email Templates**: Professional HTML with images
✅ **Escalation Feature**: Fully implemented and ready

## Important Notes

### Why VITE_ Prefix?
- **Frontend (Vite)**: Requires `VITE_` prefix for environment variables
- **Backend (Flask)**: Uses variables without prefix
- **Both needed**: Keep both versions in root `.env` for consistency

### Email Delivery
- Emails sent via **SendGrid** (reliable, professional)
- Includes alert **screenshot** as attachment
- Shows **confidence score**, **location**, **timestamp**
- Professional formatting with your company branding

### Troubleshooting

**If emails not arriving:**
1. Check SendGrid API key is valid
2. Verify email addresses are correct (no typos)
3. Check spam/junk folders
4. Look at backend console for error messages
5. Test SendGrid with: `python backend/test_sendgrid_email.py`

**If wrong email shown in UI:**
1. Clear browser cache (Ctrl + Shift + R)
2. Restart frontend dev server
3. Check `.env` file has VITE_ prefix for frontend variables

## Security Recommendations

### Protect `.env` Files
- ✅ Already in `.gitignore` - not committed to git
- ❌ Never share `.env` files publicly
- ❌ Never commit API keys to repositories
- ✅ Use environment variables in production

### Email Security
- Use **SendGrid** (already configured) instead of SMTP
- Enable **2FA** on SendGrid account
- Rotate API keys periodically
- Monitor email sending quota
- Review SendGrid activity logs regularly

## Production Deployment

When deploying to production server:

```env
# Use production email addresses
VITE_MANAGER_PRAJWAL_EMAIL=prajwal@yourcompany.com
VITE_FARMER_BASAVA_EMAIL=basava@yourcompany.com
VITE_OWNER_RAJASEKHAR_EMAIL=rajasekhar@yourcompany.com

# Professional from address
SENDGRID_FROM_EMAIL=alerts@yourcompany.com
SENDGRID_FROM_NAME=AI Eyes Security System

# Production SendGrid key
SENDGRID_API_KEY=<production_api_key>
```

---

**Last Updated**: January 2025
**System**: AI Eyes Security Surveillance
**Email Provider**: SendGrid (fyrentech@gmail.com)
**Status**: ✅ Ready for Testing → ⚠️ Update with real emails
