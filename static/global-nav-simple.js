// Simplified navigation that works without authentication blocking
console.log('[DEBUG] global-nav-simple.js script loaded');

(function() {
    console.log('[DEBUG] Simple navigation IIFE started');
    
    function renderBasicNav() {
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
                </nav>
            </div>
            <div style="display:flex;align-items:center;justify-content:flex-end;height:60px;padding:0;margin:0;">
                <span style="color:#1976ff;font-weight:600;font-size:1.08em;margin-right:18px;">Welcome</span>
                <button id="logoutBtn" style="background:none;border:none;color:#e53935;font-weight:700;font-size:1.08em;cursor:pointer;padding:8px 0;line-height:1.2;">Log<br>Out</button>
            </div>
        </div>
        `;
    }

    function setupSimpleNav() {
        console.log('[DEBUG] setupSimpleNav called');
        
        let nav = document.getElementById('global-nav');
        if (!nav) {
            nav = document.createElement('nav');
            nav.id = 'global-nav';
            document.body.prepend(nav);
        }
        
        // Style the nav
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
        
        // Set body padding
        document.body.style.paddingTop = '80px';
        
        // Render navigation
        nav.innerHTML = renderBasicNav();
        
        // Add logout handler
        const logoutBtn = nav.querySelector('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = function() {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = 'login.html';
            };
        }
        
        console.log('[DEBUG] Simple navigation setup complete');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupSimpleNav);
    } else {
        setupSimpleNav();
    }
    
})();
