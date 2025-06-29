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
        
        // Set up navigation protection immediately
        this.setupNavigationProtection();
        
        // Ensure banner persists and navigation is updated for impersonation
        if (this.isImpersonating) {
            this.ensureBannerPersistence();
            setTimeout(() => {
                this.updateNavigationForImpersonation();
            }, 500);
        }
        
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
            // Safety check for document.body
            if (!document.body) {
                console.warn('🎭 Document body not ready, retrying banner creation...');
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
                animation: slideDown 0.3s ease-out;
                height: 40px;
                border-bottom: 2px solid rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
                font-size: 0.9em;
            `;

            const userName = this.currentImpersonatedUser.display_name || 
                           `${this.currentImpersonatedUser.first_name || ''} ${this.currentImpersonatedUser.last_name || ''}`.trim() ||
                           this.currentImpersonatedUser.email;

            banner.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.1em;">🎭</span>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-weight: 600;">
                            Impersonating: ${userName}
                        </span>
                        <span style="font-size: 0.85em; opacity: 0.9;">
                            ${this.currentImpersonatedUser.role || 'user'} • ${this.currentImpersonatedUser.email}
                        </span>
                    </div>
                </div>
                <button id="switch-back-btn" style="
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: 1px solid rgba(255,255,255,0.3);
                    padding: 6px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.2s;
                    font-size: 0.85em;
                " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
                   onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                    ↩️ Switch Back
                </button>
            `;

            // Add CSS animation (without the problematic body styles)
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
                `;
                document.head.appendChild(styles);
            }

            document.body.insertBefore(banner, document.body.firstChild);
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
        
        // IMMEDIATELY check and preserve navigation
        const navAtStart = document.getElementById('global-nav');
        console.log('🔍 Navigation at modal open:', !!navAtStart, navAtStart ? 'visible' : 'missing');
        if (navAtStart) {
            // Clone the navigation before doing anything else
            this.preservedNavigation = navAtStart.cloneNode(true);
            console.log('💾 Navigation cloned and preserved');
        }
        
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

            // Check navigation after storing user info
            const navAfterStore = document.getElementById('global-nav');
            console.log('🔍 Navigation after storing user info:', !!navAfterStore, navAfterStore ? 'visible' : 'missing');

            console.log('🪟 Creating dropdown modal...');
            // Create and show dropdown
            const dropdown = this.createUserSelectionDropdown();
            
            // Check navigation after creating dropdown
            const navAfterDropdown = document.getElementById('global-nav');
            console.log('� Navigation after creating dropdown:', !!navAfterDropdown, navAfterDropdown ? 'visible' : 'missing');
            
            console.log('�👥 Loading available users...');
            // Load and display users
            await this.loadAvailableUsers();
            
            // Check navigation after loading users
            const navAfterLoad = document.getElementById('global-nav');
            console.log('🔍 Navigation after loading users:', !!navAfterLoad, navAfterLoad ? 'visible' : 'missing');
            
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
            console.log('🎭 Starting impersonation for user:', userId);
            
            // Check navigation BEFORE impersonation
            const navBefore = document.getElementById('global-nav');
            console.log('🔍 Navigation before impersonation:', !!navBefore, navBefore ? 'visible' : 'missing');
            this.debugNavigationState();
            
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

            // Check navigation AFTER localStorage changes
            const navAfterStorage = document.getElementById('global-nav');
            console.log('🔍 Navigation after localStorage changes:', !!navAfterStorage, navAfterStorage ? 'visible' : 'missing');

            // Create impersonation banner
            this.createImpersonationBanner();

            // Check navigation AFTER banner creation
            const navAfterBanner = document.getElementById('global-nav');
            console.log('🔍 Navigation after banner creation:', !!navAfterBanner, navAfterBanner ? 'visible' : 'missing');

            // Ensure banner persists
            this.ensureBannerPersistence();

            // Show success message
            this.showSuccessMessage(`Now logged in as ${user.display_name || user.email}`);

            // FORCE navigation to be visible before any other operations
            console.log('🔧 Forcing navigation visibility before refresh...');
            this.forceRestoreGlobalNavigation();
            
            // Wait a bit then check again
            setTimeout(() => {
                const navAfterForce = document.getElementById('global-nav');
                console.log('🔍 Navigation after force restore:', !!navAfterForce, navAfterForce ? 'visible' : 'missing');
                
                // Refresh the global navigation to show impersonated user info
                this.refreshGlobalNavigation();
                
                // Check navigation AFTER refresh
                setTimeout(() => {
                    const navAfterRefresh = document.getElementById('global-nav');
                    console.log('🔍 Navigation after refresh:', !!navAfterRefresh, navAfterRefresh ? 'visible' : 'missing');
                    
                    // Refresh the data for the impersonated user without reloading the page
                    if (window.loadUsersWithHierarchy) {
                        setTimeout(async () => {
                            console.log('🔄 Loading users with hierarchy...');
                            await window.loadUsersWithHierarchy();
                            

                            // Check navigation AFTER data load
                            const navAfterDataLoad = document.getElementById('global-nav');
                            console.log('🔍 Navigation after data load:', !!navAfterDataLoad, navAfterDataLoad ? 'visible' : 'missing');
                            
                            // Ensure navigation is visible after data load
                            if (!navAfterDataLoad) {
                                console.log('🚨 Navigation missing after data load - forcing restore...');
                                this.forceRestoreGlobalNavigation();
                            }
                        }, 100);
                    } else {
                        // Force restore navigation if loadUsersWithHierarchy is not available
                        console.log('🔧 loadUsersWithHierarchy not available - forcing restore...');
                        setTimeout(() => {
                            this.forceRestoreGlobalNavigation();
                        }, 500);
                    }
                }, 100);
            }, 100);

        } catch (error) {
            console.error('Error impersonating user:', error);
            this.showError('Failed to impersonate user: ' + error.message);
        }
    }

    /**
     * Refresh global navigation to show impersonated user info
     */
    refreshGlobalNavigation() {
        try {
            console.log('🔄 Refreshing navigation for impersonated user...');
            
            // Ensure global navigation is visible first
            this.ensureGlobalNavigationVisible();
            
            // Update the navigation to show impersonated user's name and hide admin functions
            if (this.isImpersonating) {
                this.updateNavigationForImpersonation();
            }
            
            // Trigger global navigation refresh if available
            if (window.refreshGlobalNavigation) {
                setTimeout(() => {
                    window.refreshGlobalNavigation();
                    this.ensureGlobalNavigationVisible();
                    if (this.isImpersonating) {
                        this.updateNavigationForImpersonation();
                    }
                }, 100);
            } else if (window.setupNav) {
                setTimeout(() => {
                    window.setupNav();
                    this.ensureGlobalNavigationVisible();
                    if (this.isImpersonating) {
                        this.updateNavigationForImpersonation();
                    }
                }, 100);
            }
            
            console.log('🔄 Global navigation refreshed for impersonated user');
        } catch (error) {
            console.error('Error refreshing global navigation:', error);
        }
    }

    /**
     * Ensure impersonation banner persists across page interactions
     */
    ensureBannerPersistence() {
        if (!this.isImpersonating) return;

        // Clear any existing interval to prevent multiple intervals
        if (this.bannerCheckInterval) {
            clearInterval(this.bannerCheckInterval);
            this.bannerCheckInterval = null;
        }

        // Check every 5 seconds (reduced frequency) if banner still exists and recreate if needed
        const bannerCheck = setInterval(() => {
            if (!this.isImpersonating) {
                clearInterval(bannerCheck);
                this.bannerCheckInterval = null;
                return;
            }

            const existingBanner = document.getElementById('impersonation-banner');
            if (!existingBanner && this.isImpersonating) {
                console.log('🎭 Banner missing, recreating...');
                this.impersonationBanner = null; // Reset reference
                this.createImpersonationBanner();
                // Reduced timeout frequency
                setTimeout(() => this.updateNavigationForImpersonation(), 200);
            }
            
            // Also ensure global navigation is always visible (less frequent check)
            const globalNav = document.getElementById('global-nav');
            if (!globalNav || globalNav.style.display === 'none') {
                console.log('🔧 Global navigation missing during impersonation, restoring...');
                this.forceRestoreGlobalNavigation();
            }
        }, 5000); // Increased from 2000ms to 5000ms

        // Store the interval ID so we can clear it later
        this.bannerCheckInterval = bannerCheck;
    }

    /**
     * Update navigation to show impersonated user's information and hide admin functions
     */
    updateNavigationForImpersonation() {
        if (!this.isImpersonating || !this.currentImpersonatedUser) return;

        try {
            // Find and update the welcome message in navigation
            const welcomeElements = document.querySelectorAll('[class*="welcome"], [id*="welcome"], .nav-welcome');
            const userNameElements = document.querySelectorAll('[class*="username"], [class*="displayName"], .nav-username');
            
            // Also look for any text containing "Welcome" in the navigation
            const navElements = document.querySelectorAll('#global-nav *');
            
            const impersonatedName = this.currentImpersonatedUser.display_name || 
                                   `${this.currentImpersonatedUser.first_name || ''} ${this.currentImpersonatedUser.last_name || ''}`.trim() ||
                                   this.currentImpersonatedUser.email;

            // Update welcome message
            navElements.forEach(element => {
                if (element.textContent && element.textContent.includes('Welcome,')) {
                    element.textContent = `Welcome, ${impersonatedName}`;
                    console.log('🎯 Updated welcome message to show impersonated user');
                }
                // Also check for display names in navigation
                if (element.textContent && (element.textContent.includes('John Admin') || element.textContent.includes('Admin'))) {
                    if (!element.textContent.includes('Welcome,')) {
                        element.textContent = impersonatedName;
                        console.log('🎯 Updated nav display name to show impersonated user');
                    }
                }
            });

            // Hide admin functions based on impersonated user's role
            this.hideAdminFunctionsForRole(this.currentImpersonatedUser.role || 'user');

        } catch (error) {
            console.error('Error updating navigation for impersonation:', error);
        }
    }

    /**
     * Create a DOM mutation observer to watch for navigation removal
     */
    setupNavigationProtection() {
        console.log('🛡️ Setting up navigation protection...');
        
        // First, ensure navigation exists and preserve it
        const nav = document.getElementById('global-nav');
        if (nav) {
            this.preservedNavigation = nav.cloneNode(true);
            console.log('💾 Navigation preserved for protection');
        }
        
        // Create a simple protection that prevents navigation removal
        const self = this;
        
        // Override any potential navigation removal
        const originalRemoveChild = Node.prototype.removeChild;
        Node.prototype.removeChild = function(child) {
            if (child && child.id === 'global-nav') {
                console.log('�️ BLOCKED: Attempt to remove global navigation');
                return child; // Return the child but don't actually remove it
            }
            return originalRemoveChild.call(this, child);
        };
        
        // Override any potential navigation hiding
        const originalSetAttribute = Element.prototype.setAttribute;
        Element.prototype.setAttribute = function(name, value) {
            if (this.id === 'global-nav') {
                if (name === 'style' && (value.includes('display:none') || value.includes('display: none'))) {
                    console.log('�️ BLOCKED: Attempt to hide global navigation via style');
                    return;
                }
                if (name === 'hidden') {
                    console.log('🛡️ BLOCKED: Attempt to hide global navigation via hidden attribute');
                    return;
                }
            }
            return originalSetAttribute.call(this, name, value);
        };
        
        console.log('🛡️ Navigation protection active');
    }

    /**
     * Emergency navigation restoration when removal is detected
     */
    emergencyNavigationRestore() {
        console.log('🚨 EMERGENCY NAVIGATION RESTORE');
        
        // Check if navigation is still missing
        if (document.getElementById('global-nav')) {
            console.log('✅ Navigation already restored');
            return;
        }
        
        // Restore from preserved copy immediately
        if (this.preservedNavigation) {
            try {
                const restoredNav = this.preservedNavigation.cloneNode(true);
                restoredNav.style.cssText = `
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    z-index: 9999 !important;
                    display: block !important;
                    visibility: visible !important;
                    background: #fff !important;
                    color: #2a3f7c !important;
                    box-shadow: 0 2px 8px rgba(42,63,124,0.08) !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    border-bottom: 1px solid rgba(42,63,124,0.1) !important;
                `;
                
                document.body.insertBefore(restoredNav, document.body.firstChild);
                console.log('✅ Emergency navigation restored from preserved copy');
                
                // Update for impersonation if needed
                if (this.isImpersonating && this.currentImpersonatedUser) {
                    setTimeout(() => {
                        this.updateNavigationForImpersonation();
                    }, 50);
                }
                
                return;
            } catch (error) {
                console.error('Emergency restore failed:', error);
            }
        }
        
        // Fallback to manual creation
        this.createNavigationFromGlobalNavScript();
        console.log('🔧 Emergency navigation created manually');
    }

    /**
     * Ensure global navigation is visible and not affected by impersonation
     */
    ensureGlobalNavigationVisible() {
        // Make sure global nav is visible and positioned correctly
        const globalNav = document.getElementById('global-nav');
        if (globalNav) {
            // Ensure global nav is visible and positioned correctly
            globalNav.style.display = '';
            globalNav.style.visibility = 'visible';
            globalNav.style.position = 'fixed';
            globalNav.style.top = '0';
            globalNav.style.left = '0';
            globalNav.style.width = '100%';
            globalNav.style.zIndex = '9999';
            
            // Remove any hidden class or style that might be applied
            globalNav.classList.remove('hidden');
            if (globalNav.hasAttribute('hidden')) {
                globalNav.removeAttribute('hidden');
            }
            
            console.log('✅ Global navigation visibility ensured');
            return true;
        } else {
            console.log('⚠️ Global navigation not found, triggering setup...');
            // Try to trigger navigation setup if available
            if (window.setupNav) {
                window.setupNav();
                return true;
            } else if (window.refreshGlobalNav) {
                window.refreshGlobalNav();
                return true;
            }
            return false;
        }
    }

    /**
     * Force restore global navigation if it got hidden
     */
    forceRestoreGlobalNavigation() {
        console.log('🔧 Force restoring global navigation...');
        
        let globalNav = document.getElementById('global-nav');
        
        // If navigation exists but is hidden, make it visible
        if (globalNav) {
            console.log('🔧 Navigation exists, ensuring visibility...');
            globalNav.style.display = 'block';
            globalNav.style.visibility = 'visible';
            globalNav.style.position = 'fixed';
            globalNav.style.top = '0';
            globalNav.style.left = '0';
            globalNav.style.width = '100%';
            globalNav.style.zIndex = '9999';
            globalNav.classList.remove('hidden');
            if (globalNav.hasAttribute('hidden')) {
                globalNav.removeAttribute('hidden');
            }
            console.log('✅ Existing navigation made visible');
            return true;
        }
        
        // Navigation is completely missing - try to restore from preserved copy first
        console.log('🔧 Navigation missing - trying preserved copy first...');
        if (this.restorePreservedNavigation()) {
            return true;
        }
        
        // If preserved navigation didn't work, try other methods
        console.log('🔧 Preserved navigation failed - attempting recreation...');
        
        // Method 1: Try window.setupNav
        if (window.setupNav) {
            console.log('🔧 Trying window.setupNav...');
            try {
                window.setupNav();
                setTimeout(() => {
                    globalNav = document.getElementById('global-nav');
                    if (globalNav) {
                        console.log('✅ Navigation restored via setupNav');
                        this.ensureGlobalNavigationVisible();
                        return true;
                    }
                }, 200);
            } catch (error) {
                console.error('Error with setupNav:', error);
            }
        }
        
        // Method 2: Try window.refreshGlobalNav
        if (window.refreshGlobalNav) {
            console.log('🔧 Trying window.refreshGlobalNav...');
            try {
                window.refreshGlobalNav();
                setTimeout(() => {
                    globalNav = document.getElementById('global-nav');
                    if (globalNav) {
                        console.log('✅ Navigation restored via refreshGlobalNav');
                        this.ensureGlobalNavigationVisible();
                        return true;
                    }
                }, 200);
            } catch (error) {
                console.error('Error with refreshGlobalNav:', error);
            }
        }
        
        // Method 3: Manually recreate using our own logic
        console.log('🔧 Manual recreation using stored logic...');
        setTimeout(() => {
            globalNav = document.getElementById('global-nav');
            if (!globalNav) {
                this.createNavigationFromGlobalNavScript();
                console.log('✅ Navigation manually recreated');
                return true;
            }
        }, 300);
        
        return false;
    }

    /**
     * Create navigation using the same logic as global-nav-v2.js
     */
    createNavigationFromGlobalNavScript() {
        try {
            const nav = document.createElement('nav');
            nav.id = 'global-nav';
            nav.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                z-index: 9999;
                background: #fff;
                color: #2a3f7c;
                box-shadow: 0 2px 8px rgba(42,63,124,0.08);
                padding: 0;
                margin: 0;
                border-bottom: 1px solid rgba(42,63,124,0.1);
                backdrop-filter: blur(10px);
            `;
            
            // Get user info from localStorage (impersonated or original)
            const displayName = localStorage.getItem('username') || 'User';
            const userRole = localStorage.getItem('userRole') || 'user';
            const isAdmin = userRole && ['admin', 'manager', 'supervisor'].includes(userRole.toLowerCase());
            
            const adminLink = isAdmin ? 
                `<a href="admin.html" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;">Admin</a>` : 
                '';
            
            nav.innerHTML = `
                <div style="display:grid;grid-template-columns:auto 1fr 0.5fr;align-items:center;width:calc(100vw - 20px);margin:0 auto;">
                    <div style="display:flex;align-items:center;justify-content:flex-start;height:60px;padding:0;margin:0;">
                        <img src='https://yggfiuqxfxsoyesqgpyt.supabase.co/storage/v1/object/sign/assetts/Sparky%20AI.gif?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV82NDZjMzIxYy05NDgwLTQ0NDgtYTYxYy0yZTBiYmIzYjA2N2MiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhc3NldHRzL1NwYXJreSBBSS5naWYiLCJpYXQiOjE3NTA4MjY0ODksImV4cCI6NDkwNDQyNjQ4OX0.EvAry9yafzSiWUPneOSv3RgPQzHcKbvpNhel_XcP_Og' alt='Logo' style='height:60px;width:60px;object-fit:cover;display:block;padding:0;margin:0;border-radius:0;'>
                        <span style="font-weight:700;letter-spacing:1px;font-size:1.8em;color:#1976ff;margin-left:0;">Sparky Messaging</span>
                    </div>
                    <div style="display:flex;align-items:center;justify-content:center;height:60px;padding-left:10px;">
                        <nav style="display:flex;gap:22px;">
                          <a href="index.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">Home</a>
                          <a href="ai_editor.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">Sparky AI</a>
                          <a href="sms_editor.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">SMS</a>
                          <a href="rvm_editor.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">RVM</a>
                          <a href="email_editor.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">Email</a>
                          <a href="list.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">List</a>
                          <a href="campaign_builder.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">Campaign</a>
                          <a href="assets.html" style="color:#1976ff;text-decoration:none;font-weight:500;font-size:1.08em;">Profile</a>
                          ${adminLink}
                        </nav>
                    </div>
                    <div style="display:flex;align-items:center;justify-content:flex-end;height:60px;padding:0;margin:0;">
                        <span style="color:#1976ff;font-weight:600;font-size:1.08em;margin-right:18px;">Welcome,${displayName ? ' ' + displayName : ''}</span>
                        <button style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;" onclick="window.location.href='login.html'">Log Out</button>
                    </div>
                </div>
            `;
            
            document.body.insertBefore(nav, document.body.firstChild);
            console.log('✅ Navigation created from global-nav-v2.js logic');
            
        } catch (error) {
            console.error('Error creating navigation from global-nav-v2.js logic:', error);
            this.createFallbackNavigation();
        }
    }

    /**
     * Create a basic fallback navigation if all else fails
     */
    createFallbackNavigation() {
        const nav = document.createElement('nav');
        nav.id = 'global-nav';
        nav.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 9999;
            background: #fff;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        nav.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: bold; color: #1976ff;">Sparky Messaging</span>
                </div>
                <div>
                    <a href="index.html" style="margin-right: 20px; color: #1976ff;">Home</a>
                    <a href="admin.html" style="margin-right: 20px; color: #1976ff;">Admin</a>
                    <button onclick="window.location.href='login.html'" style="background: none; border: none; color: #e53935; cursor: pointer;">Log Out</button>
                </div>
            </div>
        `;
        
        document.body.insertBefore(nav, document.body.firstChild);
        console.log('🔧 Fallback navigation created');
    }

    /**
     * Hide admin functions based on the impersonated user's role
     */
    hideAdminFunctionsForRole(userRole) {
        const role = userRole.toLowerCase();
        
        // Store hidden elements for restoration later
        if (!this.hiddenElements) {
            this.hiddenElements = [];
        }
        
        // Always ensure global navigation is visible before making any changes
        this.ensureGlobalNavigationVisible();
        
        // Hide the impersonation button itself when impersonating
        const impersonationControls = document.querySelectorAll('.user-impersonation-controls, [onclick*="openImpersonationModal"]');
        impersonationControls.forEach(control => {
            // Never hide global navigation or anything inside it
            if (control.id !== 'global-nav' && !control.closest('#global-nav') && control.style.display !== 'none') {
                this.hiddenElements.push({element: control, originalDisplay: control.style.display});
                control.style.display = 'none';
            }
        });

        // Hide admin-specific elements if impersonating a non-admin user
        if (role !== 'admin') {
            // Only hide very specific admin elements, not general navigation
            const specificAdminElements = document.querySelectorAll(
                '.admin-only, ' +
                '[data-admin-only="true"], ' +
                'button[onclick*="admin"], ' +
                '.admin-btn, ' +
                '[data-role="admin"], ' +
                '#admin-controls, ' +
                '.admin-panel'
            );
            
            specificAdminElements.forEach(element => {
                // Triple protection: never hide global nav or anything inside it
                if (element.id !== 'global-nav' && 
                    !element.closest('#global-nav') && 
                    !element.closest('#impersonation-banner') && 
                    element.style.display !== 'none') {
                    this.hiddenElements.push({element: element, originalDisplay: element.style.display});
                    element.style.display = 'none';
                }
            });

            // Hide role management sections for non-admin users (be more specific)
            const roleSections = document.querySelectorAll('#admin-table, #supervisor-table, #manager-table');
            
            if (role === 'user') {
                // Regular users can only see their own info
                roleSections.forEach(section => {
                    if (section && section.style.display !== 'none') {
                        this.hiddenElements.push({element: section, originalDisplay: section.style.display});
                        section.style.display = 'none';
                    }
                });
            } else if (role === 'manager') {
                // Managers can see their users but not admin/supervisor tables
                const adminSection = document.querySelector('#admin-table');
                const supervisorSection = document.querySelector('#supervisor-table');
                
                if (adminSection && adminSection.style.display !== 'none') {
                    this.hiddenElements.push({element: adminSection, originalDisplay: adminSection.style.display});
                    adminSection.style.display = 'none';
                }
                if (supervisorSection && supervisorSection.style.display !== 'none') {
                    this.hiddenElements.push({element: supervisorSection, originalDisplay: supervisorSection.style.display});
                    supervisorSection.style.display = 'none';
                }
            } else if (role === 'supervisor') {
                // Supervisors can see managers and users but not admin table
                const adminSection = document.querySelector('#admin-table');
                if (adminSection && adminSection.style.display !== 'none') {
                    this.hiddenElements.push({element: adminSection, originalDisplay: adminSection.style.display});
                    adminSection.style.display = 'none';
                }
            }
        }

        // Final check: ensure global navigation is still visible after all changes
        setTimeout(() => {
            this.ensureGlobalNavigationVisible();
        }, 50);

        console.log(`🔒 Admin functions hidden for role: ${role}`, this.hiddenElements.length, 'elements hidden');
    }

    /**
     * Restore admin functions when switching back
     */
    restoreAdminFunctions() {
        try {
            console.log('🔓 Restoring admin functions...');
            
            // First, force restore global navigation
            this.forceRestoreGlobalNavigation();
            
            // Restore previously hidden elements
            if (this.hiddenElements && this.hiddenElements.length > 0) {
                this.hiddenElements.forEach(({element, originalDisplay}) => {
                    if (element && element.style) {
                        // Never hide the global navigation
                        if (element.id === 'global-nav' || element.closest('#global-nav')) {
                            element.style.display = '';
                            element.style.visibility = 'visible';
                        } else {
                            element.style.display = originalDisplay || '';
                        }
                    }
                });
                
                console.log('🔓 Admin functions restored:', this.hiddenElements.length, 'elements restored');
                this.hiddenElements = []; // Clear the array
            }

            // Fallback: Also restore any commonly hidden elements that might have been missed
            const commonElements = document.querySelectorAll(
                '.user-impersonation-controls, ' +
                '[onclick*="openImpersonationModal"], ' +
                '.admin-only, ' +
                '[data-admin-only="true"], ' +
                'button[onclick*="admin"], ' +
                '.admin-btn, ' +
                '[data-role="admin"], ' +
                '#admin-controls, ' +
                '.admin-panel, ' +
                '#admin-table, ' +
                '#supervisor-table, ' +
                '#manager-table'
            );
            
            commonElements.forEach(element => {
                if (element && !element.closest('#impersonation-banner')) {
                    element.style.display = '';
                }
            });

            // Ensure global navigation is definitely visible
            setTimeout(() => {
                this.ensureGlobalNavigationVisible();
            }, 100);

            console.log('🔓 Admin functions fully restored');
        } catch (error) {
            console.error('Error restoring admin functions:', error);
            // If there's an error, at least try to restore the navigation
            this.forceRestoreGlobalNavigation();
        }
    }

    /**
     * Switch back to original user
     */
    switchBackToOriginalUser() {
        try {
            console.log('🔙 Switching back to original user...');
            
            if (!this.isImpersonating || !this.originalUserInfo) {
                console.log('❌ Not currently impersonating or no original user info');
                return;
            }

            // Check navigation BEFORE switching back
            const navBefore = document.getElementById('global-nav');
            console.log('🔍 Navigation before switch back:', !!navBefore, navBefore ? 'visible' : 'missing');

            // Restore original user data
            localStorage.setItem('userId', this.originalUserInfo.id);
            localStorage.setItem('userEmail', this.originalUserInfo.email);
            localStorage.setItem('userRole', this.originalUserInfo.role);
            localStorage.setItem('username', this.originalUserInfo.username);

            // Clear impersonation data
            localStorage.removeItem('impersonationData');

            // Clear banner check interval
            if (this.bannerCheckInterval) {
                clearInterval(this.bannerCheckInterval);
                this.bannerCheckInterval = null;
            }

            // Update instance state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;

            // Check navigation AFTER localStorage restoration
            const navAfterStorage = document.getElementById('global-nav');
            console.log('🔍 Navigation after localStorage restoration:', !!navAfterStorage, navAfterStorage ? 'visible' : 'missing');

            // Remove banner
            if (this.impersonationBanner) {
                this.impersonationBanner.classList.add('slide-up');
                setTimeout(() => {
                    if (this.impersonationBanner && this.impersonationBanner.parentNode) {
                        this.impersonationBanner.parentNode.removeChild(this.impersonationBanner);
                        this.impersonationBanner = null;
                    }
                }, 300);
            }

            // Show success message
            this.showSuccessMessage(`Switched back to ${this.originalUserInfo.username}`);

            // FORCE restore navigation first
            console.log('🔧 Force restoring navigation during switch back...');
            this.forceRestoreGlobalNavigation();
            
            // Restore admin functions
            this.restoreAdminFunctions();

            // Wait and check navigation after restoration
            setTimeout(() => {
                const navAfterRestore = document.getElementById('global-nav');
                console.log('🔍 Navigation after restore functions:', !!navAfterRestore, navAfterRestore ? 'visible' : 'missing');
                
                // Refresh the global navigation to show original user info
                this.refreshGlobalNavigation();
                
                // Check navigation after refresh
                setTimeout(() => {
                    const navAfterRefresh = document.getElementById('global-nav');
                    console.log('🔍 Navigation after refresh:', !!navAfterRefresh, navAfterRefresh ? 'visible' : 'missing');
                    
                    // Refresh the data without reloading the page
                    if (window.loadUsersWithHierarchy) {
                        setTimeout(async () => {
                            console.log('🔄 Loading users with hierarchy after switch back...');
                            await window.loadUsersWithHierarchy();
                            
                            // Final navigation check
                            const navFinal = document.getElementById('global-nav');
                            console.log('🔍 Navigation after final data load:', !!navFinal, navFinal ? 'visible' : 'missing');
                            
                            // Force restore if still missing
                            if (!navFinal) {
                                console.log('🚨 Navigation still missing - final force restore...');
                                this.forceRestoreGlobalNavigation();
                            }
                        }, 100);
                    } else {
                        // Force restore navigation if loadUsersWithHierarchy is not available
                        console.log('🔧 loadUsersWithHierarchy not available - forcing final restore...');
                        setTimeout(() => {
                            this.forceRestoreGlobalNavigation();
                        }, 500);
                    }
                }, 100);
            }, 100);

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
            console.log('🧹 Clearing impersonation data...');
            
            // Clear localStorage
            localStorage.removeItem('impersonationData');
            
            // Clear banner check interval
            if (this.bannerCheckInterval) {
                clearInterval(this.bannerCheckInterval);
                this.bannerCheckInterval = null;
            }
            
            // Reset instance state
            this.isImpersonating = false;
            this.currentImpersonatedUser = null;
            this.originalUserInfo = null;
            
            // Remove banner if it exists
            if (this.impersonationBanner && this.impersonationBanner.parentNode) {
                this.impersonationBanner.parentNode.removeChild(this.impersonationBanner);
                this.impersonationBanner = null;
            }
            
            // Force restore global navigation
            this.forceRestoreGlobalNavigation();
            
            // Restore admin functions
            this.restoreAdminFunctions();
            
            // Final check to ensure navigation is visible
            setTimeout(() => {
                this.ensureGlobalNavigationVisible();
            }, 100);
            
            console.log('🧹 Impersonation data cleared and navigation restored');
        } catch (error) {
            console.error('Error clearing impersonation:', error);
            // If there's an error, at least try to restore the navigation
            this.forceRestoreGlobalNavigation();
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
        console.log('- Document Body Ready:', !!document.body);
        console.log('- Global userImpersonation:', !!window.userImpersonation);
        
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

    /**
     * Manual initialization method for troubleshooting
     */
    manualInit() {
        console.log('🔧 Manual initialization triggered...');
        this.initializeAfterDOM();
    }

    /**
     * Debug method to monitor navigation DOM changes
     */
    debugNavigationState() {
        const nav = document.getElementById('global-nav');
        console.log('🔍 NAVIGATION DEBUG:', {
            exists: !!nav,
            display: nav ? nav.style.display : 'N/A',
            visibility: nav ? nav.style.visibility : 'N/A',
            position: nav ? nav.style.position : 'N/A',
            zIndex: nav ? nav.style.zIndex : 'N/A',
            innerHTML: nav ? nav.innerHTML.substring(0, 100) + '...' : 'N/A',
            classList: nav ? Array.from(nav.classList) : 'N/A',
            attributes: nav ? Array.from(nav.attributes).map(attr => `${attr.name}="${attr.value}"`).join(', ') : 'N/A',
            parentNode: nav ? nav.parentNode.tagName : 'N/A'
        });
        
        // Also check if there are any elements that might be hiding it
        const allNavs = document.querySelectorAll('[id*="nav"], [class*="nav"]');
        console.log('🔍 All navigation-related elements:', allNavs.length);
        allNavs.forEach((el, i) => {
            console.log(`Nav element ${i}:`, {
                id: el.id,
                className: el.className,
                tagName: el.tagName,
                display: el.style.display,
                visibility: el.style.visibility
            });
        });
    }

    /**
     * Manual method to force restore navigation - can be called from console
     */
    manualRestoreNavigation() {
        console.log('🔧 MANUAL NAVIGATION RESTORE INITIATED');
        
        // First debug current state
        this.debugNavigationState();
        
        // Try aggressive restoration
        let restored = false;
        
        // Method 0: Try preserved navigation first
        if (this.preservedNavigation) {
            console.log('💾 Trying preserved navigation first...');
            if (this.restorePreservedNavigation()) {
                restored = true;
                console.log('✅ Preserved navigation restored');
            }
        }
        
        // Method 1: Check if it exists but is hidden
        if (!restored) {
            let nav = document.getElementById('global-nav');
            if (nav) {
                console.log('🔧 Navigation exists but may be hidden - making visible...');
                nav.style.display = 'block';
                nav.style.visibility = 'visible';
                nav.style.position = 'fixed';
                nav.style.top = '0';
                nav.style.left = '0';
                nav.style.width = '100%';
                nav.style.zIndex = '9999';
                nav.style.background = '#fff';
                nav.classList.remove('hidden');
                if (nav.hasAttribute('hidden')) {
                    nav.removeAttribute('hidden');
                }
                console.log('✅ Existing navigation restored');
                restored = true;
            }
        }
        
        // Method 2: If it doesn't exist, create it
        if (!restored) {
            console.log('🔧 Navigation missing - creating new one...');
            this.createNavigationFromGlobalNavScript();
            restored = true;
        }
        
        // Method 3: Try original global nav functions
        if (window.setupNav) {
            console.log('🔧 Also trying window.setupNav...');
            try {
                window.setupNav();
            } catch (error) {
                console.error('Error with setupNav:', error);
            }
        }
        
        // Final state check
        setTimeout(() => {
            console.log('🔍 FINAL NAVIGATION STATE:');
            this.debugNavigationState();
            
            const finalNav = document.getElementById('global-nav');
            if (finalNav) {
                console.log('✅ Navigation restoration completed successfully');
                // Ensure proper styling
                finalNav.style.display = 'block';
                finalNav.style.visibility = 'visible';
            } else {
                console.log('❌ Navigation restoration failed');
            }
        }, 500);
        
        return 'Navigation restoration attempted - check console logs';
    }

    /**
     * Restore navigation from preserved copy
     */
    restorePreservedNavigation() {
        console.log('💾 Attempting to restore preserved navigation...');
        
        if (!this.preservedNavigation) {
            console.log('❌ No preserved navigation available');
            return false;
        }
        
        try {
            // Remove any existing navigation
            const existingNav = document.getElementById('global-nav');
            if (existingNav) {
                console.log('🗑️ Removing existing navigation');
                existingNav.remove();
            }
            
            // Clone the preserved navigation and insert it
            const restoredNav = this.preservedNavigation.cloneNode(true);
            
            // Ensure it has the right styling
            restoredNav.style.display = 'block';
            restoredNav.style.visibility = 'visible';
            restoredNav.style.position = 'fixed';
            restoredNav.style.top = '0';
            restoredNav.style.left = '0';
            restoredNav.style.width = '100%';
            restoredNav.style.zIndex = '9999';
            
            // Insert at the beginning of body
            document.body.insertBefore(restoredNav, document.body.firstChild);
            
            console.log('✅ Preserved navigation restored successfully');
            
            // Update the welcome message if we're impersonating
            if (this.isImpersonating && this.currentImpersonatedUser) {
                this.updateNavigationForImpersonation();
            }
            
            return true;
        } catch (error) {
            console.error('Error restoring preserved navigation:', error);
            return false;
        }
    }

    // ...existing code...
}

// Initialize the impersonation system with error handling
try {
    console.log('🎭 Starting User Impersonation System initialization...');
    
    // Clear any stale impersonation data that might cause issues
    const impersonationData = localStorage.getItem('impersonationData');
    if (impersonationData) {
        try {
            const data = JSON.parse(impersonationData);
            console.log('🔍 Found existing impersonation data for:', data.impersonatedUser?.email);
        } catch (error) {
            console.warn('🧹 Clearing invalid impersonation data');
            localStorage.removeItem('impersonationData');
        }
    }
    
    const userImpersonation = new UserImpersonation();

    // Make it globally available
    window.userImpersonation = userImpersonation;
    
    console.log('✅ User Impersonation System ready and globally available');
} catch (error) {
    console.error('❌ Failed to initialize User Impersonation System:', error);
    
    // Clear any problematic impersonation data
    localStorage.removeItem('impersonationData');
    
    // Create a fallback object to prevent "not defined" errors
    window.userImpersonation = {
        openImpersonationModal: function() {
            console.error('User Impersonation System failed to initialize');
            alert('User impersonation is currently unavailable. Please refresh the page.');
        },
        debugSystemState: function() {
            console.error('User Impersonation System failed to initialize:', error);
        }
    };
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserImpersonation;
}
