// Enhanced Account Switcher with Password Verification
async function switchToAccountWithPassword(targetUserId, adminPassword) {
    // Verify admin password first
    const { error: adminVerifyError } = await supabase.auth.signInWithPassword({
        email: adminUser.email,
        password: adminPassword
    });
    
    if (adminVerifyError) {
        throw new Error('Admin password verification failed');
    }
    
    // Then proceed with account switch
    // ... rest of switching logic
}
