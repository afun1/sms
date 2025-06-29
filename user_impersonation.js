/**
 * User Impersonation System - GHL Style Implementation
 * Allows administrators to seamlessly log in as other users to provide support
 */

class UserImpersonation {
    constructor() {
        this.originalUserInfo = null;
        this.currentImpersonatedUser = null;
        this.isImpersonating = false;
        this.impersonationBanner = null;
        
        this.init();
    }

    init() {
        console.log('🎭 Initializing User Impersonation System...');
        this.checkImpersonationState();
        this.createImpersonationBanner();
        this.setupEventListeners();
        console.log('✅ User Impersonation System initialized');
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
            const banner = document.createElement('div');
            banner.id = 'impersonation-banner';
            banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #e74c3c, #c0392b);
                color: white;
                padding: 12px 20px;
                z-index: 10000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                font-weight: 500;
                display: flex;
                justify-content: space-between;
                align-items: center;
                animation: slideDown 0.3s ease-out;
            `;

            const userName = this.currentImpersonatedUser.display_name || 
                           `${this.currentImpersonatedUser.first_name || ''} ${this.currentImpersonatedUser.last_name || ''}`.trim() ||
                           this.currentImpersonatedUser.email;

            banner.innerHTML = `
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="font-size: 1.1em;">🎭</span>
                    <div>
                        <div style="font-size: 1.1em; font-weight: 600;">
                            Logged in as ${userName}
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.9;">
                            Role: ${this.currentImpersonatedUser.role || 'user'} • Email: ${this.currentImpersonatedUser.email}
                        </div>
                    </div>
                </div>
                <button id="switch-back-btn" style="
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: 1px solid rgba(255,255,255,0.3);
                    padding: 8px 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.2s;
                " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
                   onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                    ↩️ Switch to my account
                </button>
            `;

            // Add CSS animation
            if (!document.getElementById('impersonation-styles')) {
                const styles = document.createElement('style');
                styles.id = 'impersonation-styles';
                styles.textContent = `
                    @keyframes slideDown {
                        from { transform: translateY(-100%); }
                        to { transform: translateY(0); }
                    }
                    @keyframes slideUp {
                        from { transform: translateY(0); }
                        to { transform: translateY(-100%); }
                    }
                    .slide-up {
                        animation: slideUp 0.3s ease-in;
                    }
                    body.impersonating {
                        padding-top: 80px !important;
                    }
                `;
                document.head.appendChild(styles);
            }

            document.body.insertBefore(banner, document.body.firstChild);
            document.body.classList.add('impersonating');
            this.impersonationBanner = banner;

            // Add event listener for switch back button
            document.getElementById('switch-back-btn').addEventListener('click', () => {
                this.switchBackToOriginalUser();
            });
        }
    }

    /**
     * Create the user selection dropdown (similar to GHL)
     */
    createUserSelectionDropdown() {
        const dropdown = document.createElement('div');
        dropdown.id = 'user-impersonation-dropdown';
        dropdown.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 10001;
            width: 500px;
            max-width: 90vw;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        `;

        dropdown.innerHTML = `
            <div style="padding: 25px 25px 15px; border-bottom: 1px solid #eee;">
                <h3 style="margin: 0; font-size: 1.3em; color: #2c3e50;">
                    🎭 Log in as User
                </h3>
                <p style="margin: 8px 0 0; color: #7f8c8d; font-size: 0.95em;">
                    ${this.getModalDescription()}
                </p>
            </div>
            
            <div style="padding: 20px 25px 15px;">
                <div style="position: relative;">
                    <input type="text" id="user-search-input" placeholder="🔍 Search by name or email..."
                           style="width: 100%; padding: 12px 15px; border: 2px solid #e9ecef; 
                                  border-radius: 8px; font-size: 1em; transition: border-color 0.2s;"
                           onfocus="this.style.borderColor='#3498db'"
                           onblur="this.style.borderColor='#e9ecef'">
                </div>
            </div>
            
            <div id="user-list-container" style="flex: 1; overflow-y: auto; max-height: 400px; border-top: 1px solid #f8f9fa;">
                <div id="user-list" style="padding: 10px 0;"></div>
            </div>
            
            <div style="padding: 15px 25px; border-top: 1px solid #eee; text-align: right;">
                <button id="cancel-impersonation" style="
                    background: #95a5a6; color: white; border: none; padding: 10px 20px;
                    border-radius: 6px; cursor: pointer; font-weight: 500; margin-right: 10px;"
                    onmouseover="this.style.background='#7f8c8d'"
                    onmouseout="this.style.background='#95a5a6'">
                    Cancel
                </button>
            </div>
        `;

        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'impersonation-backdrop';
        backdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 10000;
        `;

        document.body.appendChild(backdrop);
        document.body.appendChild(dropdown);

        // Setup event listeners
        this.setupDropdownEventListeners(dropdown);
        
        return dropdown;
    }

    /**
     * Setup event listeners for the dropdown
     */
    setupDropdownEventListeners(dropdown) {
        const searchInput = dropdown.querySelector('#user-search-input');
        const cancelBtn = dropdown.querySelector('#cancel-impersonation');
        const backdrop = document.getElementById('impersonation-backdrop');

        // Search functionality
        searchInput.addEventListener('input', (e) => {
            this.filterUsers(e.target.value);
        });

        // Close modal on cancel or backdrop click
        cancelBtn.addEventListener('click', () => this.closeImpersonationModal());
        backdrop.addEventListener('click', () => this.closeImpersonationModal());

        // Keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeImpersonationModal();
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateUserList('down');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateUserList('up');
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.selectFocusedUser();
            }
        });

        // Focus search input
        setTimeout(() => searchInput.focus(), 100);
    }

    /**
     * Open the user impersonation modal
     */
    async openImpersonationModal() {
        console.log('🎭 Opening impersonation modal...');
        
        // Check if user has permission to impersonate
        const canImpersonate = this.canImpersonate();
        console.log('🔐 Can impersonate:', canImpersonate);
        
        if (!canImpersonate) {
            const userRole = localStorage.getItem('userRole') || 'user';
            console.log('❌ Access denied for role:', userRole);
            this.showError(`Access denied: ${userRole} role cannot impersonate other users.`);
            return;
        }

        if (this.isImpersonating) {
            console.log('⚠️ Already impersonating, showing error');
            this.showError('You are already impersonating a user. Switch back first.');
            return;
        }

        try {
            console.log('📝 Storing original user info...');
            // Store original user info
            this.storeOriginalUserInfo();

            console.log('🪟 Creating dropdown modal...');
            // Create and show dropdown
            const dropdown = this.createUserSelectionDropdown();
            
            console.log('👥 Loading available users...');
            // Load and display users
            await this.loadAvailableUsers();
            
            console.log('✅ Modal opened successfully');
        } catch (error) {
            console.error('💥 Error opening impersonation modal:', error);
            this.showError('Failed to open impersonation modal: ' + error.message);
        }
    }

    /**
     * Store original user information before impersonation
     */
    storeOriginalUserInfo() {
        this.originalUserInfo = {
            id: this.getCurrentUserId(),
            email: localStorage.getItem('userEmail') || 'admin@example.com',
            username: localStorage.getItem('username') || 'Admin',
            role: localStorage.getItem('userRole') || 'admin',
            display_name: localStorage.getItem('displayName') || localStorage.getItem('username') || 'Admin'
        };
    }

    /**
     * Get current user ID
     */
    getCurrentUserId() {
        return localStorage.getItem('userId') || 'admin-user-id';
    }

    /**
     * Load available users for impersonation
     */
    async loadAvailableUsers() {
        try {
            // Get users from the global allUsers array or load from database
            let users = window.allUsers || [];
            
            if (!users.length && window.supabase) {
                // Load from database if not available
                const { data, error } = await window.supabase
                    .from('profiles')
                    .select('*')
                    .order('first_name');
                
                if (error) throw error;
                users = data || [];
            }

            // Filter users based on current user's role and hierarchy
            const availableUsers = await this.filterUsersByHierarchy(users);
            
            this.displayUsers(availableUsers);
            this.allAvailableUsers = availableUsers;
            
        } catch (error) {
            console.error('Error loading users:', error);
            this.showError('Failed to load users. Please try again.');
        }
    }

    /**
     * Filter users based on current user's role and hierarchy permissions
     */
    async filterUsersByHierarchy(allUsers) {
        const currentUserId = this.getCurrentUserId();
        const currentUserRole = localStorage.getItem('userRole')?.toLowerCase();
        
        // Exclude current user from the list
        let availableUsers = allUsers.filter(user => user.id !== currentUserId);
        
        switch (currentUserRole) {
            case 'admin':
                // Admins can impersonate everyone
                return availableUsers;
                
            case 'supervisor':
                // Supervisors can impersonate:
                // 1. Managers assigned to them (manager.supervisor_id === currentUserId)
                // 2. Users assigned to those managers (user.manager_id === manager.id)
                return this.filterUsersForSupervisor(availableUsers, currentUserId);
                
            case 'manager':
                // Managers can impersonate:
                // 1. Only users assigned to them (user.manager_id === currentUserId)
                return this.filterUsersForManager(availableUsers, currentUserId);
                
            default:
                // Regular users cannot impersonate anyone
                return [];
        }
    }

    /**
     * Filter users for supervisor role
     */
    filterUsersForSupervisor(allUsers, supervisorId) {
        const allowedUsers = [];
        
        // Find managers assigned to this supervisor
        const managersUnderSupervisor = allUsers.filter(user => 
            user.role?.toLowerCase() === 'manager' && 
            user.supervisor_id === supervisorId
        );
        
        // Add the managers themselves
        allowedUsers.push(...managersUnderSupervisor);
        
        // Find users assigned to those managers
        const managerIds = managersUnderSupervisor.map(manager => manager.id);
        const usersUnderManagers = allUsers.filter(user =>
            user.role?.toLowerCase() === 'user' &&
            managerIds.includes(user.manager_id)
        );
        
        // Add the users
        allowedUsers.push(...usersUnderManagers);
        
        console.log(`🎯 Supervisor ${supervisorId} can impersonate:`, {
            managers: managersUnderSupervisor.length,
            users: usersUnderManagers.length,
            total: allowedUsers.length
        });
        
        return allowedUsers;
    }

    /**
     * Filter users for manager role
     */
    filterUsersForManager(allUsers, managerId) {
        // Managers can only impersonate users directly assigned to them
        const usersUnderManager = allUsers.filter(user =>
            user.role?.toLowerCase() === 'user' &&
            user.manager_id === managerId
        );
        
        console.log(`👔 Manager ${managerId} can impersonate ${usersUnderManager.length} users`);
        
        return usersUnderManager;
    }

    /**
     * Display users in the list
     */
    displayUsers(users) {
        const userList = document.getElementById('user-list');
        if (!userList) return;

        if (!users.length) {
            const currentUserRole = localStorage.getItem('userRole') || 'user';
            let noUsersMessage = 'No users available for impersonation';
            
            switch (currentUserRole.toLowerCase()) {
                case 'manager':
                    noUsersMessage = 'No users assigned to you for impersonation';
                    break;
                case 'supervisor':
                    noUsersMessage = 'No managers or users under your supervision for impersonation';
                    break;
                case 'admin':
                    noUsersMessage = 'No other users found in the system';
                    break;
            }
            
            userList.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: #7f8c8d;">
                    <div style="font-size: 2em; margin-bottom: 10px;">👥</div>
                    <div style="font-weight: 500; margin-bottom: 8px;">${noUsersMessage}</div>
                    <div style="font-size: 0.9em; color: #95a5a6;">
                        ${this.getHierarchyExplanation(currentUserRole)}
                    </div>
                </div>
            `;
            return;
        }

        const userItems = users.map((user, index) => {
            const userName = user.display_name || 
                           `${user.first_name || ''} ${user.last_name || ''}`.trim() ||
                           user.email;
            
            const roleColor = this.getRoleColor(user.role);
            const secondaryRole = user.secondary_role ? ` + ${user.secondary_role}` : '';
            
            // Add hierarchy indicator
            const hierarchyInfo = this.getHierarchyIndicator(user);

            return `
                <div class="user-item" data-user-id="${user.id}" data-index="${index}"
                     style="padding: 15px 25px; cursor: pointer; border-bottom: 1px solid #f8f9fa;
                            transition: background-color 0.2s; display: flex; justify-content: space-between; align-items: center;"
                     onmouseover="this.style.backgroundColor='#f8f9fa'"
                     onmouseout="this.style.backgroundColor='white'"
                     onclick="userImpersonation.impersonateUser('${user.id}')">
                    
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1em; color: #2c3e50; margin-bottom: 4px;">
                            ${userName}
                        </div>
                        <div style="color: #7f8c8d; font-size: 0.9em; margin-bottom: 6px;">
                            ${user.email}
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: ${roleColor}; color: white; padding: 3px 8px; 
                                         border-radius: 12px; font-size: 0.8em; font-weight: 500;">
                                ${user.role || 'user'}${secondaryRole}
                            </span>
                            ${hierarchyInfo}
                        </div>
                    </div>
                    
                    <div style="color: #bdc3c7; font-size: 1.2em;">
                        👤
                    </div>
                </div>
            `;
        }).join('');

        userList.innerHTML = userItems;
    }

    /**
     * Get modal description based on current user role
     */
    getModalDescription() {
        const userRole = localStorage.getItem('userRole')?.toLowerCase() || 'user';
        
        switch (userRole) {
            case 'admin':
                return 'As an admin, you can impersonate any user in the system for support purposes';
            case 'supervisor':
                return 'As a supervisor, you can impersonate managers assigned to you and their users';
            case 'manager':
                return 'As a manager, you can impersonate users directly assigned to you';
            default:
                return 'Select a user to impersonate for support purposes';
        }
    }

    /**
     * Get hierarchy explanation text for empty state
     */
    getHierarchyExplanation(userRole) {
        switch (userRole.toLowerCase()) {
            case 'admin':
                return 'As an admin, you can impersonate all users in the system.';
            case 'supervisor':
                return 'As a supervisor, you can impersonate managers assigned to you and their users.';
            case 'manager':
                return 'As a manager, you can impersonate users directly assigned to you.';
            default:
                return 'Contact your administrator for impersonation access.';
        }
    }

    /**
     * Get hierarchy indicator for a user
     */
    getHierarchyIndicator(user) {
        const currentUserId = this.getCurrentUserId();
        const currentUserRole = localStorage.getItem('userRole')?.toLowerCase();
        
        if (currentUserRole === 'admin') {
            return ''; // Admins don't need hierarchy indicators
        }
        
        if (currentUserRole === 'supervisor') {
            if (user.role?.toLowerCase() === 'manager' && user.supervisor_id === currentUserId) {
                return '<span style="background: #3498db; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7em;">Your Manager</span>';
            } else if (user.role?.toLowerCase() === 'user') {
                return '<span style="background: #95a5a6; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7em;">Under Your Managers</span>';
            }
        }
        
        if (currentUserRole === 'manager') {
            if (user.manager_id === currentUserId) {
                return '<span style="background: #27ae60; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7em;">Your User</span>';
            }
        }
        
        return '';
    }

    /**
     * Filter users based on search term
     */
    filterUsers(searchTerm) {
        if (!this.allAvailableUsers) return;

        const filtered = this.allAvailableUsers.filter(user => {
            const searchString = `${user.first_name || ''} ${user.last_name || ''} ${user.email || ''} ${user.display_name || ''}`.toLowerCase();
            return searchString.includes(searchTerm.toLowerCase());
        });

        this.displayUsers(filtered);
    }

    /**
     * Navigate user list with keyboard
     */
    navigateUserList(direction) {
        const userItems = document.querySelectorAll('.user-item');
        let currentIndex = -1;
        
        // Find currently focused item
        userItems.forEach((item, index) => {
            if (item.style.backgroundColor === 'rgb(52, 152, 219)' || item.classList.contains('focused')) {
                currentIndex = index;
            }
        });

        // Remove previous focus
        userItems.forEach(item => {
            item.style.backgroundColor = 'white';
            item.style.color = '';
            item.classList.remove('focused');
        });

        // Calculate new index
        if (direction === 'down') {
            currentIndex = currentIndex < userItems.length - 1 ? currentIndex + 1 : 0;
        } else {
            currentIndex = currentIndex > 0 ? currentIndex - 1 : userItems.length - 1;
        }

        // Apply new focus
        if (userItems[currentIndex]) {
            const item = userItems[currentIndex];
            item.style.backgroundColor = '#3498db';
            item.style.color = 'white';
            item.classList.add('focused');
            item.scrollIntoView({ block: 'nearest' });
        }
    }

    /**
     * Select the currently focused user
     */
    selectFocusedUser() {
        const focusedItem = document.querySelector('.user-item.focused');
        if (focusedItem) {
            const userId = focusedItem.getAttribute('data-user-id');
            this.impersonateUser(userId);
        }
    }

    /**
     * Impersonate a specific user
     */
    async impersonateUser(userId) {
        try {
            const user = this.allAvailableUsers.find(u => u.id === userId);
            if (!user) {
                throw new Error('User not found');
            }

            // Store impersonation data
            const impersonationData = {
                originalUser: this.originalUserInfo,
                impersonatedUser: user,
                timestamp: new Date().toISOString()
            };

            localStorage.setItem('impersonationData', JSON.stringify(impersonationData));

            // Update localStorage to reflect impersonated user
            localStorage.setItem('userId', user.id);
            localStorage.setItem('userEmail', user.email);
            localStorage.setItem('userRole', user.role || 'user');
            localStorage.setItem('username', user.display_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email);

            // Update instance state
            this.currentImpersonatedUser = user;
            this.isImpersonating = true;

            // Close modal
            this.closeImpersonationModal();

            // Create impersonation banner
            this.createImpersonationBanner();

            // Show success message
            this.showSuccessMessage(`Now logged in as ${user.display_name || user.email}`);

            // Refresh the page to load data for the impersonated user
            if (window.loadUsersWithHierarchy) {
                await window.loadUsersWithHierarchy();
            } else {
                setTimeout(() => location.reload(), 1000);
            }

        } catch (error) {
            console.error('Error impersonating user:', error);
            this.showError('Failed to impersonate user: ' + error.message);
        }
    }

    /**
     * Switch back to original user
     */
    switchBackToOriginalUser() {
        try {
            if (!this.isImpersonating || !this.originalUserInfo) {
                return;
            }

            // Restore original user data
            localStorage.setItem('userId', this.originalUserInfo.id);
            localStorage.setItem('userEmail', this.originalUserInfo.email);
            localStorage.setItem('userRole', this.originalUserInfo.role);
            localStorage.setItem('username', this.originalUserInfo.username);

            // Clear impersonation data
            localStorage.removeItem('impersonationData');

            // Update instance state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;

            // Remove banner
            if (this.impersonationBanner) {
                this.impersonationBanner.classList.add('slide-up');
                setTimeout(() => {
                    if (this.impersonationBanner && this.impersonationBanner.parentNode) {
                        this.impersonationBanner.parentNode.removeChild(this.impersonationBanner);
                        this.impersonationBanner = null;
                    }
                    document.body.classList.remove('impersonating');
                }, 300);
            }

            // Show success message
            this.showSuccessMessage(`Switched back to ${this.originalUserInfo.username}`);

            // Refresh the page
            if (window.loadUsersWithHierarchy) {
                setTimeout(() => window.loadUsersWithHierarchy(), 500);
            } else {
                setTimeout(() => location.reload(), 1000);
            }

            this.originalUserInfo = null;

        } catch (error) {
            console.error('Error switching back to original user:', error);
            this.showError('Failed to switch back: ' + error.message);
        }
    }

    /**
     * Close the impersonation modal
     */
    closeImpersonationModal() {
        const dropdown = document.getElementById('user-impersonation-dropdown');
        const backdrop = document.getElementById('impersonation-backdrop');

        if (dropdown) dropdown.remove();
        if (backdrop) backdrop.remove();
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Listen for escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById('user-impersonation-dropdown')) {
                this.closeImpersonationModal();
            }
        });
    }

    /**
     * Get role color for styling
     */
    getRoleColor(role) {
        const colors = {
            'admin': '#e74c3c',
            'supervisor': '#f39c12',
            'manager': '#3498db',
            'user': '#95a5a6'
        };
        return colors[role?.toLowerCase()] || '#95a5a6';
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        this.showToast(message, '#27ae60');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showToast(message, '#e74c3c');
    }

    /**
     * Show toast notification
     */
    showToast(message, backgroundColor = '#27ae60') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10002;
            font-weight: 500;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Check if user has privileges to impersonate others
     */
    canImpersonate() {
        const userRole = localStorage.getItem('userRole')?.toLowerCase();
        const canImpersonate = userRole === 'admin' || userRole === 'supervisor' || userRole === 'manager';
        console.log('🔐 Checking impersonation permissions:', { userRole, canImpersonate });
        return canImpersonate;
    }

    /**
     * Clear impersonation data and reset state
     */
    clearImpersonation() {
        try {
            // Clear localStorage
            localStorage.removeItem('impersonationData');
            
            // Reset instance state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;
            this.originalUserInfo = null;
            
            // Remove banner if it exists
            if (this.impersonationBanner && this.impersonationBanner.parentNode) {
                this.impersonationBanner.parentNode.removeChild(this.impersonationBanner);
                this.impersonationBanner = null;
            }
            
            document.body.classList.remove('impersonating');
            
            console.log('🧹 Impersonation data cleared');
        } catch (error) {
            console.error('Error clearing impersonation:', error);
        }
    }

    /**
     * Debug method to check system state
     */
    debugSystemState() {
        console.log('🔍 User Impersonation System Debug Info:');
        console.log('- Is Impersonating:', this.isImpersonating);
        console.log('- Current User Role:', localStorage.getItem('userRole'));
        console.log('- Current User ID:', localStorage.getItem('userId'));
        console.log('- Current Username:', localStorage.getItem('username'));
        console.log('- Can Impersonate:', this.canImpersonate());
        console.log('- Available Users:', window.allUsers?.length || 0);
        console.log('- Impersonation Data:', localStorage.getItem('impersonationData'));
        
        // Test modal creation
        try {
            console.log('🧪 Testing modal creation...');
            const testDiv = document.createElement('div');
            testDiv.style.cssText = 'position:fixed;top:50%;left:50%;background:red;padding:20px;z-index:10000;';
            testDiv.textContent = 'Test Modal - Click to close';
            testDiv.onclick = () => testDiv.remove();
            document.body.appendChild(testDiv);
            console.log('✅ Modal creation test successful');
        } catch (error) {
            console.error('❌ Modal creation test failed:', error);
        }
    }
}

// Initialize the impersonation system
const userImpersonation = new UserImpersonation();

// Make it globally available
window.userImpersonation = userImpersonation;

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserImpersonation;
}
