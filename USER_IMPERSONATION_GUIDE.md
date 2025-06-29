# User Impersonation System - GHL Style Implementation Guide

## 🎭 Overview

This system provides a professional, GHL-style user impersonation feature that allows administrators to seamlessly log in as other users for customer support purposes. The implementation focuses on user experience, security, and ease of use.

## ✨ Key Features

### 🔐 Security & Permissions
- **Hierarchical Access Control**: Role-based impersonation with proper hierarchy
  - **Admins**: Can impersonate any user in the system
  - **Supervisors**: Can impersonate managers assigned to them and users under those managers
  - **Managers**: Can impersonate only users directly assigned to them
  - **Users**: Cannot impersonate other users
- **Session Management**: Original user context is preserved and can be restored
- **Audit Trail**: All impersonation actions are logged with timestamps

### 🎨 User Experience
- **GHL-Style Interface**: Clean, professional modal similar to GoHighLevel
- **Instant Search**: Real-time filtering of users by name, email, or role
- **Keyboard Navigation**: Full keyboard support (Arrow keys, Enter, Escape)
- **Visual Feedback**: Clear impersonation banner and role-based color coding

### 📱 UI Components
- **Impersonation Banner**: Prominent top banner when impersonating
- **Search Modal**: Professional user selection interface
- **Role Badges**: Color-coded role indicators
- **One-Click Return**: Easy "Switch to my account" button

## 🚀 Getting Started

### Installation

1. **Include the JavaScript file**:
```html
<script src="user_impersonation.js"></script>
```

2. **Add the impersonation button** to your admin interface:
```html
<button onclick="userImpersonation.openImpersonationModal()">
    🎭 Log In As User
</button>
```

3. **Ensure user data is available**:
```javascript
// The system expects window.allUsers to contain user data
window.allUsers = [
    {
        id: 'user-1',
        first_name: 'John',
        last_name: 'Smith',
        email: 'john.smith@company.com',
        role: 'manager',
        display_name: 'John Smith'
    }
    // ... more users
];
```

### Basic Usage

```javascript
// Open impersonation modal
userImpersonation.openImpersonationModal();

// Impersonate specific user
userImpersonation.impersonateUser('user-id-123');

// Switch back to original user
userImpersonation.switchBackToOriginalUser();

// Check if current user can impersonate
if (userImpersonation.canImpersonate()) {
    // Show impersonation controls
    // Admin: Can impersonate anyone
    // Supervisor: Can impersonate their managers and users under those managers  
    // Manager: Can impersonate users assigned to them
    // User: Cannot impersonate (will return false)
}
```

## 🎯 How It Works

### Hierarchical Permission System

The system implements a role-based hierarchy for impersonation permissions:

#### 🔴 **Admin Users**
- **Full Access**: Can impersonate any user in the system
- **No Restrictions**: See all users regardless of hierarchy
- **Global Support**: Perfect for system administrators and support teams

#### 🟡 **Supervisor Users**  
- **Manager Access**: Can impersonate managers directly assigned to them (`manager.supervisor_id === supervisor.id`)
- **Indirect User Access**: Can impersonate users assigned to their managers (`user.manager_id === manager.id`)
- **Hierarchical Support**: Ideal for department heads overseeing multiple teams

#### 🔵 **Manager Users**
- **Direct Reports Only**: Can impersonate users directly assigned to them (`user.manager_id === manager.id`)
- **Team Support**: Perfect for team leads helping their direct reports
- **Limited Scope**: Cannot impersonate other managers or users outside their team

#### ⚫ **Regular Users**
- **No Access**: Cannot impersonate other users
- **Contact Support**: Must request assistance from managers, supervisors, or admins

### User Selection Process

### User Selection Process

#### 1. Opening the Impersonation Modal

When a user clicks "Log In As User":

1. **Permission Check**: Verifies user has appropriate role (admin/supervisor/manager)
2. **Hierarchy Filter**: Loads only users the current user can impersonate based on their role
3. **Store Original Info**: Saves current user data for restoration  
4. **Display Modal**: Shows searchable user list with hierarchy indicators

#### 2. User Filtering and Display

The modal provides:

- **Real-time Search**: Filter users as you type
- **Keyboard Navigation**: Arrow keys to navigate, Enter to select
- **Role-Based Display**: Color-coded role badges for easy identification
- **Hierarchy Indicators**: Shows relationship between current user and impersonatable users
  - "Your Manager" (for supervisors)
  - "Under Your Managers" (for supervisors viewing users)
  - "Your User" (for managers)
- **User Details**: Name, email, role, and hierarchy information

#### 3. Impersonation Activation

When a user is selected:

1. **Data Storage**: Saves impersonation state to localStorage
2. **Context Switch**: Updates user context throughout the application
3. **Banner Creation**: Shows prominent impersonation banner
4. **Page Refresh**: Reloads data to reflect new user's permissions

#### 4. Switching Back

The impersonation banner provides:

- **Clear Status**: Shows who you're impersonating
- **One-Click Return**: "Switch to my account" button
- **Original Context**: Restores all original user data

## 🔧 Technical Implementation

### Data Structure

The system uses localStorage to manage impersonation state:

```javascript
// Impersonation data stored in localStorage
{
    originalUser: {
        id: 'admin-id',
        email: 'admin@company.com',
        username: 'Admin User',
        role: 'admin'
    },
    impersonatedUser: {
        id: 'user-id',
        email: 'user@company.com',
        role: 'user',
        display_name: 'John Smith'
    },
    timestamp: '2025-01-01T12:00:00.000Z'
}
```

### Key Methods

#### `openImpersonationModal()`
- Checks permissions
- Stores original user info
- Creates and displays user selection modal
- Loads available users

#### `impersonateUser(userId)`
- Validates user selection
- Updates localStorage with new user context
- Creates impersonation banner
- Refreshes application state

#### `switchBackToOriginalUser()`
- Restores original user context
- Clears impersonation data
- Removes banner with animation
- Refreshes application state

#### `canImpersonate()`
- Returns true if current user has admin or supervisor role
- Used to show/hide impersonation controls

### CSS Classes and Styling

The system includes comprehensive CSS for:

- **Modal Animations**: Smooth slide-in/slide-out effects
- **Responsive Design**: Works on desktop and tablet devices
- **Color Coding**: Role-based color schemes
- **Interactive States**: Hover effects and focus states

## 🎨 Customization

### Styling

You can customize the appearance by modifying the CSS in `user_impersonation.js`:

```javascript
// Example: Change banner color
banner.style.cssText = `
    background: linear-gradient(135deg, #your-color, #your-darker-color);
    // ... other styles
`;

// Example: Customize role colors
getRoleColor(role) {
    const colors = {
        'admin': '#your-admin-color',
        'manager': '#your-manager-color',
        // ... other roles
    };
    return colors[role?.toLowerCase()] || '#default-color';
}
```

### User Data Sources

The system can work with different data sources:

```javascript
// Option 1: Global array (current default)
window.allUsers = usersArray;

// Option 2: Database integration
async loadAvailableUsers() {
    const { data, error } = await window.supabase
        .from('profiles')
        .select('*')
        .order('first_name');
    // Handle data...
}

// Option 3: API endpoint
async loadAvailableUsers() {
    const response = await fetch('/api/users');
    const users = await response.json();
    // Handle data...
}
```

### Permission System

Customize who can impersonate users:

```javascript
canImpersonate() {
    const userRole = localStorage.getItem('userRole')?.toLowerCase();
    // Customize this logic based on your needs
    return userRole === 'admin' || 
           userRole === 'supervisor' || 
           userRole === 'manager'; // Add manager if desired
}
```

## 🛠️ Integration Examples

### With Supabase

```javascript
// Example integration with Supabase authentication
async impersonateUser(userId) {
    try {
        // Update localStorage (existing code)
        // ...
        
        // Optional: Update Supabase session context
        const { data, error } = await supabase.auth.admin.getUserById(userId);
        if (error) throw error;
        
        // Continue with existing impersonation logic
        // ...
    } catch (error) {
        this.showError('Failed to impersonate user: ' + error.message);
    }
}
```

### With Custom Authentication

```javascript
// Example with custom auth system
async impersonateUser(userId) {
    try {
        // Call your auth API to create impersonation session
        const response = await fetch('/api/auth/impersonate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ userId })
        });
        
        if (!response.ok) throw new Error('Impersonation failed');
        
        // Continue with existing logic
        // ...
    } catch (error) {
        this.showError('Failed to impersonate user: ' + error.message);
    }
}
```

## 🔒 Security Considerations

### Permission Validation

- **Server-Side Checks**: Always validate permissions on the server side
- **Role Verification**: Ensure only authorized roles can access impersonation
- **Audit Logging**: Log all impersonation activities for security audits

### Session Management

- **Timeout Handling**: Consider implementing automatic logout after inactivity
- **Token Refresh**: Handle authentication token refresh during impersonation
- **Data Isolation**: Ensure impersonated sessions don't leak data

### Best Practices

1. **Principle of Least Privilege**: Only grant impersonation to necessary roles
2. **Audit Trail**: Maintain logs of who impersonated whom and when
3. **Time Limits**: Consider implementing maximum impersonation duration
4. **Clear Indication**: Always show clear visual indication of impersonation state
5. **Easy Exit**: Provide obvious way to exit impersonation mode

## 📱 Browser Compatibility

The system supports:

- **Chrome**: 80+
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

### Requirements

- **JavaScript**: ES6+ features required
- **LocalStorage**: For session management
- **CSS Grid/Flexbox**: For responsive layout

## 🐛 Troubleshooting

### Common Issues

#### Impersonation Modal Not Opening
- Check if user has permission (`userImpersonation.canImpersonate()`)
- Verify user data is loaded (`window.allUsers`)
- Check browser console for JavaScript errors

#### Users Not Displaying
- Ensure `window.allUsers` is populated with user data
- Check user data format (required fields: id, email, role)
- Verify no JavaScript errors in console

#### Banner Not Showing
- Check if impersonation data exists in localStorage
- Verify `createImpersonationBanner()` is called after impersonation
- Check CSS conflicts that might hide the banner

#### Can't Switch Back
- Check localStorage for `impersonationData`
- Verify original user info was stored properly
- Try clearing localStorage and refreshing page

### Debug Mode

Enable debug logging:

```javascript
// Add to your page to enable detailed logging
userImpersonation.debugMode = true;
```

## 📚 API Reference

### Main Class: `UserImpersonation`

#### Methods

##### `openImpersonationModal()`
Opens the user selection modal for impersonation.

**Returns:** `void`

##### `impersonateUser(userId)`
Impersonates the specified user.

**Parameters:**
- `userId` (string): The ID of the user to impersonate

**Returns:** `Promise<void>`

##### `switchBackToOriginalUser()`
Switches back to the original user who initiated impersonation.

**Returns:** `void`

##### `canImpersonate()`
Checks if the current user has permission to impersonate others.

**Returns:** `boolean`

##### `showSuccessMessage(message)`
Displays a success toast notification.

**Parameters:**
- `message` (string): The message to display

##### `showError(message)`
Displays an error toast notification.

**Parameters:**
- `message` (string): The error message to display

#### Properties

##### `isImpersonating`
**Type:** `boolean`
**Description:** Whether currently impersonating a user

##### `currentImpersonatedUser`
**Type:** `object|null`
**Description:** Data of the currently impersonated user

##### `originalUserInfo`
**Type:** `object|null`
**Description:** Data of the original user (before impersonation)

## 🎯 Demo and Testing

### Demo Page

Use `user_impersonation_demo.html` to test the system:

1. Open the demo page in your browser
2. The page includes sample users and admin context
3. Test all impersonation features
4. Check browser console for detailed logs

### Test Scenarios

1. **Admin Impersonation**: Log in as admin, impersonate different user roles
2. **Permission Denied**: Try impersonating as non-admin user
3. **Search Functionality**: Test user search with various terms
4. **Keyboard Navigation**: Use arrow keys and Enter to navigate
5. **Switch Back**: Test returning to original user
6. **Page Refresh**: Verify impersonation state persists across page loads

## 🚀 Future Enhancements

### Planned Features

- **Time-Limited Sessions**: Automatic logout after specified duration
- **Multi-Level Impersonation**: Ability to impersonate while already impersonating
- **Activity Logging**: Detailed audit trail of impersonation activities
- **Permission Templates**: Pre-defined permission sets for different roles
- **Mobile Optimization**: Enhanced mobile experience

### Integration Opportunities

- **Slack/Teams Integration**: Notify support teams of impersonation activities
- **Analytics Integration**: Track impersonation usage patterns
- **Help Desk Integration**: Link impersonation to support tickets
- **SSO Integration**: Support for Single Sign-On providers

## 📞 Support

For questions or issues with the User Impersonation System:

1. Check the troubleshooting section above
2. Review the demo page for working examples
3. Check browser console for error messages
4. Verify user permissions and data format

The system is designed to be robust and user-friendly, providing a professional impersonation experience similar to GoHighLevel while maintaining security and ease of use.
