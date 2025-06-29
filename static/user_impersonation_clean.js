/**
 * User Impersonation System - Clean Implementation
 * Allows administrators to seamlessly log in as other users to provide support
 */

class UserImpersonation {
    constructor() {
        this.originalUserInfo = null;
        this.currentImpersonatedUser = null;
        this.isImpersonating = false;
        this.impersonationBanner = null;
        this.hiddenElements = []; // Track elements that are hidden during impersonation
        this.preservedNavigation = null; // Store a copy of the original navigation
        
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
        }
        
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
                this.currentImpersonatedUser = data.impersonatedUser;
                this.isImpersonating = true;
                console.log('🎭 Restoring impersonation state:', this.currentImpersonatedUser.email);
            } catch (error) {
                console.error('Error restoring impersonation state:', error);
                this.clearImpersonation();
            }
        }
    }

    /**
     * Create the impersonation banner that shows at the top when impersonating
     */
    createImpersonationBanner() {
        if (this.isImpersonating && !this.impersonationBanner) {
            if (!document.body) {
                setTimeout(() => this.createImpersonationBanner(), 100);
                return;
            }

            const banner = document.createElement('div');
            banner.id = 'impersonation-banner';
            banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #e74c3c, #c0392b);
                color: white;
                padding: 8px 20px;
                z-index: 99999;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                font-weight: 500;
                display: flex;
                justify-content: space-between;
                align-items: center;
                height: 40px;
                border-bottom: 2px solid rgba(0,0,0,0.1);
            `;

            const text = document.createElement('span');
            text.innerHTML = `
                <span style="font-size: 16px; margin-right: 8px;">👤</span>
                <strong>Impersonating:</strong> ${this.currentImpersonatedUser.email} 
                (${this.currentImpersonatedUser.displayName || 'No Display Name'})
            `;

            const exitButton = document.createElement('button');
            exitButton.textContent = 'Exit Impersonation';
            exitButton.style.cssText = `
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
            `;
            exitButton.addEventListener('click', () => this.exitImpersonation());

            banner.appendChild(text);
            banner.appendChild(exitButton);

            document.body.insertBefore(banner, document.body.firstChild);
            this.impersonationBanner = banner;

            // Adjust body padding to account for banner
            document.body.style.paddingTop = '40px';

            console.log('🎭 Impersonation banner created');
        }
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
        const currentRole = this.getCurrentUserRole();
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
     * Start impersonating a user
     */
    async startImpersonation(targetUser) {
        console.log('🎭 Starting impersonation for:', targetUser);

        try {
            // Check permissions
            if (!this.canImpersonate(targetUser)) {
                throw new Error('Insufficient permissions to impersonate this user');
            }

            // Store original user info if not already impersonating
            if (!this.isImpersonating) {
                this.originalUserInfo = this.getCurrentUserInfo();
                console.log('💾 Storing original user info:', this.originalUserInfo);
            }

            // Set impersonation state
            this.currentImpersonatedUser = targetUser;
            this.isImpersonating = true;

            // Store in localStorage for persistence
            const impersonationData = {
                originalUser: this.originalUserInfo,
                impersonatedUser: this.currentImpersonatedUser,
                timestamp: Date.now()
            };
            localStorage.setItem('impersonationData', JSON.stringify(impersonationData));

            // Create banner
            this.createImpersonationBanner();

            // Update navigation and UI
            this.updateNavigationForImpersonation();
            this.hideAdminFunctionsForRole(targetUser.role);

            // Emit success event
            document.dispatchEvent(new CustomEvent('impersonationStarted', {
                detail: { user: targetUser }
            }));

            console.log('✅ Impersonation started successfully');

        } catch (error) {
            console.error('❌ Failed to start impersonation:', error);
            throw error;
        }
    }

    /**
     * Exit impersonation and return to original user
     */
    exitImpersonation() {
        console.log('🎭 Exiting impersonation...');

        try {
            // Clear impersonation state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;

            // Remove from localStorage
            localStorage.removeItem('impersonationData');

            // Remove banner
            if (this.impersonationBanner) {
                this.impersonationBanner.remove();
                this.impersonationBanner = null;
                document.body.style.paddingTop = '';
            }

            // Restore admin functions
            this.restoreAdminFunctions();

            // Restore navigation
            this.refreshGlobalNavigation();

            // Clear original user info
            this.originalUserInfo = null;

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
        localStorage.removeItem('impersonationData');
        
        if (this.impersonationBanner) {
            this.impersonationBanner.remove();
            this.impersonationBanner = null;
            document.body.style.paddingTop = '';
        }
    }

    /**
     * Update navigation header to show impersonated user
     */
    updateNavigationForImpersonation() {
        if (!this.isImpersonating) return;

        console.log('🔄 Updating navigation for impersonation');

        const nav = document.getElementById('global-nav');
        if (!nav) {
            console.warn('⚠️ Global navigation not found');
            return;
        }

        // Update user display in navigation
        const userDisplays = nav.querySelectorAll('[data-user-display], .user-name, .user-email');
        userDisplays.forEach(element => {
            if (element.dataset.userDisplay === 'name' || element.classList.contains('user-name')) {
                element.textContent = this.currentImpersonatedUser.displayName || this.currentImpersonatedUser.email;
            } else if (element.dataset.userDisplay === 'email' || element.classList.contains('user-email')) {
                element.textContent = this.currentImpersonatedUser.email;
            }
        });

        console.log('✅ Navigation updated for impersonation');
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
     * Show the user selection modal
     */
    showUserSelectionModal() {
        console.log('🎭 Opening user selection modal');

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.id = 'impersonation-modal-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 100000;
            display: flex;
            justify-content: center;
            align-items: center;
        `;

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'impersonation-modal';
        modal.style.cssText = `
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        `;

        // Modal header
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;

        const title = document.createElement('h3');
        title.textContent = 'Select User to Impersonate';
        title.style.margin = '0';

        const closeButton = document.createElement('button');
        closeButton.innerHTML = '×';
        closeButton.style.cssText = `
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
        `;
        closeButton.addEventListener('click', () => overlay.remove());

        header.appendChild(title);
        header.appendChild(closeButton);

        // Search input
        const searchContainer = document.createElement('div');
        searchContainer.style.padding = '20px';

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search users by name or email...';
        searchInput.style.cssText = `
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        `;

        searchContainer.appendChild(searchInput);

        // User list container
        const userListContainer = document.createElement('div');
        userListContainer.style.cssText = `
            flex: 1;
            overflow-y: auto;
            padding: 0 20px 20px;
        `;

        const userList = document.createElement('div');
        userList.id = 'user-list';
        userListContainer.appendChild(userList);

        // Assemble modal
        modal.appendChild(header);
        modal.appendChild(searchContainer);
        modal.appendChild(userListContainer);
        overlay.appendChild(modal);

        // Add to document
        document.body.appendChild(overlay);

        // Load and display users
        this.loadUsers(userList, searchInput);

        // Close modal when clicking outside
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });
    }

    /**
     * Load users and populate the list
     */
    async loadUsers(userList, searchInput) {
        console.log('👥 Loading users for impersonation selection');

        try {
            // Show loading state
            userList.innerHTML = '<div style="text-align: center; padding: 20px;">Loading users...</div>';

            // Try to get users from API or use mock data
            let users = [];
            
            try {
                // Attempt to fetch from API
                const response = await fetch('/api/users');
                if (response.ok) {
                    users = await response.json();
                } else {
                    throw new Error('API not available');
                }
            } catch (error) {
                console.log('📝 Using mock users for demo');
                // Use mock data for demonstration
                users = this.getMockUsers();
            }

            // Filter users based on permissions
            const currentRole = this.getCurrentUserRole();
            const allowedUsers = users.filter(user => this.canImpersonate(user));

            console.log(`👥 Found ${allowedUsers.length} users available for impersonation`);

            // Render users
            this.renderUserList(userList, allowedUsers, searchInput);

        } catch (error) {
            console.error('❌ Failed to load users:', error);
            userList.innerHTML = '<div style="text-align: center; padding: 20px; color: red;">Failed to load users</div>';
        }
    }

    /**
     * Get mock users for demonstration
     */
    getMockUsers() {
        return [
            {
                id: '1',
                email: 'john.doe@example.com',
                displayName: 'John Doe',
                role: 'user',
                department: 'Sales',
                lastLogin: '2024-01-15'
            },
            {
                id: '2',
                email: 'jane.smith@example.com',
                displayName: 'Jane Smith',
                role: 'supervisor',
                department: 'Marketing',
                lastLogin: '2024-01-14'
            },
            {
                id: '3',
                email: 'mike.johnson@example.com',
                displayName: 'Mike Johnson',
                role: 'manager',
                department: 'Operations',
                lastLogin: '2024-01-13'
            },
            {
                id: '4',
                email: 'sarah.wilson@example.com',
                displayName: 'Sarah Wilson',
                role: 'user',
                department: 'Support',
                lastLogin: '2024-01-12'
            },
            {
                id: '5',
                email: 'tom.brown@example.com',
                displayName: 'Tom Brown',
                role: 'user',
                department: 'Development',
                lastLogin: '2024-01-11'
            }
        ];
    }

    /**
     * Render the user list
     */
    renderUserList(userList, users, searchInput) {
        let filteredUsers = users;

        const renderUsers = () => {
            if (filteredUsers.length === 0) {
                userList.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">No users found</div>';
                return;
            }

            userList.innerHTML = filteredUsers.map(user => `
                <div class="user-item" data-user-id="${user.id}" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    border: 1px solid #eee;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    cursor: pointer;
                    transition: background-color 0.2s;
                " onmouseover="this.style.backgroundColor='#f5f5f5'" onmouseout="this.style.backgroundColor='white'">
                    <div>
                        <div style="font-weight: 500; color: #333;">${user.displayName || user.email}</div>
                        <div style="font-size: 12px; color: #666;">${user.email}</div>
                        <div style="font-size: 11px; color: #999;">
                            Role: ${user.role} ${user.department ? `• ${user.department}` : ''}
                        </div>
                    </div>
                    <button class="impersonate-btn" style="
                        background: #007cba;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    " onmouseover="this.style.backgroundColor='#005a87'" onmouseout="this.style.backgroundColor='#007cba'">
                        Impersonate
                    </button>
                </div>
            `).join('');

            // Add click handlers
            userList.querySelectorAll('.impersonate-btn').forEach((btn, index) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.startImpersonationFromModal(filteredUsers[index]);
                });
            });
        };

        // Initial render
        renderUsers();

        // Search functionality
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filteredUsers = users.filter(user => 
                user.email.toLowerCase().includes(searchTerm) ||
                (user.displayName && user.displayName.toLowerCase().includes(searchTerm))
            );
            renderUsers();
        });
    }

    /**
     * Start impersonation from modal selection
     */
    async startImpersonationFromModal(user) {
        console.log('🎭 Starting impersonation from modal for:', user.email);

        try {
            await this.startImpersonation(user);
            
            // Close modal
            const overlay = document.getElementById('impersonation-modal-overlay');
            if (overlay) {
                overlay.remove();
            }

            // Show success message
            this.showNotification(`Now impersonating: ${user.displayName || user.email}`, 'success');

        } catch (error) {
            console.error('❌ Failed to start impersonation:', error);
            this.showNotification(`Failed to impersonate user: ${error.message}`, 'error');
        }
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: ${this.isImpersonating ? '50px' : '10px'};
            right: 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 100001;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            max-width: 400px;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the impersonation system when the page loads
window.userImpersonation = new UserImpersonation();

// Expose methods globally for easy access
window.startUserImpersonation = () => {
    window.userImpersonation.showUserSelectionModal();
};

window.exitUserImpersonation = () => {
    window.userImpersonation.exitImpersonation();
};

console.log('✅ User Impersonation System loaded and ready');
