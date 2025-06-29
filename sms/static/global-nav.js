// static/global-nav-v2.js
// Simple sticky header with 3 columns and optional Supabase integration

(function() {
    // Helper: Wait for DOMContentLoaded
    function onDOMReady(cb) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', cb);
        } else {
            cb();
        }
    }

    // Render the navigation bar
    function renderNav(displayName) {
        return `
        <div style="display:grid;grid-template-columns:auto 1fr 0.5fr;align-items:center;width:100vw;margin:0;">
            <div style="background:#f3f3f3;display:flex;align-items:center;justify-content:flex-start;height:60px;padding:0;margin:0;">
                <img src='static/assets/supersparky.png' alt='Logo' style='height:60px;width:60px;object-fit:cover;display:block;padding:0;margin:0;border-radius:0;'>
                <span style="font-weight:700;letter-spacing:1px;font-size:1.8em;color:#1976ff;margin-left:0;">Sparky Messaging</span>
            </div>
            <div style="background:#e0e0e0;display:flex;align-items:center;justify-content:center;height:60px;"></div>
            <div style="background:#cccccc;display:flex;align-items:center;justify-content:flex-end;height:60px;padding:0;margin:0;">
                <span style="color:#1976ff;font-weight:600;font-size:1.08em;margin-right:18px;">${displayName ? 'Welcome, ' + displayName : ''}</span>
                <button id="logout-btn" style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;">Log Out</button>
            </div>
        </div>
        `;
    }

    // Optionally fetch display name from Supabase (if available)
    async function getDisplayName() {
        if (!window.supabase || !window.supabase.auth) return '';
        try {
            const sessionResult = await window.supabase.auth.getSession();
            const session = sessionResult.data.session;
            if (!session || !session.user) return '';
            const userId = session.user.id;
            const { data, error } = await window.supabase
                .from('profiles')
                .select('display_name, email')
                .eq('id', userId)
                .maybeSingle();
            if (error || !data) return '';
            if (data.display_name && data.display_name.trim()) return data.display_name;
            if (data.email) return data.email;
            return '';
        } catch {
            return '';
        }
    }

    // Setup the navigation bar
    async function setupNav() {
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
        if (window.supabase && window.supabase.auth) {
            displayName = await getDisplayName();
        }
        nav.innerHTML = renderNav(displayName);

        // Log Out button logic (if Supabase is present)
        var logoutBtn = nav.querySelector('#logout-btn');
        if (logoutBtn) {
            logoutBtn.onclick = async function() {
                if (window.supabase && window.supabase.auth) {
                    await window.supabase.auth.signOut();
                }
                window.location.href = 'login.html';
            };
        }
    }

    // Initial setup
    onDOMReady(setupNav);
})();