# User Impersonation Troubleshooting Guide

## 🚨 "Nothing happens when I click Log In As User"

### Quick Debug Steps:

1. **Open Browser Console** (F12 → Console tab)

2. **Check if system initialized:**
   ```javascript
   userImpersonation.debugSystemState()
   ```

3. **Manually test permission:**
   ```javascript
   console.log('Can impersonate:', userImpersonation.canImpersonate())
   ```

4. **Check user role:**
   ```javascript
   console.log('User role:', localStorage.getItem('userRole'))
   ```

5. **Test modal creation:**
   ```javascript
   userImpersonation.openImpersonationModal()
   ```

### Common Issues & Solutions:

#### Issue 1: User Role Not Set
**Symptoms:** Console shows `canImpersonate: false`
**Solution:** Set a valid role
```javascript
localStorage.setItem('userRole', 'admin')
localStorage.setItem('userId', 'admin-1')
localStorage.setItem('username', 'Admin User')
localStorage.setItem('userEmail', 'admin@company.com')
```

#### Issue 2: No Users Available
**Symptoms:** Modal opens but shows "No users available"
**Solution:** Load demo users
```javascript
// For demo page
window.allUsers = [
    {
        id: 'user-1',
        first_name: 'Test',
        last_name: 'User',
        email: 'test@example.com',
        role: 'user',
        display_name: 'Test User'
    }
]
```

#### Issue 3: JavaScript Errors
**Symptoms:** Console shows errors
**Solution:** Check for missing methods or syntax errors

#### Issue 4: System Not Initialized
**Symptoms:** `userImpersonation` is undefined
**Solution:** Make sure script is loaded
```html
<script src="user_impersonation.js"></script>
```

### Manual Testing Commands:

```javascript
// 1. Check if system exists
console.log('System:', typeof userImpersonation)

// 2. Check current state
userImpersonation.debugSystemState()

// 3. Set admin role
localStorage.setItem('userRole', 'admin')

// 4. Load test users
window.allUsers = [
    { id: '1', email: 'test@example.com', role: 'user', first_name: 'Test', last_name: 'User' }
]

// 5. Try opening modal
userImpersonation.openImpersonationModal()
```

### Expected Console Output:
When working correctly, you should see:
```
🎭 Initializing User Impersonation System...
✅ User Impersonation System initialized
🔐 Checking impersonation permissions: {userRole: "admin", canImpersonate: true}
🎭 Opening impersonation modal...
🔐 Can impersonate: true
📝 Storing original user info...
🪟 Creating dropdown modal...
👥 Loading available users...
✅ Modal opened successfully
```

### Emergency Reset:
If nothing works, reset everything:
```javascript
// Clear all data
localStorage.clear()

// Set admin role
localStorage.setItem('userRole', 'admin')
localStorage.setItem('userId', 'admin-1')
localStorage.setItem('username', 'Admin')

// Reload page
location.reload()
```

### Test in Demo Page:
1. Open `user_impersonation_demo.html`
2. Click "Debug System" button
3. Check console output
4. Try "Test as Admin" then "Open Impersonation Modal"

### Still Not Working?

Check these files exist and are loaded:
- ✅ `user_impersonation.js` 
- ✅ Browser console shows no 404 errors
- ✅ No JavaScript syntax errors
- ✅ `userImpersonation` is defined globally

### Browser Compatibility:
- Chrome 80+
- Firefox 75+ 
- Safari 13+
- Edge 80+

### Contact Support:
If issue persists, provide:
1. Browser and version
2. Console error messages
3. Output of `userImpersonation.debugSystemState()`
