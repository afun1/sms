# Asset Security System Documentation

## Overview

This document outlines the comprehensive asset security system implemented for user-based access control to Supabase storage assets. The system provides secure, hierarchical access to assets based on user roles and organizational structure.

## Key Features

### 🔐 Security Features
- **Row Level Security (RLS)** - All storage operations are protected by RLS policies
- **User-based path structure** - Assets are organized by user ID in storage
- **Hierarchical access control** - Managers and supervisors can access their team's assets
- **Role-based permissions** - Four distinct user roles with different access levels
- **Automatic role assignment** - New users are automatically assigned a default role

### 👥 User Roles

1. **User** - Basic role with access to own assets only
2. **Manager** - Can access assets of assigned team members
3. **Supervisor** - Can access assets of assigned team members and their managers
4. **Admin** - Full system access to all assets and user management

### 🗂️ Asset Organization

Assets are stored using the following path structure:
```
{user_id}/{filename}
```

This ensures that each user's assets are isolated and access can be properly controlled.

## Database Schema

### user_roles Table

```sql
CREATE TABLE public.user_roles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'manager', 'supervisor', 'admin')),
    manager_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    supervisor_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);
```

### Storage Bucket Configuration

- **Bucket Name**: `assets`
- **Public Access**: Disabled (requires authentication)
- **File Size Limit**: 50MB
- **Allowed MIME Types**: Images, documents, videos, audio files
- **RLS**: Enabled on `storage.objects`

## Access Control Policies

### Storage Policies

1. **View Access**: Users can view their own assets and assets they have hierarchical access to
2. **Upload Access**: Users can only upload to their own directory
3. **Update Access**: Users can only update their own assets
4. **Delete Access**: Users can delete their own assets and assets they have hierarchical access to

### RLS Implementation

The system uses a custom function `can_access_user_assets(target_user_id UUID)` that:
- Allows users to access their own assets
- Allows admins to access all assets
- Allows managers to access their team members' assets
- Allows supervisors to access their team and managers' assets

## Setup Instructions

### 1. Run the Security Setup SQL

Execute the SQL file `setup_assets_bucket_security.sql` in your Supabase SQL Editor:

```bash
# This will create:
# - Assets bucket with proper configuration
# - user_roles table with RLS
# - Storage policies for secure access
# - Helper functions and triggers
# - Sample admin user (update email as needed)
```

### 2. Update Application Code

Ensure your application code follows the correct path structure:

**Upload Example:**
```javascript
const { data: { user } } = await supabase.auth.getUser();
const filePath = `${user.id}/${filename}`;
const { error } = await supabase.storage
  .from('assets')
  .upload(filePath, file);
```

**List Files Example:**
```javascript
const { data: { user } } = await supabase.auth.getUser();
const { data: files } = await supabase.storage
  .from('assets')
  .list(user.id);
```

**Delete Example:**
```javascript
const { data: { user } } = await supabase.auth.getUser();
const filePath = `${user.id}/${filename}`;
const { error } = await supabase.storage
  .from('assets')
  .remove([filePath]);
```

### 3. Assign User Roles

Use the admin panel (`admin_asset_security.html`) to:
- Assign roles to users
- Set up manager/supervisor relationships
- Monitor system usage and security

## Testing and Validation

### Security Test Suite

Use `test_asset_security.html` to validate:
- Bucket configuration
- User role assignments
- Upload security
- Access control policies
- Delete permissions
- Path structure compliance

### Test Scenarios

1. **User Isolation**: Verify users can only access their own assets
2. **Manager Access**: Confirm managers can access team member assets
3. **Supervisor Access**: Verify supervisors have appropriate hierarchical access
4. **Admin Access**: Confirm admins have full system access
5. **Upload Security**: Test that uploads use correct path structure
6. **Delete Security**: Verify delete operations respect access controls

## Administration

### Admin Dashboard Features

The admin dashboard (`admin_asset_security.html`) provides:

- **System Statistics**: User counts, asset counts, role distribution
- **User Management**: Add, edit, delete user roles
- **Asset Overview**: Monitor asset usage and storage
- **Maintenance Tools**: Database validation, policy testing
- **Role Assignment**: Manage hierarchical relationships

### Common Administrative Tasks

1. **Add New User Role**:
   - User must first sign up through normal authentication
   - Admin assigns role through dashboard
   - Manager/supervisor relationships configured as needed

2. **Change User Role**:
   - Update role through admin dashboard
   - Existing assets remain accessible based on new role
   - Access permissions update immediately

3. **Remove User Access**:
   - Delete user role record
   - User loses access to organizational assets
   - Personal assets remain accessible

## Security Best Practices

### For Developers

1. **Always use user-based paths** for storage operations
2. **Validate user authentication** before any storage operation
3. **Use the provided helper functions** for access control checks
4. **Test with different user roles** to ensure proper isolation
5. **Monitor storage usage** and implement cleanup procedures

### For Administrators

1. **Regularly audit user roles** and access permissions
2. **Monitor asset storage usage** and implement quotas as needed
3. **Review access logs** for unusual activity
4. **Keep role assignments current** with organizational changes
5. **Test backup and recovery procedures** for asset data

## Troubleshooting

### Common Issues

1. **Upload Failures**:
   - Check user authentication status
   - Verify path structure includes user ID
   - Confirm file type is allowed
   - Check file size limits

2. **Access Denied Errors**:
   - Verify user has proper role assignment
   - Check manager/supervisor relationships
   - Confirm RLS policies are active
   - Test with admin account to isolate issues

3. **Missing Assets**:
   - Verify correct user directory is being queried
   - Check if assets were uploaded with old path structure
   - Confirm storage bucket permissions

### Diagnostic Tools

1. **Test Security Page**: Comprehensive validation of all security features
2. **Admin Dashboard**: System-wide view of users, roles, and assets
3. **Browser Console**: Detailed error messages from Supabase client
4. **Supabase Logs**: Server-side operation logs and policy evaluations

## Migration from Existing Systems

If you have existing assets not following the user-based path structure:

1. **Inventory existing assets** and their ownership
2. **Create migration script** to move assets to correct paths
3. **Update database references** to new file paths
4. **Test access with various user roles** before going live
5. **Keep backup** of original structure until migration is verified

## Performance Considerations

- **Storage queries are filtered by user ID** which is indexed for performance
- **RLS policies are evaluated efficiently** using the provided helper function
- **Asset listing operations** scale linearly with user's asset count, not total assets
- **Consider pagination** for users with large numbers of assets

## Future Enhancements

Potential improvements to consider:

1. **Asset sharing** between users with explicit permissions
2. **Folder organization** within user directories
3. **Asset tagging** and advanced search capabilities
4. **Audit logging** for all asset operations
5. **Automated cleanup** of unused or old assets
6. **Storage quotas** per user or role
7. **Asset versioning** and revision history

## Support and Maintenance

- **Database schema changes** should be tested in development environment first
- **Policy updates** require careful testing to avoid breaking existing access
- **Regular monitoring** of storage usage and performance metrics
- **Backup procedures** should include both database and storage assets
- **Documentation updates** when organizational structure changes

---

*This documentation covers the complete asset security system. For specific implementation details, refer to the source code files and SQL setup scripts.*
