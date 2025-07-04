# Admin Debug Setup

## Overview
The debug information in the Spaces section is now hidden from regular users and only visible to administrators.

## Admin Access Methods

### Method 1: Admin Email List
Add your admin email addresses to the `adminEmails` array in `SpacesList.tsx`:

```javascript
const adminEmails = ['admin@example.com', 'your-admin-email@example.com'];
```

### Method 2: Environment Variable (Development)
Set the environment variable to enable debug mode during development:

```bash
# In your .env.local file
VITE_ADMIN_DEBUG=true
```

## Debug Information Shown
When visible to admins, the debug panel shows:
- User ID
- User Email
- Spaces count
- Loading state
- Refreshing state
- Error messages
- JSON dump of spaces data

## Security Notes
- Debug info is completely hidden from regular users
- Only shows for users with emails in the `adminEmails` list
- Can be temporarily enabled via environment variable for development
- Panel clearly labeled as "(Admin Only)"

## To Configure Your Admin Access
1. Edit `Website/src/components/SpacesList.tsx`
2. Find the `adminEmails` array
3. Replace `'admin@example.com'` with your actual admin email
4. Save the file

The debug panel will then be visible when you're logged in with your admin email address. 