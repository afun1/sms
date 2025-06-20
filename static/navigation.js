// Global Navigation Header for Sparky Messaging
// This script creates a consistent navigation header across all pages

class SparkyNavigation {
    constructor() {
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        return filename.replace('.html', '');
    }

    getNavigationHTML() {
        return `
            <nav class="sparky-nav">
                <div class="nav-container">
                    <a href="index.html" class="nav-brand">
                        <img src="static/logo.png" alt="Sparky Logo" class="nav-logo" onerror="this.style.display='none'">
                        <div class="brand-logo" style="display:none;">⚡</div>
                        <span class="brand-text">Sparky Messaging</span>
                    </a>
                    <div class="nav-menu">
                        <a href="index.html" class="nav-link ${this.currentPage === 'index' ? 'active' : ''}">🏠 Home</a>
                        <a href="dashboard.html" class="nav-link ${this.currentPage === 'dashboard' ? 'active' : ''}">📊 Dashboard</a>
                        <a href="sms_editor.html" class="nav-link ${this.currentPage === 'sms_editor' ? 'active' : ''}">📱 SMS</a>
                        <a href="email_editor.html" class="nav-link ${this.currentPage === 'email_editor' ? 'active' : ''}">📧 Email</a>
                        <a href="rvm_editor.html" class="nav-link ${this.currentPage === 'rvm_editor' ? 'active' : ''}">📞 RVM</a>
                        <a href="ai_editor.html" class="nav-link ${this.currentPage === 'ai_editor' ? 'active' : ''}">🤖 AI</a>
                        <a href="campaign_builder.html" class="nav-link ${this.currentPage === 'campaign_builder' ? 'active' : ''}">🚀 Campaigns</a>
                        <a href="admin.html" class="nav-link admin-only" id="adminLink" style="display: none;">⚙️ Admin</a>
                    </div>
                    <div class="nav-user">
                        <div class="user-info">
                            <span>Welcome, <span class="user-name" id="userName">User</span></span>
                            <span class="user-role" id="userRole">user</span>
                        </div>
                        <a href="#" class="logout-link" onclick="sparkyNav.logout(); return false;">Log Out</a>
                    </div>
                </div>
            </nav>
        `;
    }

    getNavigationCSS() {
        return `
            /* Global Sparky Navigation Styles */
            .sparky-nav {
                background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
                padding: 12px 0;
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                border-bottom: 2px solid rgba(255,255,255,0.1);
            }
            
            .sparky-nav .nav-container {
                max-width: 1400px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: 250px 1fr auto;
                align-items: center;
                gap: 20px;
                padding: 0 30px;
            }
            
            .sparky-nav .nav-brand {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.3em;
                font-weight: 700;
                color: white;
                text-decoration: none;
            }
            
            .sparky-nav .nav-brand:hover {
                color: white;
                text-decoration: none;
            }
            
            .sparky-nav .nav-logo {
                width: 32px;
                height: 32px;
                border-radius: 50%;
            }
            
            .sparky-nav .brand-logo {
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
            
            .sparky-nav .nav-menu {
                display: flex;
                justify-content: center;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .sparky-nav .nav-link {
                color: rgba(255,255,255,0.9);
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                font-weight: 500;
                font-size: 0.95em;
                white-space: nowrap;
            }
            
            .sparky-nav .nav-link:hover {
                color: white;
                background: rgba(255,255,255,0.15);
                transform: translateY(-1px);
                text-decoration: none;
            }
            
            .sparky-nav .nav-link.active {
                background: rgba(255,255,255,0.25);
                color: white;
                box-shadow: 0 2px 8px rgba(255,255,255,0.2);
            }
            
            .sparky-nav .nav-user {
                display: flex;
                align-items: center;
                gap: 15px;
                justify-self: end;
            }
            
            .sparky-nav .user-info {
                color: rgba(255,255,255,0.9);
                font-size: 0.9em;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .sparky-nav .user-name {
                font-weight: 600;
            }
            
            .sparky-nav .user-role {
                background: rgba(255,255,255,0.2);
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.8em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .sparky-nav .logout-link {
                color: #ff4757 !important;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                padding: 6px 12px;
                border-radius: 15px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255, 71, 87, 0.3);
            }
            
            .sparky-nav .logout-link:hover {
                color: #ff3742 !important;
                background: rgba(255, 71, 87, 0.2);
                border-color: rgba(255, 71, 87, 0.5);
                text-decoration: none;
                transform: translateY(-1px);
            }
            
            /* Responsive Design */
            @media (max-width: 1200px) {
                .sparky-nav .nav-container {
                    grid-template-columns: 200px 1fr auto;
                    gap: 15px;
                    padding: 0 20px;
                }
                
                .sparky-nav .nav-brand {
                    font-size: 1.1em;
                }
                
                .sparky-nav .nav-link {
                    padding: 6px 12px;
                    font-size: 0.9em;
                }
            }
            
            @media (max-width: 768px) {
                .sparky-nav .nav-container {
                    grid-template-columns: 1fr;
                    gap: 10px;
                    text-align: center;
                }
                
                .sparky-nav .nav-menu {
                    order: 2;
                    gap: 5px;
                }
                
                .sparky-nav .nav-user {
                    order: 3;
                    justify-self: center;
                }
                
                .sparky-nav .nav-link {
                    padding: 5px 10px;
                    font-size: 0.85em;
                }
            }
            
            /* Body padding to account for sticky nav */
            body:not(.login-page) {
                padding-top: 70px;
            }
        `;
    }

    init() {
        // Add CSS styles to head
        const style = document.createElement('style');
        style.textContent = this.getNavigationCSS();
        document.head.appendChild(style);

        // Add navigation HTML to top of body
        const nav = document.createElement('div');
        nav.innerHTML = this.getNavigationHTML();
        document.body.insertBefore(nav.firstElementChild, document.body.firstChild);

        // Initialize authentication and user info
        this.checkAuth();

        // Handle logo load error
        const logo = document.querySelector('.nav-logo');
        const brandLogo = document.querySelector('.brand-logo');
        if (logo) {
            logo.addEventListener('error', () => {
                logo.style.display = 'none';
                if (brandLogo) brandLogo.style.display = 'flex';
            });
            logo.addEventListener('load', () => {
                logo.style.display = 'block';
                if (brandLogo) brandLogo.style.display = 'none';
            });
        }
    }

    checkAuth() {
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');
        const userRole = localStorage.getItem('userRole');
        
        if (!token && !window.location.pathname.includes('login.html')) {
            window.location.href = 'login.html';
            return;
        }
        
        // Display user info in navigation
        const userNameElement = document.getElementById('userName');
        const userRoleElement = document.getElementById('userRole');
        const adminLink = document.getElementById('adminLink');
        
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

    logout() {
        if (confirm('Are you sure you want to log out?')) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userRole');
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        }
    }
}

// Initialize navigation when DOM is loaded
let sparkyNav;
document.addEventListener('DOMContentLoaded', function() {
    // Don't add navigation to login page
    if (!document.body.classList.contains('login-page') && !window.location.pathname.includes('login.html')) {
        sparkyNav = new SparkyNavigation();
    }
});

// Export for global use
window.SparkyNavigation = SparkyNavigation;
