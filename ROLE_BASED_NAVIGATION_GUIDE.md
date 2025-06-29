# Role-Based Navigation Guide

## Overview
The global navigation now supports role-based access control, showing different navigation options based on user roles.

## Roles with Admin Access
Users with the following roles will see the **Admin** link in the navigation:
- `admin` - Full administrative access
- `manager` - Management level access
- `supervisor` - Supervisory level access

## Setup Instructions

### 1. Add Role Column to Profiles Table
Run the SQL script `add_role_column.sql` in your Supabase SQL editor to:
- Add a `role` column to the profiles table
- Set default role as 'user'
- Update your test user to 'admin' role

### 2. Role Assignment
You can assign roles to users in several ways:

#### Via SQL (Supabase SQL Editor):
```sql
-- By email
UPDATE profiles SET role = 'admin' WHERE email = 'user@example.com';

-- By user ID
UPDATE profiles SET role = 'manager' WHERE id = 'user-uuid-here';
```

#### Via Supabase Dashboard:
1. Go to Table Editor > profiles
2. Find the user row
3. Edit the `role` column
4. Save changes

### 3. Role Verification
Check current user roles:
```sql
SELECT id, email, display_name, role FROM profiles;
```

## How It Works

### Navigation Logic
- The `global-nav-v2.js` fetches user role from the profiles table
- If role is 'admin', 'manager', or 'supervisor', the Admin link appears
- The Admin link is styled in red to distinguish it from other nav items
- Regular users (role 'user' or null) won't see the Admin link

### Technical Implementation
1. **getDisplayName()** function now returns both displayName and userRole
2. **renderNav()** function accepts userRole parameter and conditionally renders admin link
3. **setupNav()** function passes both values to the render function

## Admin Page Access
- Admin link points to `admin.html`
- Only visible to users with elevated roles
- Includes visual separator (border-left) to distinguish from other nav items

## Security Notes
- This is **client-side role checking** for UI purposes only
- **Always implement server-side role validation** in your backend/API
- Use Supabase Row Level Security (RLS) policies for database access control
- Consider adding role-based route protection in your application

## Testing
1. Set your user role to 'admin' using the SQL script
2. Refresh any page with global navigation
3. Verify the Admin link appears in red
4. Change role back to 'user' and verify link disappears

## Role Hierarchy Suggestion
- `user` - Default role, basic access
- `supervisor` - Team/department oversight
- `manager` - Multi-department management  
- `admin` - Full system administration

You can customize the role names and hierarchy in the `renderNav()` function as needed for your organization.
