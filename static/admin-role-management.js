// Admin Role Management JavaScript
// Separated from main admin.html to reduce memory usage

// Global variables for role management
let currentEditingUserId = null;
let allUsers = []; // Store all users for role modal

// Individual Role Management Functions (for single user editing)
async function openRoleModal(userId) {
    console.log('🎭 Opening role modal for user:', userId);
    currentEditingUserId = userId;
    
    try {
        // Find the user in our cached data
        const user = allUsers.find(u => u.id === userId);
        if (!user) {
            alert('User not found. Please refresh the page.');
            return;
        }
        
        // Populate the modal
        document.getElementById('role-user-name').textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Unknown User';
        document.getElementById('role-user-email').textContent = user.email || 'No email';
        document.getElementById('primary-role').value = user.role || '';
        document.getElementById('secondary-role').value = user.secondary_role || '';
        
        // Update role combination info
        updateRoleCombinationInfo();
        
        // Show the modal
        const modal = document.getElementById('role-modal');
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('💥 Error opening role modal:', error);
        alert('Error opening role modal: ' + error.message);
    }
}

// Update role combination information display
function updateRoleCombinationInfo() {
    const primaryRole = document.getElementById('primary-role').value;
    const secondaryRole = document.getElementById('secondary-role').value;
    
    const infoDiv = document.getElementById('role-combination-info');
    const warningDiv = document.getElementById('role-combination-warning');
    const infoText = document.getElementById('role-combination-text');
    const warningText = document.getElementById('role-combination-warning-text');
    
    // Hide both initially
    infoDiv.style.display = 'none';
    warningDiv.style.display = 'none';
    
    if (!secondaryRole) {
        // No secondary role selected
        return;
    }
    
    if (primaryRole === secondaryRole) {
        // Invalid: same role
        warningDiv.style.display = 'block';
        warningText.textContent = 'Primary and secondary roles must be different.';
        return;
    }
    
    // Valid combination - show helpful info
    infoDiv.style.display = 'block';
    
    const combinations = {
        'user+admin': 'Regular user with administrative privileges - can manage other users while maintaining user role',
        'manager+admin': 'Manager with administrative privileges - can manage teams and system administration',
        'supervisor+admin': 'Supervisor with administrative privileges - can oversee operations and manage system',
        'manager+supervisor': 'Manager with supervisory privileges - can manage teams and supervise other managers',
        'user+manager': 'Regular user with management privileges - can lead small teams',
        'user+supervisor': 'Regular user with supervisory privileges - can oversee specific areas'
    };
    
    const comboKey = `${primaryRole}+${secondaryRole}`;
    infoText.textContent = combinations[comboKey] || `User will have both ${primaryRole} and ${secondaryRole} privileges.`;
}

// Handle role form submission
async function handleRoleFormSubmit(event) {
    event.preventDefault();
    
    const primaryRole = document.getElementById('primary-role').value;
    const secondaryRole = document.getElementById('secondary-role').value || null;
    
    if (primaryRole === secondaryRole) {
        alert('Primary and secondary roles must be different.');
        return;
    }
    
    try {
        console.log('💾 Updating roles for user:', currentEditingUserId, { primaryRole, secondaryRole });
        
        // Get Supabase client from main page
        const supabase = window.supabase;
        if (!supabase) {
            throw new Error('Supabase client not available');
        }
        
        // Update the user in Supabase
        const { data, error } = await window.supabase
            .from('profiles')
            .update({ 
                role: primaryRole,
                secondary_role: secondaryRole 
            })
            .eq('id', currentEditingUserId);
        
        if (error) {
            throw error;
        }
        
        console.log('✅ Roles updated successfully');
        
        // Close the modal
        document.getElementById('role-modal').style.display = 'none';
        
        // Refresh the user tables if function exists
        if (window.loadUsersWithHierarchy) {
            await window.loadUsersWithHierarchy();
        }
        
        alert('Roles updated successfully!');
        
    } catch (error) {
        console.error('💥 Error updating roles:', error);
        alert('Error updating roles: ' + error.message);
    }
}

// Add event listeners for role modal
function setupRoleModalListeners() {
    // Role form submission
    const roleForm = document.getElementById('role-form');
    if (roleForm) {
        roleForm.addEventListener('submit', handleRoleFormSubmit);
    }
    
    // Cancel button
    const cancelButton = document.getElementById('cancel-role-modal');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            document.getElementById('role-modal').style.display = 'none';
        });
    }
    
    // Role selection change listeners
    const primaryRoleSelect = document.getElementById('primary-role');
    const secondaryRoleSelect = document.getElementById('secondary-role');
    
    if (primaryRoleSelect) {
        primaryRoleSelect.addEventListener('change', updateRoleCombinationInfo);
    }
    
    if (secondaryRoleSelect) {
        secondaryRoleSelect.addEventListener('change', updateRoleCombinationInfo);
    }
    
    // Click outside modal to close
    const modal = document.getElementById('role-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }
    
    console.log('✅ Role modal listeners setup complete');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupRoleModalListeners);
} else {
    setupRoleModalListeners();
}

// Make functions available globally
window.openRoleModal = openRoleModal;
window.updateRoleCombinationInfo = updateRoleCombinationInfo;
window.handleRoleFormSubmit = handleRoleFormSubmit;
window.setupRoleModalListeners = setupRoleModalListeners;

// Function to update the allUsers cache from main page
window.updateUserCache = function(users) {
    allUsers = users || [];
    console.log('📋 User cache updated:', allUsers.length, 'users');
};
