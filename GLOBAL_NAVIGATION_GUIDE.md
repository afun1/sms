# Global Navigation Implementation Guide

## Overview
The global navigation system provides a consistent navigation header across all pages in the Sparky Messaging platform. It's implemented as a single JavaScript file that automatically adds the navigation when included.

## Features
- ✅ Consistent blue gradient design matching your requirements
- ✅ Sticky positioning at the top of all pages
- ✅ Three-column layout: Logo/Brand (left), Menu (center), User Info/Logout (right)
- ✅ Red logout link as requested
- ✅ Automatic authentication checking
- ✅ Responsive design for mobile devices
- ✅ Automatic active page highlighting
- ✅ Admin link visibility based on user role

## Implementation

### Step 1: Include the Global Navigation Script
Add this single line to the `<head>` section of any page where you want navigation:

```html
<script src="static/global-nav.js"></script>
```

### Step 2: Remove Existing Navigation (Optional)
You can remove any existing navigation HTML and CSS from your pages, as the global script will handle everything.

### Step 3: Exclude from Login Page
The script automatically detects and excludes itself from login pages. No additional configuration needed.

## File Structure
```
static/
├── global-nav.js    # Main global navigation script
├── logo.png         # Your logo (optional - will show ⚡ icon if missing)
└── navigation.js    # Alternative implementation (more advanced)
```

## Usage Examples

### Minimal Page Example
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Page - Sparky Messaging</title>
    <script src="static/global-nav.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px; /* Navigation adds 70px top padding automatically */
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Your page content here -->
    </div>
</body>
</html>
```

### Login Page (Excluded)
For login pages, either:
1. Don't include the script at all, OR
2. Add `class="login-page"` to the body tag

## Customization

### Active Page Detection
The script automatically detects the current page and highlights it in the navigation. It uses the filename (without .html) to determine the active state.

### User Authentication
The navigation automatically:
- Checks for authentication tokens in localStorage
- Displays user name and role
- Shows admin link for admin users
- Redirects to login.html if not authenticated

### Logo Handling
- Tries to load `static/logo.png`
- Falls back to ⚡ icon if logo fails to load
- Automatically switches between logo and icon

## Navigation Links
The global navigation includes these links by default:
- 🏠 Home (index.html)
- 📊 Dashboard (dashboard.html)
- 📱 SMS (sms_editor.html)
- 📧 Email (email_editor.html)
- 📞 RVM (rvm_editor.html)
- 🤖 AI (ai_editor.html)
- 🚀 Campaigns (campaign_builder.html)
- ⚙️ Admin (admin.html) - only visible to admin users

## Benefits
1. **Consistency**: Same navigation across all pages
2. **Maintainability**: Update navigation in one file, affects all pages
3. **Performance**: Lightweight JavaScript implementation
4. **Responsive**: Works on desktop, tablet, and mobile
5. **Accessible**: Proper semantic HTML and keyboard navigation
6. **Easy Integration**: Just add one script tag

## Troubleshooting

### Navigation not appearing
- Check that the script path is correct: `static/global-nav.js`
- Ensure the page is not marked as a login page
- Check browser console for JavaScript errors

### Authentication issues
- Verify localStorage contains: `authToken`, `username`, `userRole`
- Check that the user is properly logged in
- Ensure login.html exists for redirects

### Styling conflicts
- The navigation uses prefixed CSS classes to avoid conflicts
- Body padding is automatically adjusted
- Override specific styles by using more specific CSS selectors

## Migration from Existing Navigation

### Quick Migration
1. Add `<script src="static/global-nav.js"></script>` to each page
2. Remove old navigation HTML and CSS (optional)
3. Test each page to ensure proper functionality

### Gradual Migration
You can migrate pages one at a time:
1. Keep existing navigation on most pages
2. Add global navigation to new pages
3. Gradually replace navigation on existing pages
4. Remove old navigation code once all pages are migrated

## Test Pages
- `simple_nav_test.html` - Basic test of global navigation
- `test_navigation.html` - Advanced test with detailed examples

The global navigation system is now ready for deployment across your entire Sparky Messaging platform!
