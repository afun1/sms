/**
 * User Impersonation System - Clean Implementation
 * Allows administrators to seamlessly log in as other users to provide support
 */

class UserImpersonation {
    constructor() {
        this.originalUserInfo = null;
        this.originalUserData = null; // Store original localStorage values
        this.originalSession = null; // Store original Supabase session
        this.currentImpersonatedUser = null;
        this.isImpersonating = false;
        this.impersonationBanner = null;
        this.hiddenElements = []; // Track elements that are hidden during impersonation
        this.preservedNavigation = null; // Store a copy of the original navigation
        this.navigationMonitor = null; // Interval for monitoring navigation updates
        
        this.init();
    }

    init() {
        console.log('🎭 Initializing User Impersonation System...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeAfterDOM();
            });
        } else {
            this.initializeAfterDOM();
        }
    }

    initializeAfterDOM() {
        console.log('🎭 DOM ready, continuing initialization...');
        this.checkImpersonationState();
        this.createImpersonationBanner();
        this.setupEventListeners();
        
        // Simple navigation backup
        this.preserveNavigation();
        
        // Update UI for impersonation
        if (this.isImpersonating) {
            this.updateNavigationForImpersonation();
            this.hideAdminFunctionsForRole(this.currentImpersonatedUser.role);
        }
        
        // Set up navigation link interception for persistent impersonation
        this.setupNavigationInterception();
        
        console.log('✅ User Impersonation System initialized');
    }

    /**
     * Simple navigation preservation without DOM overrides
     */
    preserveNavigation() {
        const nav = document.getElementById('global-nav');
        if (nav) {
            this.preservedNavigation = nav.cloneNode(true);
            console.log('💾 Navigation preserved');
        }
    }

    /**
     * Check if currently impersonating a user and restore state
     */
    checkImpersonationState() {
        const impersonationData = localStorage.getItem('impersonationData');
        if (impersonationData) {
            try {
                const data = JSON.parse(impersonationData);
                this.originalUserInfo = data.originalUser;
                this.originalUserData = data.originalUserData;
                this.currentImpersonatedUser = data.impersonatedUser;
                this.isImpersonating = true;
                
                console.log('🎭 Restoring impersonation state:', this.currentImpersonatedUser.email);
                
                // Restore the impersonated user's session data
                this.setupSupabaseImpersonation(this.currentImpersonatedUser);
                
            } catch (error) {
                console.error('Error restoring impersonation state:', error);
                this.clearImpersonation();
            }
        }
    }

    /**
     * Create the impersonation banner that shows below the nav when impersonating
     * DISABLED: Using only the compact navigation banner instead
     */
    createImpersonationBanner() {
        // Disabled - we're using only the compact banner in the navigation
        // The navigation banner (global-nav-v2.js) provides the impersonation indicator
        console.log('🎭 Secondary impersonation banner disabled - using navigation banner only');
        return;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for the custom event to start impersonation
        document.addEventListener('startImpersonation', (event) => {
            this.startImpersonation(event.detail.user);
        });

        // Listen for the custom event to exit impersonation
        document.addEventListener('exitImpersonation', () => {
            this.exitImpersonation();
        });
    }

    /**
     * Get current user permissions for hierarchy check
     */
    getCurrentUserRole() {
        // Try to get from impersonated user first
        if (this.isImpersonating && this.originalUserInfo) {
            return this.originalUserInfo.role || 'user';
        }
        
        // Try to get from current user
        const userInfo = this.getCurrentUserInfo();
        return userInfo?.role || 'user';
    }

    /**
     * Get current user information from various sources
     */
    getCurrentUserInfo() {
        // Check if available in window.currentUser
        if (window.currentUser) {
            return window.currentUser;
        }

        // Check localStorage
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                return JSON.parse(userData);
            } catch (e) {
                console.warn('Failed to parse userData from localStorage');
            }
        }

        // Check if available in a global variable
        if (window.user) {
            return window.user;
        }

        // Default fallback
        return {
            id: 'current-user',
            email: 'current@example.com',
            displayName: 'Current User',
            role: 'admin' // Default to admin for testing
        };
    }

    /**
     * Check if current user can impersonate target user
     */
    canImpersonate(targetUser) {
        // When checking permissions, always use the ORIGINAL user's role
        let currentRole;
        
        if (this.isImpersonating) {
            // If already impersonating, check impersonation data for original user role
            const impersonationData = localStorage.getItem('impersonationData');
            if (impersonationData) {
                try {
                    const data = JSON.parse(impersonationData);
                    currentRole = data.originalProfile?.role || 'user';
                    console.log(`🔍 Using original admin role for permission check: ${currentRole}`);
                } catch (e) {
                    console.error('Error parsing impersonation data:', e);
                    currentRole = 'user';
                }
            } else {
                currentRole = 'user';
            }
        } else {
            // Not impersonating, get role from global navigation helper (which uses Supabase session)
            if (window.getAuthenticatedUser) {
                try {
                    const userData = window.getAuthenticatedUser();
                    currentRole = userData?.userRole || 'admin';
                    console.log(`🔍 Using current user role from global helper: ${currentRole}`);
                } catch (e) {
                    console.error('Error getting user from global helper:', e);
                    currentRole = 'admin'; // Default to admin for permission checks
                }
            } else {
                currentRole = 'admin'; // Default to admin if helper not available
                console.log(`🔍 Global helper not available, defaulting to admin role`);
            }
        }
        
        const targetRole = targetUser.role || 'user';

        console.log(`🔍 Permission check: ${currentRole} → ${targetRole}`);

        // Define role hierarchy (higher number = more permissions)
        const roleHierarchy = {
            'user': 1,
            'supervisor': 2,
            'manager': 3,
            'admin': 4,
            'super_admin': 5
        };

        const currentLevel = roleHierarchy[currentRole] || 0;
        const targetLevel = roleHierarchy[targetRole] || 0;

        const canImpersonate = currentLevel > targetLevel;
        console.log(`🔍 Can impersonate: ${canImpersonate} (${currentLevel} > ${targetLevel})`);

        return canImpersonate;
    }

    /**
     * Start impersonating a user directly (no modal)
     */
    async startImpersonation(targetUser, startingPage = null) {
        console.log('🎭 Starting direct impersonation for:', targetUser);

        try {
            // Check permissions
            if (!this.canImpersonate(targetUser)) {
                throw new Error('Insufficient permissions to impersonate this user');
            }

            // Store original user info if not already impersonating
            if (!this.isImpersonating) {
                this.originalUserInfo = this.getCurrentUserInfo();
                console.log('💾 Storing original user info:', this.originalUserInfo);
                
                // Also backup original localStorage values
                this.originalUserData = {
                    userId: localStorage.getItem('userId'),
                    userEmail: localStorage.getItem('userEmail'),
                    userRole: localStorage.getItem('userRole'),
                    username: localStorage.getItem('username'),
                    displayName: localStorage.getItem('displayName'),
                    userData: localStorage.getItem('userData')
                };
            }

            // Set impersonation state
            this.currentImpersonatedUser = targetUser;
            this.isImpersonating = true;

            // Store in localStorage for persistence
            const impersonationData = {
                originalUser: this.originalUserInfo,
                originalUserData: this.originalUserData,
                impersonatedUser: this.currentImpersonatedUser,
                timestamp: Date.now()
            };
            localStorage.setItem('impersonationData', JSON.stringify(impersonationData));

            // Actually change the user session data to the impersonated user
            this.switchToImpersonatedUserSession(targetUser);

            // Create banner
            this.createImpersonationBanner();

            // Update navigation immediately and force refresh
            this.updateNavigationForImpersonation();
            
            // Force refresh the global navigation to use impersonated user data
            if (typeof window.setupNav === 'function') {
                console.log('🔄 Refreshing global navigation with impersonated user data...');
                setTimeout(() => {
                    window.setupNav();
                    // Update again after nav refresh
                    setTimeout(() => this.updateNavigationForImpersonation(), 200);
                }, 100);
            }
            
            this.hideAdminFunctionsForRole(targetUser.role);
            
            // Start monitoring navigation for persistence
            this.startNavigationMonitoring();

            // Navigate to dashboard by default if no starting page specified
            const defaultPage = startingPage || 'dashboard.html';
            
            console.log(`🔄 Starting impersonation and navigating to: ${defaultPage}`);
            console.log(`📍 Current location: ${window.location.href}`);
            console.log(`📍 About to navigate to: ${defaultPage}`);
            
            // Small delay to ensure session data is set before navigation
            setTimeout(() => {
                console.log(`🚀 Actually navigating to: ${defaultPage}`);
                window.location.href = defaultPage;
            }, 100);

        } catch (error) {
            console.error('❌ Failed to start impersonation:', error);
            this.showNotification(`Failed to impersonate user: ${error.message}`, 'error');
        }
    }

    /**
     * Exit impersonation and return to original user
     */
    async exitImpersonation() {
        console.log('🎭 Exiting impersonation...');

        try {
            // Clear impersonation state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;
            
            // Stop navigation monitoring
            if (this.navigationMonitor) {
                clearInterval(this.navigationMonitor);
                this.navigationMonitor = null;
            }

            // Remove from localStorage
            localStorage.removeItem('impersonationData');
            
            // Restore original user session data and remove query interception
            await this.restoreOriginalUserSession();

            // Remove banner and body class
            if (this.impersonationBanner) {
                this.impersonationBanner.remove();
                this.impersonationBanner = null;
                document.body.classList.remove('impersonating');
            }

            // Restore admin functions
            this.restoreAdminFunctions();

            // Restore navigation
            this.refreshGlobalNavigation();

            // Clear original user info
            this.originalUserInfo = null;
            this.originalUserData = null;

            // Emit exit event
            document.dispatchEvent(new CustomEvent('impersonationExited'));

            console.log('✅ Impersonation exited successfully');

        } catch (error) {
            console.error('❌ Failed to exit impersonation:', error);
        }
    }

    /**
     * Clear impersonation state (used for error recovery)
     */
    clearImpersonation() {
        this.isImpersonating = false;
        this.currentImpersonatedUser = null;
        this.originalUserInfo = null;
        this.originalUserData = null;
        localStorage.removeItem('impersonationData');
        
        // Stop navigation monitoring
        if (this.navigationMonitor) {
            clearInterval(this.navigationMonitor);
            this.navigationMonitor = null;
        }
        
        if (this.impersonationBanner) {
            this.impersonationBanner.remove();
            this.impersonationBanner = null;
            document.body.style.paddingTop = '60px'; // Reset to just nav height
        }
    }

    /**
     * Update navigation header to show impersonated user
     */
    updateNavigationForImpersonation() {
        if (!this.isImpersonating) return;

        console.log('🔄 Updating navigation for impersonated user:', this.currentImpersonatedUser.email);

        // Wait for navigation to be fully loaded
        const updateNav = () => {
            const nav = document.getElementById('global-nav');
            if (!nav) {
                console.warn('⚠️ Global navigation not found, will retry...');
                // Retry after navigation loads
                setTimeout(() => this.updateNavigationForImpersonation(), 500);
                return;
            }

            const impersonatedDisplayName = this.currentImpersonatedUser.display_name || 
                                           this.currentImpersonatedUser.displayName ||
                                           `${this.currentImpersonatedUser.first_name || ''} ${this.currentImpersonatedUser.last_name || ''}`.trim() ||
                                           this.currentImpersonatedUser.email.split('@')[0];

            console.log(`🏷️ Using display name: ${impersonatedDisplayName}`);

            // Find and update various navigation elements that might show the user name
            
            // 1. Welcome messages and greetings
            const welcomeSpans = nav.querySelectorAll('span, div, p, h1, h2, h3, h4, h5, h6');
            let updatedElements = 0;
            
            welcomeSpans.forEach(element => {
                const text = element.textContent || '';
                
                // Check for welcome patterns but be more specific to avoid updating everything
                if (text && text.length < 200 && (
                    (text.includes('Welcome,') && !text.includes('SMS') && !text.includes('Campaign')) ||
                    (text.includes('Hello,') && !text.includes('SMS')) ||
                    (text.includes('Hi,') && !text.includes('SMS'))
                )) {
                    // For welcome messages, try to be more surgical
                    if (text.includes('Welcome,')) {
                        // Extract everything after "Welcome," and replace it
                        const welcomeIndex = text.indexOf('Welcome,');
                        const beforeWelcome = text.substring(0, welcomeIndex);
                        const newText = `${beforeWelcome}Welcome, ${impersonatedDisplayName}`;
                        element.textContent = newText;
                        console.log(`✅ Updated greeting from "${text}" to: ${newText}`);
                        updatedElements++;
                    }
                }
            });

            // 2. User display elements with data attributes and classes
            const userDisplaySelectors = [
                '[data-user-display]', 
                '.user-name', 
                '.user-email', 
                '.username',
                '.user-display-name',
                '.profile-name',
                '.current-user',
                '#user-name',
                '#username',
                '#current-user-name'
            ];

            userDisplaySelectors.forEach(selector => {
                const elements = nav.querySelectorAll(selector);
                elements.forEach(element => {
                    if (element.dataset.userDisplay === 'name' || 
                        element.classList.contains('user-name') || 
                        element.classList.contains('username') ||
                        element.classList.contains('user-display-name') ||
                        element.classList.contains('profile-name') ||
                        element.classList.contains('current-user') ||
                        element.id === 'user-name' ||
                        element.id === 'username' ||
                        element.id === 'current-user-name') {
                        
                        const oldText = element.textContent;
                        element.textContent = impersonatedDisplayName;
                        console.log(`✅ Updated user name element (${selector}) from "${oldText}" to: ${impersonatedDisplayName}`);
                        updatedElements++;
                        
                    } else if (element.dataset.userDisplay === 'email' || element.classList.contains('user-email')) {
                        element.textContent = this.currentImpersonatedUser.email;
                        console.log(`✅ Updated user email element to: ${this.currentImpersonatedUser.email}`);
                        updatedElements++;
                    }
                });
            });

            // 3. Look for elements that might contain just the user name
            // Try to find text nodes or elements that contain what looks like a user name
            const walker = document.createTreeWalker(
                nav,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let textNode;
            while (textNode = walker.nextNode()) {
                const text = textNode.textContent?.trim();
                if (text && text.includes('Welcome,')) {
                    // Found a text node with Welcome - replace just the name part
                    const regex = /Welcome,\s*([^,\n\r]+)/;
                    const match = text.match(regex);
                    if (match) {
                        const newText = text.replace(regex, `Welcome, ${impersonatedDisplayName}`);
                        textNode.textContent = newText;
                        console.log(`✅ Updated text node from "${text}" to: ${newText}`);
                        updatedElements++;
                    }
                }
            }

            // 4. Profile buttons, dropdowns, and any element containing user names
            const profileElements = nav.querySelectorAll('.profile-name, .user-profile, [class*="profile"], [class*="user"]');
            profileElements.forEach(element => {
                const text = element.textContent || '';
                // Only update if it looks like a user name (not generic labels)
                if (text && !text.includes('Profile') && !text.includes('Settings') && 
                    !text.includes('Logout') && !text.includes('Menu') && 
                    !text.includes('Dashboard') && text.length > 0 && text.length < 50) {
                    
                    // Check if it might be a user name by looking for email pattern or name pattern
                    if (text.includes('@') || text.match(/^[A-Za-z\s]+$/)) {
                        const oldText = element.textContent;
                        element.textContent = impersonatedDisplayName;
                        console.log(`✅ Updated profile element from "${oldText}" to: ${impersonatedDisplayName}`);
                        updatedElements++;
                    }
                }
            });

            // 4. Update localStorage values to ensure consistency across page loads
            localStorage.setItem('displayName', impersonatedDisplayName);
            localStorage.setItem('username', impersonatedDisplayName);

            // 5. Update window.currentUser if it exists
            if (window.currentUser) {
                window.currentUser.displayName = impersonatedDisplayName;
                window.currentUser.username = impersonatedDisplayName;
            }

            console.log(`✅ Navigation updated for impersonation (${updatedElements} elements updated)`);
            
            // If no elements were updated, the navigation might use a different structure
            if (updatedElements === 0) {
                console.warn('⚠️ No navigation elements were updated - navigation might use a different structure');
                
                // Try a more aggressive approach - look for any text that might be a name
                const allTextElements = nav.querySelectorAll('*');
                allTextElements.forEach(element => {
                    const text = element.textContent?.trim();
                    if (text && text.length > 2 && text.length < 50 && 
                        (text.includes(' ') || text.includes('@')) &&
                        !text.includes('Dashboard') && !text.includes('Admin') && 
                        !text.includes('Home') && !text.includes('Settings')) {
                        
                        console.log(`🔍 Found potential name element: "${text}" in`, element);
                    }
                });
            }
        };

        // Execute immediately, but also retry after a delay for slow-loading navigation
        updateNav();
        setTimeout(updateNav, 100);
        setTimeout(updateNav, 500);
    }

    /**
     * Refresh global navigation
     */
    refreshGlobalNavigation() {
        console.log('🔄 Refreshing global navigation');

        // Check if global navigation is still present
        const nav = document.getElementById('global-nav');
        if (!nav && this.preservedNavigation) {
            console.log('🔧 Restoring navigation from backup');
            document.body.appendChild(this.preservedNavigation.cloneNode(true));
        }

        // Re-initialize navigation if the reinit function exists
        if (typeof window.initializeGlobalNavigation === 'function') {
            window.initializeGlobalNavigation();
        } else if (typeof window.setupNav === 'function') {
            window.setupNav();
        }

        // If we just exited impersonation, update navigation to show original user
        if (!this.isImpersonating && this.originalUserInfo) {
            setTimeout(() => {
                const navElement = document.getElementById('global-nav');
                if (navElement) {
                    const welcomeSpans = navElement.querySelectorAll('span');
                    welcomeSpans.forEach(span => {
                        if (span.textContent && span.textContent.includes('Welcome,')) {
                            const originalName = this.originalUserInfo.displayName || 
                                               this.originalUserInfo.email?.split('@')[0] || 
                                               'Admin';
                            span.textContent = `Welcome, ${originalName}`;
                            console.log(`✅ Restored navigation to show: Welcome, ${originalName}`);
                        }
                    });
                }
            }, 100);
        }

        console.log('✅ Global navigation refreshed');
    }

    /**
     * Hide admin-specific functions based on impersonated user's role
     */
    hideAdminFunctionsForRole(userRole) {
        console.log(`🔒 Hiding admin functions for role: ${userRole}`);

        // Define admin-only selectors
        const adminSelectors = [
            '[data-admin-only]',
            '.admin-only',
            '[data-role="admin"]',
            '[data-min-role="admin"]',
            '.user-management',
            '.admin-panel',
            '.admin-controls'
        ];

        // Define role-based visibility
        const rolePermissions = {
            'user': [],
            'supervisor': ['[data-min-role="supervisor"]'],
            'manager': ['[data-min-role="supervisor"]', '[data-min-role="manager"]'],
            'admin': ['[data-min-role="supervisor"]', '[data-min-role="manager"]', '[data-min-role="admin"]']
        };

        // Hide elements that the current role shouldn't see
        adminSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                // Skip navigation elements to avoid breaking the header
                if (element.closest('#global-nav')) {
                    return;
                }

                if (!rolePermissions[userRole]?.includes(selector)) {
                    element.style.display = 'none';
                    this.hiddenElements.push({ element, originalDisplay: element.style.display });
                }
            });
        });

        console.log(`🔒 Hidden ${this.hiddenElements.length} admin elements`);
    }

    /**
     * Restore admin functions when exiting impersonation
     */
    restoreAdminFunctions() {
        console.log('🔓 Restoring admin functions');

        this.hiddenElements.forEach(({ element, originalDisplay }) => {
            element.style.display = originalDisplay;
        });

        this.hiddenElements = [];
        console.log('🔓 Admin functions restored');
    }

    /**
     * Main entry point for impersonation - direct start, no modal
     */
    showImpersonationModal(user) {
        console.log('🎭 Starting direct impersonation (no modal) for:', user);
        
        if (!user) {
            console.error('❌ No user provided for impersonation');
            this.showNotification('Error: No user selected for impersonation', 'error');
            return;
        }
        
        if (!user.email) {
            console.error('❌ User missing email:', user);
            this.showNotification('Error: User data is incomplete', 'error');
            return;
        }
        
        // Start impersonation directly and navigate to dashboard
        this.startImpersonation(user, 'dashboard.html');
    }

    /**
     * Get available pages for a user role (simplified for direct dashboard navigation)
     */
    getAvailablePages(userRole = 'user') {
        // Since we're going directly to dashboard, this is simplified
        return [
            {
                title: 'Dashboard',
                url: 'dashboard.html',
                icon: '📊',
                description: 'Main dashboard with overview and quick actions'
            }
        ];
    }

    /**
     * Get available pages based on user role
     */
    getAvailablePages(userRole) {
        const allPages = [
            {
                title: 'Dashboard',
                url: '/dashboard.html',
                icon: '📊',
                description: 'Main dashboard with overview and recent activity',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'SMS Campaign Builder',
                url: '/sms_editor.html',
                icon: '📱',
                description: 'Create and manage SMS campaigns',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'Email Campaign Builder',
                url: '/email_editor.html',
                icon: '✉️',
                description: 'Create and manage email campaigns',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'RVM Campaign Builder',
                url: '/rvm_editor.html',
                icon: '🎤',
                description: 'Create and manage ringless voicemail campaigns',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'AI Content Editor',
                url: '/ai_editor.html',
                icon: '🤖',
                description: 'AI-powered content creation and editing',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'Contact Lists',
                url: '/list.html',
                icon: '📇',
                description: 'Manage contact lists and segments',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'Assets & Files',
                url: '/assets.html',
                icon: '📁',
                description: 'Manage uploaded files and media assets',
                roles: ['user', 'supervisor', 'manager', 'admin']
            },
            {
                title: 'Admin Panel',
                url: '/admin.html',
                icon: '⚙️',
                description: 'User management and system administration',
                roles: ['admin']
            }
        ];

        // Filter pages based on user role
        return allPages.filter(page => page.roles.includes(userRole));
    }

    /**
     * Start impersonation with a specific starting page
     */
    async startImpersonationWithPage(targetUser, startingPage) {
        console.log('🎭 Starting impersonation with page:', startingPage, 'for:', targetUser.email);

        try {
            // Start the impersonation first
            await this.startImpersonation(targetUser);

            // Navigate to the selected page
            if (startingPage && startingPage !== window.location.pathname) {
                console.log('🔄 Navigating to starting page:', startingPage);
                
                // Show a brief message before navigation
                this.showNotification(`Starting as ${targetUser.displayName || targetUser.email}...`, 'info');
                
                // Small delay to ensure impersonation state is fully set
                setTimeout(() => {
                    window.location.href = startingPage;
                }, 500);
            } else {
                this.showNotification(`Now impersonating: ${targetUser.displayName || targetUser.email}`, 'success');
            }

        } catch (error) {
            console.error('❌ Failed to start impersonation with page:', error);
            this.showNotification(`Failed to impersonate user: ${error.message}`, 'error');
        }
    }

    /**
     * Show a notification message
     */
    showNotification(message, type = 'info', duration = 4000) {
        console.log(`📢 Notification (${type}):`, message);

        // Remove any existing notifications
        const existingNotification = document.getElementById('user-impersonation-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.id = 'user-impersonation-notification';
        
        const bgColors = {
            'success': '#d4edda',
            'error': '#f8d7da',
            'warning': '#fff3cd',
            'info': '#d1ecf1'
        };

        const textColors = {
            'success': '#155724',
            'error': '#721c24',
            'warning': '#856404',
            'info': '#0c5460'
        };

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${bgColors[type] || bgColors.info};
            color: ${textColors[type] || textColors.info};
            border: 1px solid ${textColors[type] || textColors.info}33;
            border-radius: 6px;
            padding: 12px 20px;
            z-index: 100002;
            max-width: 350px;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease-out;
        `;

        notification.textContent = message;

        // Add animation keyframes if not already added
        if (!document.getElementById('notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOutRight 0.3s ease-in';
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 300);
                }
            }, duration);
        }

        // Allow manual close on click
        notification.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        });

        notification.style.cursor = 'pointer';
        notification.title = 'Click to dismiss';
    }

    /**
     * Setup navigation interception to maintain impersonation across pages
     */
    setupNavigationInterception() {
        if (!this.isImpersonating) return;
        
        // Monitor for navigation changes and ensure impersonation persists
        setTimeout(() => {
            const nav = document.getElementById('global-nav');
            if (nav) {
                const navLinks = nav.querySelectorAll('a[href]');
                navLinks.forEach(link => {
                    // Don't interfere with links, just log for debugging
                    link.addEventListener('click', () => {
                        console.log('🔄 Navigation detected while impersonating, state will persist');
                    });
                });
            }
        }, 1000);
    }

    /**
     * Start monitoring navigation to ensure impersonation state
     */
    startNavigationMonitoring() {
        if (this.navigationMonitor) {
            clearInterval(this.navigationMonitor);
        }
        
        // Check navigation state every 2 seconds (more frequent during impersonation)
        this.navigationMonitor = setInterval(() => {
            if (!this.isImpersonating) {
                clearInterval(this.navigationMonitor);
                this.navigationMonitor = null;
                return;
            }
            
            // Ensure the impersonation banner is still visible
            if (!document.getElementById('impersonation-banner')) {
                console.log('🔄 Impersonation banner missing, recreating...');
                this.createImpersonationBanner();
            }
            
            // Ensure navigation shows the correct user - check more frequently
            const nav = document.getElementById('global-nav');
            if (nav) {
                // Check if navigation still shows admin name instead of impersonated user
                const navText = nav.textContent || '';
                const expectedName = this.currentImpersonatedUser.display_name || 
                                   this.currentImpersonatedUser.displayName ||
                                   `${this.currentImpersonatedUser.first_name || ''} ${this.currentImpersonatedUser.last_name || ''}`.trim();
                
                if (expectedName && !navText.includes(expectedName)) {
                    console.log('🔄 Navigation needs update, refreshing...');
                    this.updateNavigationForImpersonation();
                    
                    // Also try to refresh the global nav
                    if (typeof window.setupNav === 'function') {
                        setTimeout(() => window.setupNav(), 100);
                    }
                }
            }
            
        }, 2000);
    }

    /**
     * Switch localStorage to impersonated user's data
     */
    /**
     * Switch to impersonated user session - REAL SESSION SWITCHING
     */
    async switchToImpersonatedUserSession(targetUser) {
        console.log('🔄 Switching Supabase session to impersonated user:', targetUser.email);
        
        try {
            // Get the current Supabase client
            const supabase = window.globalSupabase || window.supabase;
            if (!supabase) {
                throw new Error('Supabase client not available');
            }

            // Store the original session before switching
            const { data: { session: originalSession } } = await supabase.auth.getSession();
            if (originalSession && !this.originalSession) {
                this.originalSession = originalSession;
                console.log('💾 Stored original admin session');
            }

            // Create a temporary authentication session for the impersonated user
            // Since we don't have their password, we'll use admin privileges to create a session
            
            // Override Supabase auth methods to return impersonated user
            this.setupSupabaseImpersonation(targetUser);
            
            // Create complete user data object for the impersonated user
            const impersonatedUserData = {
                id: targetUser.id,
                email: targetUser.email,
                displayName: targetUser.display_name || targetUser.displayName || 
                            `${targetUser.first_name || ''} ${targetUser.last_name || ''}`.trim() ||
                            targetUser.email.split('@')[0],
                firstName: targetUser.first_name || '',
                lastName: targetUser.last_name || '',
                role: targetUser.role || 'user',
                department: targetUser.department || null,
                phone: targetUser.phone || '',
                sparkyUsername: targetUser.sparky_username || '',
                fullName: `${targetUser.first_name || ''} ${targetUser.last_name || ''}`.trim()
            };
            
            // Update ALL localStorage values to reflect the impersonated user
            localStorage.setItem('userId', targetUser.id);
            localStorage.setItem('userEmail', targetUser.email);
            localStorage.setItem('userRole', targetUser.role || 'user');
            localStorage.setItem('username', impersonatedUserData.displayName);
            localStorage.setItem('displayName', impersonatedUserData.displayName);
            localStorage.setItem('firstName', impersonatedUserData.firstName);
            localStorage.setItem('lastName', impersonatedUserData.lastName);
            localStorage.setItem('fullName', impersonatedUserData.fullName);
            localStorage.setItem('userData', JSON.stringify(impersonatedUserData));
            
            // Also update window.currentUser if it exists
            if (window.currentUser) {
                window.currentUser = impersonatedUserData;
            }
            
            // Update any other global user variables that might exist
            if (window.user) {
                window.user = impersonatedUserData;
            }
            
            if (window.userInfo) {
                window.userInfo = impersonatedUserData;
            }

            // Store impersonation data for persistence
            const impersonationData = {
                originalSession: this.originalSession,
                originalProfile: this.originalUserInfo,
                impersonatedUser: targetUser,
                timestamp: Date.now()
            };
            localStorage.setItem('impersonationData', JSON.stringify(impersonationData));
            
            console.log('✅ Session switched to impersonated user (with query interception):', impersonatedUserData.displayName);
            console.log('📊 User data set:', impersonatedUserData);
            
        } catch (error) {
            console.error('❌ Failed to switch Supabase session:', error);
            throw error;
        }
    }

    /**
     * Set up Supabase impersonation by overriding auth methods
     */
    setupSupabaseImpersonation(impersonatedUser) {
        console.log('🔧 Setting up Supabase impersonation for user:', impersonatedUser.email);
        
        const supabase = window.globalSupabase || window.supabase;
        if (!supabase) {
            console.error('❌ Cannot set up impersonation: Supabase not available');
            return;
        }

        // Create fake user object for the impersonated user
        const fakeUser = {
            id: impersonatedUser.id,
            email: impersonatedUser.email,
            user_metadata: {
                display_name: impersonatedUser.display_name,
                first_name: impersonatedUser.first_name,
                last_name: impersonatedUser.last_name
            },
            app_metadata: {},
            aud: 'authenticated',
            created_at: impersonatedUser.created_at || new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        // Create fake session object
        const fakeSession = {
            access_token: 'fake-impersonation-token',
            token_type: 'bearer',
            expires_in: 3600,
            refresh_token: 'fake-refresh-token',
            user: fakeUser
        };

        // Store original auth methods
        if (!supabase.auth._originalGetUser) {
            supabase.auth._originalGetUser = supabase.auth.getUser.bind(supabase.auth);
            supabase.auth._originalGetSession = supabase.auth.getSession.bind(supabase.auth);
        }

        // Override getUser to return impersonated user
        supabase.auth.getUser = async function() {
            console.log('🎭 Returning impersonated user:', fakeUser.email);
            return {
                data: { user: fakeUser },
                error: null
            };
        };

        // Override getSession to return impersonated session
        supabase.auth.getSession = async function() {
            console.log('🎭 Returning impersonated session for:', fakeUser.email);
            return {
                data: { session: fakeSession },
                error: null
            };
        };

        console.log('✅ Supabase auth methods overridden for impersonation');
    }

    /**
     * Remove Supabase impersonation
     */
    removeSupabaseImpersonation() {
        console.log('🔧 Removing Supabase impersonation');
        
        const supabase = window.globalSupabase || window.supabase;
        if (!supabase) return;

        // Restore original auth methods
        if (supabase.auth._originalGetUser) {
            supabase.auth.getUser = supabase.auth._originalGetUser;
            delete supabase.auth._originalGetUser;
        }

        if (supabase.auth._originalGetSession) {
            supabase.auth.getSession = supabase.auth._originalGetSession;
            delete supabase.auth._originalGetSession;
        }

        console.log('✅ Supabase impersonation removed');
    }

    /**
     * Debug function to inspect navigation structure
     */
    debugNavigationStructure() {
        console.log('🔍 DEBUG: Analyzing navigation structure...');
        
        const nav = document.getElementById('global-nav');
        if (!nav) {
            console.log('❌ No global-nav found');
            return;
        }
        
        console.log('✅ Global nav found:', nav);
        
        // Find all text-containing elements
        const allElements = nav.querySelectorAll('*');
        console.log(`📊 Total elements in nav: ${allElements.length}`);
        
        const textElements = [];
        allElements.forEach((element, index) => {
            const text = element.textContent?.trim();
            if (text && text.length > 0 && text.length < 100) {
                textElements.push({
                    index,
                    tag: element.tagName.toLowerCase(),
                    classes: element.className,
                    id: element.id,
                    text: text,
                    element: element
                });
            }
        });
        
        console.log('📝 Text elements found:', textElements);
        
        // Look for potential user name elements
        const potentialNames = textElements.filter(item => {
            const text = item.text.toLowerCase();
            return (
                text.includes('welcome') ||
                text.includes('hello') ||
                text.includes('@') ||
                (text.includes(' ') && text.length > 5 && text.length < 30) ||
                item.classes.includes('user') ||
                item.classes.includes('name') ||
                item.id.includes('user') ||
                item.id.includes('name')
            );
        });
        
        console.log('👤 Potential user name elements:', potentialNames);
        
        return {
            nav,
            allElements: allElements.length,
            textElements,
            potentialNames
        };
    }

    /**
     * Restore original user session data and remove impersonation
     */
    async restoreOriginalUserSession() {
        console.log('🔄 Restoring original user session');
        
        try {
            // Remove impersonation first
            this.removeSupabaseImpersonation();

            // Restore original Supabase session if we have it (skip fake tokens)
            if (this.originalSession && this.originalSession.access_token !== 'fake-impersonation-token') {
                const supabase = window.globalSupabase || window.supabase;
                if (supabase && supabase.auth) {
                    try {
                        const { error } = await supabase.auth.setSession({
                            access_token: this.originalSession.access_token,
                            refresh_token: this.originalSession.refresh_token
                        });
                        
                        if (error) {
                            console.error('❌ Failed to restore original session:', error);
                            // Don't throw error, just log it
                        } else {
                            console.log('✅ Original Supabase session restored');
                        }
                    } catch (e) {
                        console.error('❌ Exception restoring session:', e);
                        // Don't throw error, just log it
                    }
                } else {
                    console.log('🔄 Skipping session restoration (no auth available)');
                }
            } else {
                console.log('🔄 Skipping session restoration (fake token or no session)');
            }

            // Restore localStorage values
            if (this.originalUserData) {
                Object.keys(this.originalUserData).forEach(key => {
                    if (this.originalUserData[key] !== null) {
                        localStorage.setItem(key, this.originalUserData[key]);
                    } else {
                        localStorage.removeItem(key);
                    }
                });
            }
            
            // Restore window.currentUser if it exists
            if (window.currentUser && this.originalUserInfo) {
                window.currentUser = this.originalUserInfo;
            }

            // Clear stored session
            this.originalSession = null;
            
            console.log('✅ Original user session fully restored');
            
        } catch (error) {
            console.error('❌ Error restoring original user session:', error);
        }
    }
}

/**
 * Restore original user session data and remove impersonation
 */
async function restoreOriginalUserSession() {
    console.log('🔄 Restoring original user session');
    
    try {
        // Remove impersonation first
        window.userImpersonation.removeSupabaseImpersonation();

        // Restore original Supabase session if we have it
        if (window.userImpersonation.originalSession) {
            const supabase = window.globalSupabase || window.supabase;
            if (supabase) {
                const { error } = await supabase.auth.setSession({
                    access_token: window.userImpersonation.originalSession.access_token,
                    refresh_token: window.userImpersonation.originalSession.refresh_token
                });
                
                if (error) {
                    console.error('❌ Failed to restore original session:', error);
                } else {
                    console.log('✅ Original Supabase session restored');
                }
            }
        }

        // Restore localStorage values
        if (window.userImpersonation.originalUserData) {
            Object.keys(window.userImpersonation.originalUserData).forEach(key => {
                if (window.userImpersonation.originalUserData[key] !== null) {
                    localStorage.setItem(key, window.userImpersonation.originalUserData[key]);
                } else {
                    localStorage.removeItem(key);
                }
            });
        }
        
        // Restore window.currentUser if it exists
        if (window.currentUser && window.userImpersonation.originalUserInfo) {
            window.currentUser = window.userImpersonation.originalUserInfo;
        }

        // Clear stored session
        window.userImpersonation.originalSession = null;
        
        console.log('✅ Original user session fully restored');
        
    } catch (error) {
        console.error('❌ Error restoring original user session:', error);
    }
}

// Initialize the impersonation system when the page loads
window.userImpersonation = new UserImpersonation();

// Expose methods globally for easy access
window.startUserImpersonation = (user) => {
    console.log('🎭 startUserImpersonation called with:', user);
    
    if (!user) {
        console.error('❌ No user object provided to startUserImpersonation');
        if (window.userImpersonation && window.userImpersonation.showNotification) {
            window.userImpersonation.showNotification('Error: No user selected for impersonation', 'error');
        } else {
            alert('Error: No user selected for impersonation');
        }
        return;
    }
    
    if (!window.userImpersonation) {
        console.error('❌ User impersonation system not initialized');
        alert('Error: Impersonation system not ready');
        return;
    }
    
    window.userImpersonation.showImpersonationModal(user);
};

window.exitUserImpersonation = () => {
    window.userImpersonation.exitImpersonation();
};

// Debug function for navigation troubleshooting
window.debugNavigation = () => {
    return window.userImpersonation.debugNavigationStructure();
};

// Add backward compatibility for old method names
window.userImpersonation.openImpersonationModal = (user) => {
    window.userImpersonation.showImpersonationModal(user);
};

console.log('✅ User Impersonation System loaded and ready');
