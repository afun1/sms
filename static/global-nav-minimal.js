// Minimal navigation for debugging
console.log('[NAV] Loading minimal navigation...');

(function() {
    'use strict';
    
    // Basic navigation setup
    function setupBasicNavigation() {
        console.log('[NAV] Setting up basic navigation...');
        
        // Don't setup navigation if already exists
        if (document.getElementById('global-nav')) {
            console.log('[NAV] Navigation already exists, skipping setup');
            return;
        }
        
        // Create navigation container
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
            padding: 15px 20px;
            margin: 0;
            border-bottom: 1px solid rgba(42,63,124,0.1);
        `;
        
        // Basic navigation content
        nav.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <span style="font-weight: 700; font-size: 1.5em; color: #1976ff;">Sparky Messaging</span>
                </div>
                <div style="display: flex; gap: 20px; align-items: center;">
                    <a href="index.html" style="color: #1976ff; text-decoration: none;">Home</a>
                    <a href="ai_editor.html" style="color: #1976ff; text-decoration: none;">AI Editor</a>
                    <a href="sms_editor.html" style="color: #1976ff; text-decoration: none;">SMS</a>
                    <a href="list.html" style="color: #1976ff; text-decoration: none;">List</a>
                    <a href="assets.html" style="color: #1976ff; text-decoration: none;">Profile</a>
                    <button id="logoutBtn" style="background: none; border: none; color: #e53935; cursor: pointer;">Logout</button>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.insertBefore(nav, document.body.firstChild);
        
        // Add body padding
        document.body.style.paddingTop = '70px';
        
        // Simple logout handler
        const logoutBtn = nav.querySelector('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = function() {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = 'login.html';
            };
        }
        
        console.log('[NAV] Basic navigation setup complete');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupBasicNavigation);
    } else {
        setupBasicNavigation();
    }
    
})();
