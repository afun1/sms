// Simplified Global Navigation for Sparky Messaging
// Just include this script and it will automatically add navigation

(function() {
    'use strict';
    
    // Don't add navigation to login page
    if (window.location.pathname.includes('login.html') || document.body.classList.contains('login-page')) {
        return;
    }

    // Get current page for active state
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        return filename.replace('.html', '');
    }

    // Add navigation CSS
    function addNavigationCSS() {
        const css = `
            /* Global Sparky Navigation */
            .sparky-global-nav {
                background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
                padding: 12px 0;
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                border-bottom: 2px solid rgba(255,255,255,0.1);
            }
            
            .sparky-global-nav .nav-container {
                width: 100%;
                display: grid;
                grid-template-columns: 250px 1fr auto;
                align-items: center;
                gap: 20px;
                padding-left: 0;
                padding-right: 0;
            }
            
            .sparky-global-nav .nav-brand {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.3em;
                font-weight: 700;
                color: white;
                text-decoration: none;
            }
            
            .sparky-global-nav .nav-brand:hover {
                color: white;
                text-decoration: none;
            }
            
            .sparky-global-nav .nav-logo {
                width: 32px;
                height: 32px;
                border-radius: 50%;
            }
            
            .sparky-global-nav .brand-icon {
                width: 32px;
                height: 32px;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: #4e73df;
            }
            
            .sparky-global-nav .nav-menu {
                display: flex;
                justify-content: center;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .sparky-global-nav .nav-link {
                color: rgba(255,255,255,0.9);
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                font-weight: 500;
                font-size: 0.95em;
                white-space: nowrap;
            }
            
            .sparky-global-nav .nav-link:hover {
                color: white;
                background: rgba(255,255,255,0.15);
                transform: translateY(-1px);
                text-decoration: none;
            }
            
            .sparky-global-nav .nav-link.active {
                background: rgba(255,255,255,0.25);
                color: white;
                box-shadow: 0 2px 8px rgba(255,255,255,0.2);
            }
            
            .sparky-global-nav .nav-user {
                display: flex;
                align-items: center;
                gap: 15px;
                justify-self: end;
            }
            
            .sparky-global-nav .user-info {
                color: rgba(255,255,255,0.9);
                font-size: 0.9em;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .sparky-global-nav .user-name {
                font-weight: 600;
            }
            
            .sparky-global-nav .user-role {
                background: rgba(255,255,255,0.2);
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.8em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .sparky-global-nav .logout-link {
                color: #ff4757 !important;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                padding: 6px 12px;
                border-radius: 15px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255, 71, 87, 0.3);
            }
            
            .sparky-global-nav .logout-link:hover {
                color: #ff3742 !important;
                background: rgba(255, 71, 87, 0.2);
                border-color: rgba(255, 71, 87, 0.5);
                text-decoration: none;
                transform: translateY(-1px);
            }
            
            /* Responsive Design */
            @media (max-width: 1200px) {
                .sparky-global-nav .nav-container {
                    grid-template-columns: 200px 1fr auto;
                    gap: 15px;
                    padding-left: 0;
                    padding-right: 0;
                    width: 100%;
                }
                
                .sparky-global-nav .nav-brand {
                    font-size: 1.1em;
                }
                
                .sparky-global-nav .nav-link {
                    padding: 6px 12px;
                    font-size: 0.9em;
                }
            }
            
            @media (max-width: 768px) {
                .sparky-global-nav .nav-container {
                    grid-template-columns: 1fr;
                    gap: 10px;
                    text-align: center;
                    width: 100%;
                }
                
                .sparky-global-nav .nav-menu {
                    order: 2;
                    gap: 5px;
                }
                
                .sparky-global-nav .nav-user {
                    order: 3;
                    justify-self: center;
                }
                
                .sparky-global-nav .nav-link {
                    padding: 5px 10px;
                    font-size: 0.85em;
                }
            }
            
            /* Body padding adjustment */
            body {
                padding-top: 70px !important;
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
    }

    // Create navigation HTML
    function createNavigation() {
        const currentPage = getCurrentPage();
        
        const nav = document.createElement('nav');
        nav.className = 'sparky-global-nav';
        nav.innerHTML = `
            <div class="nav-container">
                <a href="index.html" class="nav-brand">
                    <img src="static/logo.png" alt="Sparky Logo" class="nav-logo" style="display: none;">
                    <div class="brand-icon">⚡</div>
                    <span>Sparky Messaging</span>
                </a>
                <div class="nav-menu">
                    <a href="index.html" class="nav-link ${currentPage === 'index' ? 'active' : ''}">🏠 Home</a>
                    <a href="sms_editor.html" class="nav-link ${currentPage === 'sms_editor' ? 'active' : ''}">📱 SMS</a>
                    <a href="email_editor.html" class="nav-link ${currentPage === 'email_editor' ? 'active' : ''}">📧 Email</a>
                    <a href="rvm_editor.html" class="nav-link ${currentPage === 'rvm_editor' ? 'active' : ''}">📞 RVM</a>
                    <a href="ai_editor.html" class="nav-link ${currentPage === 'ai_editor' ? 'active' : ''}">🤖 AI</a>
                    <a href="campaign_builder.html" class="nav-link ${currentPage === 'campaign_builder' ? 'active' : ''}">🚀 Campaigns</a>
                    <a href="list.html" class="nav-link ${currentPage === 'list' ? 'active' : ''}">📋 List Builder</a>
                    <a href="admin.html" class="nav-link admin-only" style="display: none;">⚙️ Admin</a>
                </div>
                <div class="nav-user">
                    <div class="user-info">
                        <span>Welcome, <span class="user-name">User</span></span>
                        <span class="user-role">user</span>
                    </div>
                    <a href="#" class="logout-link" onclick="sparkyLogout(); return false;">Log Out</a>
                </div>
            </div>
        `;
        
        return nav;
    }

    // Handle authentication
    function handleAuth() {
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');
        const userRole = localStorage.getItem('userRole');
        
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        
        // Update user info
        const userNameElement = document.querySelector('.sparky-global-nav .user-name');
        const userRoleElement = document.querySelector('.sparky-global-nav .user-role');
        const adminLink = document.querySelector('.sparky-global-nav .admin-only');
        
        if (username && userNameElement) {
            userNameElement.textContent = username;
        }
        if (userRole && userRoleElement) {
            userRoleElement.textContent = userRole;
            
            // Show admin link if user is admin
            if (userRole === 'admin' && adminLink) {
                adminLink.style.display = 'inline-block';
            }
        }
    }

    // Handle logo loading
    function handleLogo() {
        const logo = document.querySelector('.sparky-global-nav .nav-logo');
        const brandIcon = document.querySelector('.sparky-global-nav .brand-icon');
        
        if (logo) {
            logo.onload = function() {
                logo.style.display = 'block';
                if (brandIcon) brandIcon.style.display = 'none';
            };
            logo.onerror = function() {
                logo.style.display = 'none';
                if (brandIcon) brandIcon.style.display = 'flex';
            };
            // Try to load the logo
            logo.src = logo.src;
        }
    }

    // Global logout function
    window.sparkyLogout = function() {
        if (confirm('Are you sure you want to log out?')) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userRole');
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        }
    };

    // Initialize navigation
    function init() {
        addNavigationCSS();
        const nav = createNavigation();
        document.body.insertBefore(nav, document.body.firstChild);
        handleAuth();
        handleLogo();
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();