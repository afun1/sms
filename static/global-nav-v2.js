console.log('[DEBUG] global-nav-v2.js script loaded');

// --- DIAGNOSTIC BLOCK ---
console.log('[DIAG] typeof window.supabase:', typeof window.supabase);
if (window.supabase) {
    console.log('[DIAG] window.supabase.createClient:', typeof window.supabase.createClient);
}
console.log('[DIAG] All script tags on page:');
document.querySelectorAll('script').forEach(s => console.log(s.src));
// --- END DIAGNOSTIC BLOCK ---

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
        if (!window.supabase || !window.supabase.auth) {
            console.warn('[DEBUG] window.supabase or window.supabase.auth missing:', window.supabase, window.supabase && window.supabase.auth);
            return '';
        }
        try {
            const sessionResult = await window.supabase.auth.getSession();
            const session = sessionResult.data.session;
            console.log('[DEBUG] Supabase session:', session);
            if (!session || !session.user) {
                console.warn('[DEBUG] No Supabase session or user found');
                return '';
            }
            const userId = session.user.id;
            const { data, error } = await window.supabase
                .from('profiles')
                .select('display_name, email')
                .eq('id', userId)
                .maybeSingle();
            console.log('[DEBUG] Supabase profiles query:', { userId, data, error });
            if (error) {
                console.error('[DEBUG] Error fetching profile:', error);
                return '';
            }
            if (!data) {
                console.warn('[DEBUG] No profile row found for user:', userId);
                return '';
            }
            if (data.display_name && data.display_name.trim()) return data.display_name;
            if (data.email) return data.email;
            return '';
        } catch (e) {
            console.error('[DEBUG] Exception in getDisplayName:', e);
            return '';
        }
    }

    function renderNav(displayName) {
        return `\
        <div style="display:grid;grid-template-columns:auto 1fr 0.5fr;align-items:center;width:100vw;margin:0;">
            <div style="background:#f3f3f3;display:flex;align-items:center;justify-content:flex-start;height:60px;padding:0;margin:0;">
                <img src='https://yggfiuqxfxsoyesqgpyt.supabase.co/storage/v1/object/sign/assetts/Sparky%20AI.gif?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV82NDZjMzIxYy05NDgwLTQ0NDgtYTYxYy0yZTBiYmIzYjA2N2MiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhc3NldHRzL1NwYXJreSBBSS5naWYiLCJpYXQiOjE3NTA4MjY0ODksImV4cCI6NDkwNDQyNjQ4OX0.EvAry9yafzSiWUPneOSv3RgPQzHcKbvpNhel_XcP_Og' alt='Logo' style='height:60px;width:60px;object-fit:cover;display:block;padding:0;margin:0;border-radius:0;'>
                <span style="font-weight:700;letter-spacing:1px;font-size:1.8em;color:#1976ff;margin-left:0;">Sparky Messaging</span>
            </div>
            <div style="background:#e0e0e0;display:flex;align-items:center;justify-content:center;height:60px;"></div>
            <div style="background:#cccccc;display:flex;align-items:center;justify-content:flex-end;height:60px;padding:0;margin:0;">
                <span style="color:#1976ff;font-weight:600;font-size:1.08em;margin-right:18px;">Welcome,${displayName ? ' ' + displayName : ''}</span>
                <button style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;">Log Out</button>
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
        nav.style.position = 'sticky';
        nav.style.top = '0';
        nav.style.left = '0';
        nav.style.width = '100%';
        nav.style.zIndex = '1000';
        nav.style.background = '#fff';
        nav.style.color = '#2a3f7c';
        nav.style.boxShadow = '0 2px 8px rgba(42,63,124,0.08)';
        nav.style.padding = '0';
        nav.style.margin = '0';
        let displayName = '';
        try {
            console.log('[DEBUG] window.supabase:', window.supabase);
            console.log('[DEBUG] window.supabase.auth:', window.supabase && window.supabase.auth);
            if (window.supabase && window.supabase.auth) {
                displayName = await getDisplayName();
                console.log('[DEBUG] getDisplayName returned:', displayName);
            }
        } catch (e) {
            console.error('[DEBUG] Error in setupNav getDisplayName:', e);
        }
        nav.innerHTML = renderNav(displayName);
        // Make Log Out button work if Supabase is present
        var logoutBtn = nav.querySelector('button');
        if (logoutBtn) {
            logoutBtn.onclick = async function() {
                try {
                    if (window.supabase && window.supabase.auth) {
                        await window.supabase.auth.signOut();
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
        console.log('[DEBUG] Nav rendered, displayName:', displayName);
    }

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
            if (!window.supabaseClient) {
                window.supabaseClient = window.supabase.createClient(
                    'https://yggfiuqxfxsoyesqgpyt.supabase.co',
                    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9zZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q'
                );
                window.supabase = window.supabaseClient;
                console.log('[DEBUG] Supabase client initialized');
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
            nav.style.position = 'sticky';
            nav.style.top = '0';
            nav.style.left = '0';
            nav.style.width = '100%';
            nav.style.zIndex = '1000';
            nav.style.background = '#fff';
            nav.style.color = '#2a3f7c';
            nav.style.boxShadow = '0 2px 8px rgba(42,63,124,0.08)';
            nav.style.padding = '0';
            nav.style.margin = '0';
            nav.innerHTML = renderNav('');
            console.error('[ERROR] Supabase UMD not found. Header will be static.');
        }
    });

})();