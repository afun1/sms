// Test script to verify impersonation fix
// Run this in the browser console on admin.html

console.log('🧪 Testing impersonation state fix...');

// Function to check current state
async function checkState() {
    console.log('\n=== Current State Check ===');
    
    // Check impersonation data
    const impersonationData = localStorage.getItem('impersonationData');
    console.log('💾 Impersonation Data:', impersonationData ? JSON.parse(impersonationData) : 'None');
    
    // Check legacy localStorage values
    console.log('🗂️ Legacy localStorage:');
    console.log('  - userId:', localStorage.getItem('userId'));
    console.log('  - userRole:', localStorage.getItem('userRole'));
    console.log('  - userEmail:', localStorage.getItem('userEmail'));
    
    // Check window.userImpersonation state
    if (window.userImpersonation) {
        console.log('🎭 Impersonation System State:');
        console.log('  - isImpersonating:', window.userImpersonation.isImpersonating);
        console.log('  - currentImpersonatedUser:', window.userImpersonation.currentImpersonatedUser);
    }
    
    // Test getCurrentUserRoleFromDB
    if (typeof getCurrentUserRoleFromDB === 'function') {
        try {
            const role = await getCurrentUserRoleFromDB();
            console.log('🔍 getCurrentUserRoleFromDB() returned:', role);
        } catch (e) {
            console.error('❌ Error calling getCurrentUserRoleFromDB:', e);
        }
    }
    
    // Check how many users are visible in the table
    const userRows = document.querySelectorAll('table tbody tr');
    console.log('👥 Users visible in table:', userRows.length);
    
    console.log('=== End State Check ===\n');
}

// Function to test full impersonation cycle
async function testImpersonationCycle() {
    console.log('\n🧪 Starting full impersonation test cycle...');
    
    // Check initial state
    await checkState();
    
    // Find a user to impersonate (look for impersonation buttons)
    const impersonateButtons = document.querySelectorAll('button[onclick*="impersonate"]');
    if (impersonateButtons.length === 0) {
        console.error('❌ No impersonation buttons found! Cannot test impersonation.');
        return;
    }
    
    console.log(`🎯 Found ${impersonateButtons.length} impersonation buttons`);
    
    // Extract user ID from first button onclick
    const firstButton = impersonateButtons[0];
    const onclickAttr = firstButton.getAttribute('onclick');
    const userIdMatch = onclickAttr.match(/impersonateUser\s*\(\s*['"`]([^'"`]+)['"`]/);
    
    if (!userIdMatch) {
        console.error('❌ Could not extract user ID from button onclick');
        return;
    }
    
    const userIdToImpersonate = userIdMatch[1];
    console.log('🎯 Will impersonate user:', userIdToImpersonate);
    
    // Start impersonation
    console.log('▶️ Starting impersonation...');
    if (typeof impersonateUser === 'function') {
        await impersonateUser(userIdToImpersonate);
        
        // Wait a moment for state to update
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check state during impersonation
        console.log('📊 State during impersonation:');
        await checkState();
        
        // Exit impersonation
        console.log('🚪 Exiting impersonation...');
        if (window.userImpersonation && typeof window.userImpersonation.exitImpersonation === 'function') {
            await window.userImpersonation.exitImpersonation();
            
            // Wait a moment for state to update
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Check state after exiting
            console.log('📊 State after exiting impersonation:');
            await checkState();
            
            // Reload users to test filtering
            if (typeof loadUsers === 'function') {
                console.log('🔄 Reloading users...');
                await loadUsers();
                await checkState();
            }
            
            console.log('✅ Full impersonation cycle test completed!');
        } else {
            console.error('❌ Cannot exit impersonation - function not available');
        }
    } else {
        console.error('❌ impersonateUser function not available');
    }
}

// Run initial state check
checkState();

// Expose functions for manual testing
window.testImpersonationCycle = testImpersonationCycle;
window.checkState = checkState;

console.log('🧪 Test functions available:');
console.log('  - checkState() - Check current impersonation state');
console.log('  - testImpersonationCycle() - Run full test cycle');
console.log('');
console.log('▶️ Run testImpersonationCycle() to test the full impersonation cycle');
