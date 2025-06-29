// This file should only contain JavaScript for the navigation bar.
// All HTML and any reference to global-nav.js have been removed.

console.log('[DEBUG] global-nav-v2.js script loaded');

// --- DIAGNOSTIC BLOCK ---
console.log('[DIAG] typeof window.supabase:', typeof window.supabase);
if (window.supabase) {
    console.log('[DIAG] window.supabase.createClient:', typeof window.supabase.createClient);
}
console.log('[DIAG] All script tags on page:');
document.querySelectorAll('script').forEach(s => console.log(s.src));
// --- END DIAGNOSTIC BLOCK ---

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
        console.log('[DEBUG] getDisplayName called');
        
        // First check if we're in impersonation mode
        const impersonationData = localStorage.getItem('impersonationData');
        if (impersonationData) {
            try {
                const parsed = JSON.parse(impersonationData);
                const impersonatedUser = parsed.impersonatedUser;
                if (impersonatedUser) {
                    console.log('[DEBUG] Using impersonated user data:', impersonatedUser);
                    const displayName = impersonatedUser.display_name || 
                                       impersonatedUser.displayName ||
                                       `${impersonatedUser.first_name || ''} ${impersonatedUser.last_name || ''}`.trim() ||
                                       impersonatedUser.email?.split('@')[0] || '';
                    const userRole = impersonatedUser.role || 'user';
                    return { displayName, userRole };
                }
            } catch (e) {
                console.error('[DEBUG] Error parsing impersonation data:', e);
            }
        }
        
        const supabase = window.globalSupabase || window.supabase;
        if (!supabase || !supabase.auth) {
            console.warn('[DEBUG] supabase or supabase.auth missing:', supabase, supabase && supabase.auth);
            return { displayName: '', userRole: null };
        }
        try {
            const sessionResult = await supabase.auth.getSession();
            const session = sessionResult.data.session;
            console.log('[DEBUG] Supabase session:', session);
            if (!session || !session.user) {
                console.warn('[DEBUG] No Supabase session or user found');
                return { displayName: '', userRole: null };
            }
            const userId = session.user.id;
            const { data, error } = await supabase
                .from('profiles')
                .select('first_name, last_name, email, role')
                .eq('id', userId)
                .maybeSingle();
            console.log('[DEBUG] Supabase profiles query:', { userId, data, error });
            if (error) {
                console.error('[DEBUG] Error fetching profile:', error);
                return { displayName: '', userRole: null };
            }
            if (!data) {
                console.warn('[DEBUG] No profile row found for user:', userId);
                return { displayName: '', userRole: null };
            }
            
            let displayName = '';
            // Try first_name + last_name combination
            if (data.first_name || data.last_name) {
                displayName = `${data.first_name || ''} ${data.last_name || ''}`.trim();
            }
            // Fallback to email if no names available
            if (!displayName && data.email) {
                displayName = data.email;
            }
            
            const userRole = data.role || null;
            console.log('[DEBUG] User role:', userRole);
            
            return { displayName, userRole };
        } catch (e) {
            console.error('[DEBUG] Exception in getDisplayName:', e);
            return { displayName: '', userRole: null };
        }
    }

    function renderNav(displayName, userRole = null) {
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
        
        // Build admin link if user has privileges (hide during impersonation)
        const adminLink = (isAdmin && !isImpersonating) ? 
            `<a href="admin.html" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;">Admin</a>` : 
            '';
        
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
                <button id="logoutBtn" style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;">Log Out</button>
            </div>
        </div>
        `;
    }

    async function setupNav() {
        console.log('[DEBUG] setupNav called');
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
        
        // Calculate the required padding based on whether impersonation banner is present
        const impersonationData = localStorage.getItem('impersonationData');
        const hasImpersonationBanner = impersonationData && (() => {
            try {
                const parsed = JSON.parse(impersonationData);
                return !!(parsed.originalSession && parsed.impersonatedUser);
            } catch (e) {
                return false;
            }
        })();
        
        // Adjust body padding for fixed nav (60px nav + 40px banner if present)
        const requiredPadding = hasImpersonationBanner ? '100px' : '80px';
        document.body.style.paddingTop = requiredPadding;
        let displayName = '';
        let userRole = null;
        try {
            const supabase = window.globalSupabase || window.supabase;
            console.log('[DEBUG] Using supabase client:', !!supabase);
            console.log('[DEBUG] supabase.auth available:', !!(supabase && supabase.auth));
            if (supabase && supabase.auth) {
                const result = await getDisplayName();
                displayName = result.displayName;
                userRole = result.userRole;
                console.log('[DEBUG] getDisplayName returned:', { displayName, userRole });
            }
        } catch (e) {
            console.error('[DEBUG] Error in setupNav getDisplayName:', e);
        }
        nav.innerHTML = renderNav(displayName, userRole);
        
        // Handle logout button
        var logoutBtn = nav.querySelector('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = async function() {
                try {
                    const supabase = window.globalSupabase || window.supabase;
                    if (supabase && supabase.auth) {
                        await supabase.auth.signOut();
                        console.log('[DEBUG] User signed out');
                    } else {
                        console.warn('[DEBUG] Supabase not available for logout');
                    }
                } catch (e) {
                    console.error('[DEBUG] Error during logout:', e);
                }
                window.location.href = 'login.html';
            };
        } else {
            console.warn('[DEBUG] Logout button not found in nav');
        }
        
        // Handle switch back button (for impersonation)
        var switchBackBtn = nav.querySelector('#switchBackBtn');
        if (switchBackBtn) {
            switchBackBtn.onclick = async function() {
                console.log('[DEBUG] Switch back button clicked');
                
                try {
                    // Check if we have the user impersonation system available
                    if (window.userImpersonation && typeof window.userImpersonation.exitImpersonation === 'function') {
                        console.log('[DEBUG] Using user impersonation system to exit');
                        await window.userImpersonation.exitImpersonation();
                        
                        // Refresh the navigation to remove the banner
                        await setupNav();
                        
                        // Redirect to admin panel
                        window.location.href = 'admin.html';
                        return;
                    }
                    
                    // Fallback: manual session restoration
                    const impersonationData = localStorage.getItem('impersonationData');
                    if (!impersonationData) {
                        console.error('[ERROR] No impersonation data found');
                        alert('No impersonation session found');
                        return;
                    }
                    
                    const parsed = JSON.parse(impersonationData);
                    const originalSession = parsed.originalSession;
                    
                    if (!originalSession) {
                        console.error('[ERROR] No original session found in impersonation data');
                        alert('No original admin session found');
                        return;
                    }
                    
                    console.log('[DEBUG] Restoring original session...', originalSession);
                    
                    const supabase = window.globalSupabase || window.supabase;
                    if (!supabase) {
                        console.error('[ERROR] Supabase not available');
                        alert('Unable to access authentication system');
                        return;
                    }
                    
                    // Restore the original session
                    const { error } = await supabase.auth.setSession({
                        access_token: originalSession.access_token,
                        refresh_token: originalSession.refresh_token
                    });
                    
                    if (error) {
                        console.error('[ERROR] Failed to restore session:', error);
                        alert('Failed to restore admin session: ' + error.message);
                        return;
                    }
                    
                    // Clear impersonation data
                    localStorage.removeItem('impersonationData');
                    console.log('[DEBUG] Impersonation ended, session restored');
                    
                    // Refresh the navigation to remove the banner
                    await setupNav();
                    
                    // Redirect to admin panel
                    window.location.href = 'admin.html';
                    
                } catch (e) {
                    console.error('[ERROR] Exception during switch back:', e);
                    alert('Error switching back to admin: ' + e.message);
                }
            };
        }
        
        console.log('[DEBUG] Nav rendered, displayName:', displayName);
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
            nav.innerHTML = renderNav('');
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