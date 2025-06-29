// Impersonation Test Script
// Run this in the browser console on any page to test impersonation functionality

async function testImpersonationOnCurrentPage() {
    console.log('🧪 IMPERSONATION TEST STARTED');
    console.log('=====================================');
    
    // Check if global navigation is loaded
    const hasGlobalNav = typeof window.getAuthenticatedUserGlobal === 'function';
    console.log('✅ Global navigation loaded:', hasGlobalNav);
    
    // Check impersonation data
    const impersonationData = localStorage.getItem('impersonationData');
    const hasImpersonation = !!impersonationData;
    console.log('🎭 Impersonation active:', hasImpersonation);
    
    if (hasImpersonation) {
        try {
            const data = JSON.parse(impersonationData);
            console.log('👤 Impersonated user:', data.impersonatedUser?.email || 'Unknown');
            console.log('🆔 Impersonated user ID:', data.impersonatedUser?.id || 'Unknown');
        } catch (e) {
            console.error('❌ Invalid impersonation data:', e);
        }
    }
    
    // Test global authentication helper
    if (hasGlobalNav) {
        try {
            const user = await window.getAuthenticatedUserGlobal();
            if (user) {
                console.log('🔑 Current user (via global helper):', user.email);
                console.log('🆔 Current user ID:', user.id);
                
                if (hasImpersonation) {
                    const impData = JSON.parse(impersonationData);
                    const isCorrectUser = user.id === impData.impersonatedUser?.id;
                    console.log('✅ Correct impersonated user returned:', isCorrectUser);
                } else {
                    console.log('ℹ️ Normal authentication (no impersonation)');
                }
            } else {
                console.log('❌ No user returned by global helper');
            }
        } catch (error) {
            console.error('❌ Error testing global helper:', error);
        }
    }
    
    // Check page-specific elements
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    console.log('📄 Current page:', currentPage);
    
    // Check for impersonation banner
    const banner = document.querySelector('.impersonation-banner');
    const hasBanner = !!banner;
    console.log('🏷️ Impersonation banner visible:', hasBanner);
    
    if (hasBanner && hasImpersonation) {
        console.log('✅ Banner correctly shown during impersonation');
    } else if (!hasBanner && !hasImpersonation) {
        console.log('✅ No banner shown when not impersonating');
    } else {
        console.log('⚠️ Banner state inconsistent with impersonation state');
    }
    
    console.log('=====================================');
    console.log('🧪 IMPERSONATION TEST COMPLETED');
}

// Auto-run the test
testImpersonationOnCurrentPage();
