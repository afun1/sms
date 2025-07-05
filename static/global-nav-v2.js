// This file should only contain JavaScript for the navigation bar.
// All HTML and any reference to global-nav.js have been removed.

// NUCLEAR OPTION: Exit before ANY code runs if on login page
(function() {
    'use strict';
    
    // Multiple detection methods
    const path = window.location.pathname.toLowerCase();
    const href = window.location.href.toLowerCase();
    const filename = path.split('/').pop() || '';
    
    // Check 1: Direct file/path detection
    if (filename === 'login.html' || 
        path.includes('login') || 
        href.includes('login')) {
        console.log('[NUCLEAR EXIT] Login page detected by path/file');
        return; // Exit immediately
    }
    
    // Check 2: Document title (if available)
    if (document.title && document.title.toLowerCase().includes('login')) {
        console.log('[NUCLEAR EXIT] Login page detected by title');
        return;
    }
    
    // Check 3: Look for login elements in DOM
    const loginElements = ['#loginForm', '#loginFormPanel', '.login-container', 'input[type="password"]'];
    for (const selector of loginElements) {
        if (document.querySelector(selector)) {
            console.log('[NUCLEAR EXIT] Login page detected by element:', selector);
            return;
        }
    }
    
    // Check 4: Look for login-specific text content
    if (document.body && document.body.innerHTML.toLowerCase().includes('login')) {
        console.log('[NUCLEAR EXIT] Login page detected by body content');
        return;
    }
    
    console.log('[NUCLEAR EXIT] Passed all login checks, continuing with navigation');
    
    // Only continue if we're definitely NOT on a login page
    loadNavigationScript();
})();

function loadNavigationScript() {

console.log('[DEBUG] global-nav-v2.js script loaded');

// Set up global Supabase client if not already set
if (!window.globalSupabase && window.supabase && window.supabase.createClient) {
    const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';
    const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_P4joo9i6y5PmtDM4bIznNg_Wrv5Cjew';
    window.globalSupabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
    console.log('[DEBUG] Created global Supabase client');
} else if (window.globalSupabase) {
    console.log('[DEBUG] Using existing global Supabase client');
} else {
    console.log('[DEBUG] Supabase library not available yet - will create client in onDOMReady');
}

(function() {
    console.log('[DEBUG] IIFE started');
    window.addEventListener('error', function(e) {
        console.error('[DEBUG] Global error:', e.message, e);
    });
    window.addEventListener('unhandledrejection', function(e) {
        console.error('[DEBUG] Unhandled promise rejection:', e.reason);
    });

    async function getDisplayName() {
        const supabase = window.globalSupabase || window.supabase;
        if (!supabase || !supabase.auth) {
            return { displayName: '', userRole: null, secondaryRole: null };
        }
        
        try {
            // Set a timeout for the auth check
            const sessionPromise = supabase.auth.getSession();
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Auth timeout')), 3000)
            );
            
            const sessionResult = await Promise.race([sessionPromise, timeoutPromise]);
            const session = sessionResult.data.session;
            
            if (!session?.user) {
                return { displayName: '', userRole: null, secondaryRole: null };
            }
            
            const userId = session.user.id;
            const { data, error } = await supabase
                .from('profiles')
                .select('first_name, last_name, email, role, secondary_role')
                .eq('id', userId)
                .maybeSingle();
                
            console.log('[DB DEBUG] Profile query result:', { data, error });
            console.log('[DB DEBUG] Raw data.role:', data?.role, 'data.secondary_role:', data?.secondary_role);
                
            if (error || !data) {
                return { displayName: '', userRole: null, secondaryRole: null };
            }
            
            let displayName = '';
            if (data.first_name || data.last_name) {
                displayName = `${data.first_name || ''} ${data.last_name || ''}`.trim();
            }
            if (!displayName && data.email) {
                displayName = data.email;
            }
            
            console.log('[DB DEBUG] Returning:', {
                displayName,
                userRole: data.role || null,
                secondaryRole: data.secondary_role || null
            });
            
            return {
                displayName,
                userRole: data.role || null,
                secondaryRole: data.secondary_role || null
            };
        } catch (e) {
            console.error('Auth error:', e);
            return { displayName: '', userRole: null, secondaryRole: null };
        }
    }

    function renderNav(displayName, userRole = null, secondaryRole = null) {
        // Check if user has admin privileges
        const isAdmin = userRole && ['admin', 'manager', 'supervisor'].includes(userRole.toLowerCase());
        console.log('[DEBUG] User role check - Role:', userRole, 'Is Admin:', isAdmin);
        
        // Check if we're in impersonation mode
        const impersonationData = localStorage.getItem('impersonationData');
        let isImpersonating = false;
        let originalAdminName = '';
        let impersonatedUserName = '';
        
        if (impersonationData) {
            try {
                const parsed = JSON.parse(impersonationData);
                if (parsed.originalSession && parsed.impersonatedUser) {
                    isImpersonating = true;
                    // Get original admin name
                    const originalProfile = parsed.originalProfile;
                    if (originalProfile) {
                        originalAdminName = originalProfile.display_name || 
                                          originalProfile.displayName ||
                                          `${originalProfile.first_name || ''} ${originalProfile.last_name || ''}`.trim() ||
                                          originalProfile.email?.split('@')[0] || 'Admin';
                    }
                    // Get impersonated user name
                    const impUser = parsed.impersonatedUser;
                    impersonatedUserName = impUser.display_name || 
                                         impUser.displayName ||
                                         `${impUser.first_name || ''} ${impUser.last_name || ''}`.trim() ||
                                         impUser.email?.split('@')[0] || 'User';
                }
            } catch (e) {
                console.error('[DEBUG] Error parsing impersonation data in renderNav:', e);
            }
        }
        
        // Build admin link - always visible regardless of role (hide during impersonation)
        // SIMPLE RULE: Always show "View as [secondary_role]" when logged in as primary role
        // SPECIAL CASE: Primary admin users get "Admin" button to access admin panel
        let roleText = '';
        let roleDestination = '';
        
        // Check if user has a secondary role AND it's different from primary role
        if (secondaryRole && secondaryRole.toLowerCase() !== userRole.toLowerCase()) {
            // Get current page for destination
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            
            // Check if we're currently viewing as any specific role
            const urlParams = new URLSearchParams(window.location.search);
            const currentView = urlParams.get('view');
            
            console.log('[ROLE DEBUG] userRole:', userRole, 'secondaryRole:', secondaryRole, 'currentView:', currentView);
            console.log('[ROLE DEBUG] Comparison:', currentView?.toLowerCase(), '===', secondaryRole?.toLowerCase(), '=', currentView?.toLowerCase() === secondaryRole?.toLowerCase());
            
            // If we're viewing as the secondary role, show option to go back to primary
            if (currentView && currentView.toLowerCase() === secondaryRole.toLowerCase()) {
                // Currently viewing as secondary role, show option to go back to primary role
                roleText = userRole.charAt(0).toUpperCase() + userRole.slice(1);
                roleDestination = currentPage; // Remove view parameter to go back to primary
                console.log('[ROLE DEBUG] Showing primary role button:', roleText);
            } else {
                // Currently viewing as primary role (no view param or different view), show option to switch to secondary role
                roleText = secondaryRole.charAt(0).toUpperCase() + secondaryRole.slice(1);
                roleDestination = `${currentPage}?view=${secondaryRole.toLowerCase()}`;
                console.log('[ROLE DEBUG] Showing secondary role button:', roleText);
            }
        } else if (userRole && userRole.toLowerCase() === 'admin' && !secondaryRole) {
            // Special case: Primary admin with no secondary role gets "Admin" button to admin panel
            roleText = 'Admin';
            roleDestination = 'admin.html';
        }
        
        console.log('[LINK DEBUG] isImpersonating:', isImpersonating, 'roleText:', roleText, 'roleDestination:', roleDestination);
        
        const adminLink = (!isImpersonating && roleText) ? 
            `<a href="${roleDestination}" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;line-height:1.2;"><span style="font-size:10px;">View as</span><br>${roleText}</a>` : 
            '';
            
        console.log('[LINK DEBUG] adminLink created:', adminLink.length > 0 ? 'YES' : 'NO', 'length:', adminLink.length);
        
        // Build impersonation banner
        const impersonationBanner = isImpersonating ? `
            <div style="background:#ff5252;color:white;padding:8px 0;text-align:center;font-weight:600;font-size:14px;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <span>🔄 You are viewing as ${impersonatedUserName} (Admin: ${originalAdminName})</span>
                <button id="switchBackBtn" style="background:#fff;color:#ff5252;border:none;padding:4px 12px;margin-left:15px;border-radius:4px;font-weight:600;cursor:pointer;font-size:13px;">
                    Switch Back to Admin
                </button>
            </div>
        ` : '';
        
        return `
        ${impersonationBanner}
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
                <button id="logoutBtn" style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;line-height:1.2;">Log<br>Out</button>
            </div>
        </div>
        `;
    }

    async function setupNav() {
        let nav = document.getElementById('global-nav');
        if (!nav) {
            nav = document.createElement('nav');
            nav.id = 'global-nav';
            document.body.prepend(nav);
        }
        nav.style.position = 'fixed';
        nav.style.top = '0';
        nav.style.left = '0';
        nav.style.width = '100%';
        nav.style.zIndex = '9999';
        nav.style.background = '#fff';
        nav.style.color = '#2a3f7c';
        nav.style.boxShadow = '0 2px 8px rgba(42,63,124,0.08)';
        nav.style.padding = '0';
        nav.style.margin = '0';
        nav.style.borderBottom = '1px solid rgba(42,63,124,0.1)';
        
        document.body.style.paddingTop = '80px';
        
        let displayName = '';
        let userRole = null;
        let secondaryRole = null;
        
        try {
            const result = await getDisplayName();
            displayName = result.displayName;
            userRole = result.userRole;
            secondaryRole = result.secondaryRole;
        } catch (e) {
            console.error('Setup nav error:', e);
        }
        
        nav.innerHTML = renderNav(displayName, userRole, secondaryRole);
        
        // Handle logout button with immediate redirect
        const logoutBtn = nav.querySelector('#logoutBtn');
        if (logoutBtn) {
            // Remove all existing event listeners
            const newLogoutBtn = logoutBtn.cloneNode(true);
            logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);
            
            newLogoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopImmediatePropagation();
                
                // Immediately disable all page functionality
                window.onbeforeunload = null;
                
                // Clear storage immediately and aggressively
                try {
                    localStorage.clear();
                    sessionStorage.clear();
                    
                    // Clear specific auth items
                    localStorage.removeItem('supabase.auth.token');
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('userRole');
                    localStorage.removeItem('username');
                    localStorage.removeItem('userEmail');
                    localStorage.removeItem('impersonationData');
                } catch (ex) {
                    // Ignore storage errors
                }
                
                // Multiple immediate redirect attempts
                setTimeout(() => {
                    window.location.replace('login.html');
                }, 0);
                window.location.href = 'login.html';
                
                return false;
            });
        }
    }

    // Function to refresh navigation (can be called from other pages)
    window.refreshGlobalNav = async function() {
        console.log('[DEBUG] Refreshing global navigation...');
        await setupNav();
    };

    // Helper: Wait for DOMContentLoaded
    function onDOMReady(cb) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', cb);
        } else {
            cb();
        }
    }

    // Ensure Supabase UMD is present
    onDOMReady(function() {
        // TRIPLE CHECK: Don't load navigation on login or authentication pages
        const currentPath = window.location.pathname.toLowerCase();
        const currentFile = currentPath.split('/').pop() || '';
        const currentURL = window.location.href.toLowerCase();
        const pageTitle = document.title ? document.title.toLowerCase() : '';
        
        const isAuthPage = currentFile === 'login.html' || 
                           currentFile === 'signup.html' || 
                           currentFile === 'reset.html' ||
                           currentFile === 'auth.html' ||
                           currentPath.includes('login') ||
                           currentPath.includes('signup') ||
                           currentPath.includes('auth') ||
                           currentURL.includes('login') ||
                           pageTitle.includes('login') ||
                           pageTitle.includes('sign in') ||
                           pageTitle.includes('authentication');
        
        if (isAuthPage) {
            console.log('[DEBUG] TRIPLE CHECK: Skipping navigation on authentication page:', currentPath);
            console.log('[DEBUG] Detection details - file:', currentFile, 'path:', currentPath, 'title:', pageTitle);
            return;
        }
        
        if (window.supabase && typeof window.supabase.createClient === 'function') {
            // Use the global client that was already created
            if (!window.globalSupabase) {
                const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
                const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';
                const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_P4joo9i6y5PmtDM4bIznNg_Wrv5Cjew';
                window.globalSupabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
                console.log('[DEBUG] Created global Supabase client in onDOMReady');
            } else {
                console.log('[DEBUG] Using existing global Supabase client');
            }
            setupNav();
        } else {
            // If UMD is not present, show static nav
            let nav = document.getElementById('global-nav');
            if (!nav) {
                nav = document.createElement('nav');
                nav.id = 'global-nav';
                document.body.prepend(nav);
            }
            nav.style.position = 'fixed';
            nav.style.top = '0';
            nav.style.left = '0';
            nav.style.width = '100%';
            nav.style.zIndex = '9999';
            nav.style.background = '#fff';
            nav.style.color = '#2a3f7c';
            nav.style.boxShadow = '0 2px 8px rgba(42,63,124,0.08)';
            nav.style.padding = '0';
            nav.style.margin = '0';
            nav.style.borderBottom = '1px solid rgba(42,63,124,0.1)';
            nav.style.backdropFilter = 'blur(10px)';
            nav.style.webkitBackdropFilter = 'blur(10px)';
            
            // Ensure body has top padding to account for fixed nav
            if (!document.body.style.paddingTop) {
                document.body.style.paddingTop = '80px';
            }
            nav.innerHTML = renderNav('', null, null);
            console.error('[ERROR] Supabase UMD not found. Header will be static.');
        }
    });

})();

// Global helper function for pages to get the current authenticated user (with impersonation support)
window.getAuthenticatedUserGlobal = async function() {
    try {
        // First check if we're in impersonation mode
        const impersonationData = localStorage.getItem('impersonationData');
        if (impersonationData) {
            try {
                const data = JSON.parse(impersonationData);
                if (data.impersonatedUser && data.timestamp) {
                    // Check if impersonation data is recent (not stale)
                    const now = Date.now();
                    const impersonationAge = now - data.timestamp;
                    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
                    
                    if (impersonationAge > maxAge) {
                        console.warn('🎭 Global: Impersonation data is stale, clearing it');
                        localStorage.removeItem('impersonationData');
                    } else {
                        console.log('🎭 Global: Using impersonated user:', data.impersonatedUser.email);
                        // Return impersonated user in the same format as supabase user
                        const impersonatedUser = {
                            id: data.impersonatedUser.id,
                            email: data.impersonatedUser.email,
                            user_metadata: data.impersonatedUser.user_metadata || {},
                            app_metadata: data.impersonatedUser.app_metadata || {}
                        };
                        return impersonatedUser;
                    }
                }
            } catch (parseError) {
                console.error('❌ Global: Error parsing impersonation data:', parseError);
                localStorage.removeItem('impersonationData');
            }
        }
        
        // No valid impersonation, use normal auth
        if (!window.globalSupabase) {
            console.error('❌ Global: No Supabase client available');
            return null;
        }
        
        const { data: { user }, error } = await window.globalSupabase.auth.getUser();
        if (error || !user) {
            console.log('🔑 Global: User not authenticated');
            return null;
        }
        
        console.log('🔑 Global: Using normal authenticated user:', user.email);
        return user;
    } catch (error) {
        console.error('❌ Global: Error getting authenticated user:', error);
        return null;
    }
};

})(); // End of IIFE that wraps the entire navigation script

} // End of loadNavigationScript function