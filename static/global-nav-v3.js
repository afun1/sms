// Simple, clean navigation with role switching
// This version focuses only on the core functionality

console.log('[DEBUG] global-nav-v3.js script loaded');

// Set up global Supabase client
if (!window.globalSupabase && window.supabase && window.supabase.createClient) {
    const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';
    window.globalSupabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    console.log('[DEBUG] Created global Supabase client');
} else if (!window.supabase) {
    console.warn('[DEBUG] Supabase library not available');
}

(function() {
    
    async function getUserData() {
        console.log('[DEBUG] Getting user data...');
        
        const supabase = window.globalSupabase || window.supabase;
        if (!supabase || !supabase.auth) {
            console.warn('[DEBUG] Supabase not available');
            return { displayName: '', userRole: null, secondaryRole: null };
        }
        
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session?.user) {
                console.warn('[DEBUG] No user session');
                return { displayName: '', userRole: null, secondaryRole: null };
            }
            
            const { data: profile } = await supabase
                .from('profiles')
                .select('first_name, last_name, email, role, secondary_role')
                .eq('id', session.user.id)
                .single();
            
            if (!profile) {
                console.warn('[DEBUG] No profile found');
                return { displayName: '', userRole: null, secondaryRole: null };
            }
            
            const displayName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || profile.email;
            
            console.log('[DEBUG] User data:', {
                displayName,
                userRole: profile.role,
                secondaryRole: profile.secondary_role
            });
            
            return {
                displayName,
                userRole: profile.role,
                secondaryRole: profile.secondary_role
            };
            
        } catch (error) {
            console.error('[DEBUG] Error getting user data:', error);
            return { displayName: '', userRole: null, secondaryRole: null };
        }
    }
    
    function createViewAsButton(userRole, secondaryRole) {
        if (!userRole || !['admin', 'manager', 'supervisor'].includes(userRole.toLowerCase())) {
            return ''; // No admin privileges
        }
        
        if (!secondaryRole) {
            return ''; // No secondary role to switch to
        }
        
        // Check current view parameter
        const urlParams = new URLSearchParams(window.location.search);
        const currentView = urlParams.get('view');
        
        // Get current page (handle root path)
        let currentPage = window.location.pathname;
        if (currentPage === '/') {
            currentPage = '/index.html';
        }
        
        let buttonText = '';
        let buttonLink = '';
        
        if (currentView === secondaryRole.toLowerCase()) {
            // Currently viewing as secondary role, show primary role
            buttonText = userRole.charAt(0).toUpperCase() + userRole.slice(1);
            buttonLink = currentPage; // Remove view parameter
        } else {
            // Currently viewing as primary role, show secondary role
            buttonText = secondaryRole.charAt(0).toUpperCase() + secondaryRole.slice(1);
            buttonLink = `${currentPage}?view=${secondaryRole.toLowerCase()}`;
        }
        
        console.log('[DEBUG] View as button:', { buttonText, buttonLink, currentView });
        
        return `<a href="${buttonLink}" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;line-height:1.2;"><span style="font-size:10px;">View as</span><br>${buttonText}</a>`;
    }
    
    function renderNavigation(displayName, userRole, secondaryRole) {
        const viewAsButton = createViewAsButton(userRole, secondaryRole);
        
        return `
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
                  ${viewAsButton}
                </nav>
            </div>
            <div style="display:flex;align-items:center;justify-content:flex-end;height:60px;padding:0;margin:0;">
                <span style="color:#1976ff;font-weight:600;font-size:1.08em;margin-right:18px;">Welcome, ${displayName}</span>
                <button id="logoutBtn" style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;line-height:1.2;">Log<br>Out</button>
            </div>
        </div>
        `;
    }
    
    async function setupNavigation() {
        console.log('[DEBUG] Setting up navigation...');
        
        try {
            // Create navigation container
            let nav = document.getElementById('global-nav');
            if (!nav) {
                nav = document.createElement('nav');
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
                `;
                document.body.prepend(nav);
            }
            
            // Add body padding for fixed nav
            document.body.style.paddingTop = '80px';
            
            // Show loading state
            nav.innerHTML = renderNavigation('Loading...', null, null);
            
            try {
                // Get user data and render navigation
                const userData = await getUserData();
                nav.innerHTML = renderNavigation(userData.displayName, userData.userRole, userData.secondaryRole);
                console.log('[DEBUG] Navigation rendered with user data:', userData);
            } catch (error) {
                console.error('[DEBUG] Error getting user data, showing basic nav:', error);
                // Show basic navigation even if user data fails
                nav.innerHTML = renderNavigation('Guest', null, null);
            }
            
            // Handle logout
            const logoutBtn = nav.querySelector('#logoutBtn');
            if (logoutBtn) {
                logoutBtn.onclick = async function() {
                    console.log('[DEBUG] Logout clicked');
                    
                    // Show loading state
                    const originalText = logoutBtn.innerHTML;
                    logoutBtn.innerHTML = 'Logging out...';
                    logoutBtn.disabled = true;
                    
                    try {
                        const supabase = window.globalSupabase || window.supabase;
                        if (supabase?.auth) {
                            console.log('[DEBUG] Signing out from Supabase');
                            await supabase.auth.signOut();
                        }
                        
                        // Clear any local storage
                        localStorage.clear();
                        sessionStorage.clear();
                        
                        console.log('[DEBUG] Redirecting to login');
                        window.location.href = 'login.html';
                        
                    } catch (error) {
                        console.error('[DEBUG] Logout error:', error);
                        
                        // Reset button state on error
                        logoutBtn.innerHTML = originalText;
                        logoutBtn.disabled = false;
                        
                        // Force redirect anyway
                        window.location.href = 'login.html';
                    }
                };
            }
            
            console.log('[DEBUG] Navigation setup complete');
        } catch (error) {
            console.error('[DEBUG] Failed to setup navigation:', error);
            // Try to add minimal navigation at least
            if (document.body) {
                document.body.style.paddingTop = '80px';
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
                    padding: 20px;
                    margin: 0;
                    border-bottom: 1px solid rgba(42,63,124,0.1);
                `;
                nav.innerHTML = '<div>Navigation Error - Please refresh the page</div>';
                document.body.prepend(nav);
            }
        }
    }
    
    // Initialize when DOM is ready
    console.log('[DEBUG] Initializing navigation script...');
    if (document.readyState === 'loading') {
        console.log('[DEBUG] DOM still loading, waiting for DOMContentLoaded...');
        document.addEventListener('DOMContentLoaded', setupNavigation);
    } else {
        console.log('[DEBUG] DOM already loaded, setting up navigation immediately...');
        setupNavigation();
    }
    
})();
