// Clean navigation script - bulletproof login detection
(function() {
    // FIRST LINE CHECK: Exit before any other code
    if (window.location.pathname.toLowerCase().includes('login')) {
        console.log('[IMMEDIATE EXIT] Login detected in pathname');
        return;
    }
    
    if (window.location.href.toLowerCase().includes('login')) {
        console.log('[IMMEDIATE EXIT] Login detected in href');
        return;
    }
    
    if (document.title && document.title.toLowerCase().includes('login')) {
        console.log('[IMMEDIATE EXIT] Login detected in title');
        return;
    }
    
    // Additional check for login elements
    if (document.readyState !== 'loading') {
        if (document.querySelector('.login-container') || 
            document.querySelector('#loginForm') || 
            document.querySelector('#loginFormPanel')) {
            console.log('[IMMEDIATE EXIT] Login elements detected');
            return;
        }
    }
    
    console.log('[NAVIGATION] Starting navigation script');
    
    // Set up Supabase client
    if (!window.globalSupabase && window.supabase) {
        const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
        const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';
        window.globalSupabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    }

    async function getDisplayName() {
        const supabase = window.globalSupabase;
        if (!supabase) return { displayName: '', userRole: null, secondaryRole: null };
        
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session?.user) return { displayName: '', userRole: null, secondaryRole: null };
            
            const { data, error } = await supabase
                .from('profiles')
                .select('first_name, last_name, email, role, secondary_role')
                .eq('id', session.user.id)
                .maybeSingle();
                
            console.log('[DB DEBUG] Profile:', data);
                
            if (error || !data) return { displayName: '', userRole: null, secondaryRole: null };
            
            const displayName = `${data.first_name || ''} ${data.last_name || ''}`.trim() || data.email || '';
            
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

    function renderNav(displayName, userRole, secondaryRole) {
        let roleButton = '';
        
        if (secondaryRole && secondaryRole.toLowerCase() !== userRole.toLowerCase()) {
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const urlParams = new URLSearchParams(window.location.search);
            const currentView = urlParams.get('view');
            
            console.log('[ROLE DEBUG] Primary:', userRole, 'Secondary:', secondaryRole, 'View:', currentView);
            
            if (currentView && currentView.toLowerCase() === secondaryRole.toLowerCase()) {
                // Viewing as secondary, show primary button
                roleButton = `<a href="${currentPage}" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;line-height:1.2;"><span style="font-size:10px;">View as</span><br>${userRole.charAt(0).toUpperCase() + userRole.slice(1)}</a>`;
                console.log('[ROLE DEBUG] Showing primary button');
            } else {
                // Viewing as primary, show secondary button
                roleButton = `<a href="${currentPage}?view=${secondaryRole.toLowerCase()}" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;line-height:1.2;"><span style="font-size:10px;">View as</span><br>${secondaryRole.charAt(0).toUpperCase() + secondaryRole.slice(1)}</a>`;
                console.log('[ROLE DEBUG] Showing secondary button');
            }
        } else if (userRole === 'admin' && !secondaryRole) {
            roleButton = `<a href="admin.html" style="color:#e53935;text-decoration:none;font-weight:500;font-size:1.08em;border-left:1px solid #ddd;padding-left:22px;line-height:1.2;"><span style="font-size:10px;">View as</span><br>Admin</a>`;
        }
        
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
                  ${roleButton}
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
        console.log('[NAVIGATION] Setting up navigation');
        
        let nav = document.getElementById('global-nav');
        if (!nav) {
            nav = document.createElement('nav');
            nav.id = 'global-nav';
            document.body.prepend(nav);
        }
        nav.style.cssText = 'position:fixed;top:0;left:0;width:100%;z-index:9999;background:#fff;color:#2a3f7c;box-shadow:0 2px 8px rgba(42,63,124,0.08);padding:0;margin:0;border-bottom:1px solid rgba(42,63,124,0.1);';
        document.body.style.paddingTop = '80px';
        
        const { displayName, userRole, secondaryRole } = await getDisplayName();
        nav.innerHTML = renderNav(displayName, userRole, secondaryRole);
        
        // Handle logout
        const logoutBtn = nav.querySelector('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Immediate logout - clear everything and redirect
                try {
                    // Try to sign out from Supabase synchronously if possible
                    const supabase = window.globalSupabase;
                    if (supabase && supabase.auth && supabase.auth.signOut) {
                        supabase.auth.signOut().catch(() => {}); // Fire and forget
                    }
                } catch (error) {
                    console.log('Supabase signout error (ignored):', error);
                }
                
                // Clear all storage
                localStorage.clear();
                sessionStorage.clear();
                
                // Immediate redirect
                window.location.href = 'login.html';
            });
        }
        
        console.log('[NAVIGATION] Navigation setup complete');
    }

    // Export global function for refreshing navigation
    window.refreshGlobalNav = async function() {
        console.log('[NAVIGATION] Refreshing global navigation');
        await setupNav();
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupNav);
    } else {
        setupNav();
    }
})();
