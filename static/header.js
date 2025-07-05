(function() {
    'use strict';
    
    // Early exit for login and auth pages
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    if (currentPage === 'login.html' || currentPage.includes('auth')) {
        return;
    }
    
    console.log('[HEADER] Initializing header system');
    
    // Initialize Supabase client
    const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';
    let supabase = null;
    
    // Initialize Supabase if available
    if (typeof window.supabase !== 'undefined' && window.supabase.createClient) {
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    }
    
    // Function to load user's display name and role
    async function loadUserDisplayName(welcomeElement, roleElement) {
        try {
            if (!supabase) {
                console.warn('[HEADER] Supabase not available, keeping default welcome text');
                return;
            }
            
            // Add timeout to prevent hanging
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Timeout')), 5000);
            });
            
            const userPromise = supabase.auth.getUser();
            const { data: { user } } = await Promise.race([userPromise, timeoutPromise]);
            
            if (!user) {
                console.warn('[HEADER] No authenticated user found');
                return;
            }
            
            const profilePromise = supabase
                .from('profiles')
                .select('display_name, role, secondary_role')
                .eq('id', user.id)
                .single();
            
            const { data: profile, error } = await Promise.race([profilePromise, timeoutPromise]);
            
            if (error) {
                console.error('[HEADER] Error fetching profile:', error);
                return;
            }
            
            if (profile && profile.display_name) {
                welcomeElement.textContent = `Welcome, ${profile.display_name}`;
            }
            
            // Only show "View as" if user has admin secondary role
            if (profile && profile.secondary_role && profile.secondary_role.toLowerCase() === 'admin') {
                // Check current view mode from URL or localStorage
                const urlParams = new URLSearchParams(window.location.search);
                const currentView = urlParams.get('view') || localStorage.getItem('currentView') || 'secondary';
                
                // Determine which role to show based on current view
                let roleToShow = '';
                let nextView = '';
                let targetPage = '';
                
                if (currentView === 'primary' && profile && profile.role) {
                    // Currently viewing as primary role, offer to switch to admin (secondary)
                    roleToShow = profile.role;
                    nextView = 'secondary';
                    targetPage = window.location.pathname.split('/').pop().split('?')[0];
                } else if (profile && profile.secondary_role) {
                    // Currently viewing as secondary role (or default), show admin role
                    roleToShow = profile.secondary_role;
                    nextView = 'primary';
                    targetPage = 'admin.html';
                }
                
                if (roleToShow) {
                    roleElement.innerHTML = `<span style="color: #d32f2f; font-size: 10px;">View as:</span> <a href="${targetPage}?view=${nextView}" style="font-size: 12px; color: #1976ff; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'" onclick="localStorage.setItem('currentView', '${nextView}')">${roleToShow}</a>`;
                }
            }
        } catch (error) {
            console.error('[HEADER] Error loading user display name:', error);
        }
    }
    
    // Add timeout to prevent hanging
    const initTimeout = setTimeout(() => {
        console.warn('[HEADER] Initialization timeout, creating basic header');
        createBasicHeader();
    }, 1000);
    
    function createBasicHeader() {
        try {
            createHeader();
            clearTimeout(initTimeout);
        } catch (error) {
            console.error('[HEADER] Error creating header:', error);
            // Create minimal fallback header
            const header = document.createElement('div');
            header.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:50px;background:white;border-bottom:1px solid #ccc;z-index:9999;display:flex;align-items:center;padding:0 20px;"><span style="font-weight:bold;color:#1976ff;">Sparky Messaging</span></div>';
            document.body.insertBefore(header.firstChild, document.body.firstChild);
            document.body.style.paddingTop = '50px';
        }
    }
    
    function createHeader() {
        // Remove any existing header
        const existingHeader = document.getElementById('app-header');
        if (existingHeader) {
            existingHeader.remove();
        }
        
        // Create header element
        const header = document.createElement('header');
        header.id = 'app-header';
        header.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 50px;
            background: #ffffff;
            border-bottom: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0;
            box-sizing: border-box;
        `;
        
        // Create logo/brand section
        const brandSection = document.createElement('div');
        brandSection.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0px;
            width: 280px;
            flex-shrink: 0;
            height: 50px;
            padding: 0 0 0 10px;
            box-sizing: border-box;
        `;
        
        const logo = document.createElement('img');
        logo.src = 'https://yggfiuqxfxsoyesqgpyt.supabase.co/storage/v1/object/sign/assetts/Sparky%20AI.gif?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV82NDZjMzIxYy05NDgwLTQ0NDgtYTYxYy0yZTBiYmIzYjA2N2MiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhc3NldHRzL1NwYXJreSBBSS5naWYiLCJpYXQiOjE3NTA4MjY0ODksImV4cCI6NDkwNDQyNjQ4OX0.EvAry9yafzSiWUPneOSv3RgPQzHcKbvpNhel_XcP_Og';
        logo.alt = 'Sparky AI';
        logo.style.cssText = `
            height: 50px;
            width: 50px;
            object-fit: cover;
        `;
        
        const brandText = document.createElement('span');
        brandText.textContent = 'Sparky Messaging';
        brandText.style.cssText = `
            font-size: 24px;
            font-weight: 700;
            color: #1976ff;
            letter-spacing: 1px;
            white-space: nowrap;
        `;
        
        brandSection.appendChild(logo);
        brandSection.appendChild(brandText);
        
        // Create navigation section
        const navSection = document.createElement('nav');
        navSection.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0px;
            height: 50px;
            padding: 0 10px;
            box-sizing: border-box;
            flex: 1;
        `;
        
        // Navigation links
        const navLinks = [
            { text: 'Home', href: 'index.html' },
            { text: 'Sparky AI', href: 'ai_editor.html' },
            { text: 'SMS', href: 'sms_editor.html' },
            { text: 'RVM', href: 'rvm_editor.html' },
            { text: 'Email', href: 'email_editor.html' },
            { text: 'Campaigns', href: 'campaign_builder.html' },
            { text: 'Lists', href: 'list.html' },
            { text: 'Profile', href: 'assets.html' }
        ];
        
        navLinks.forEach((link, index) => {
            const a = document.createElement('a');
            a.href = link.href;
            a.textContent = link.text;
            a.style.cssText = `
                color: #1976ff;
                text-decoration: none;
                font-weight: 500;
                font-size: 16px;
                padding: 8px 10px;
                border-radius: 4px;
                transition: background-color 0.2s;
            `;
            
            // Highlight current page
            if (currentPage === link.href) {
                a.style.backgroundColor = '#e3f2fd';
                a.style.fontWeight = '600';
            }
            
            // Hover effect
            a.addEventListener('mouseenter', () => {
                if (currentPage !== link.href) {
                    a.style.backgroundColor = '#f5f5f5';
                }
            });
            
            a.addEventListener('mouseleave', () => {
                if (currentPage !== link.href) {
                    a.style.backgroundColor = 'transparent';
                }
            });
            
            navSection.appendChild(a);
            
            // Add pipe separator after each link except the last one
            if (index < navLinks.length - 1) {
                const pipe = document.createElement('span');
                pipe.textContent = '|';
                pipe.style.cssText = `
                    color: #ccc;
                    margin: 0 5px;
                    font-size: 16px;
                `;
                navSection.appendChild(pipe);
            }
        });
        
        // Create user section
        const userSection = document.createElement('div');
        userSection.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 16px;
            height: 50px;
            padding: 0 0 0 10px;
            box-sizing: border-box;
            width: 280px;
            flex-shrink: 0;
        `;
        
        // Create a container for the text elements (role and welcome)
        const textContainer = document.createElement('div');
        textContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 2px;
        `;
        
        const roleText = document.createElement('div');
        roleText.style.cssText = `
            color: #333;
            font-weight: 600;
            line-height: 1;
        `;
        
        const welcomeText = document.createElement('span');
        welcomeText.textContent = 'Welcome, User';
        welcomeText.style.cssText = `
            color: #333;
            font-weight: 600;
            font-size: 16px;
        `;
        
        textContainer.appendChild(roleText);
        textContainer.appendChild(welcomeText);
        
        // Load user's display name and role from Supabase asynchronously (don't block header creation)
        loadUserDisplayName(welcomeText, roleText).catch(error => {
            console.error('[HEADER] Failed to load user data:', error);
        });
        
        const logoutLink = document.createElement('a');
        logoutLink.href = 'login.html';
        logoutLink.innerHTML = 'Log<br>out';
        logoutLink.style.cssText = `
            color: #d32f2f;
            text-decoration: none;
            font-weight: 600;
            font-size: 10px;
            padding: 4px 0px;
            border: 1px solid #d32f2f;
            border-radius: 4px;
            transition: all 0.2s;
            line-height: 1.1;
            text-align: center;
        `;
        
        logoutLink.addEventListener('mouseenter', () => {
            logoutLink.style.backgroundColor = '#d32f2f';
            logoutLink.style.color = 'white';
        });
        
        logoutLink.addEventListener('mouseleave', () => {
            logoutLink.style.backgroundColor = 'transparent';
            logoutLink.style.color = '#d32f2f';
        });
        
        // Ultra-simple logout - prevent default navigation and handle everything ourselves
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('[HEADER] Logout clicked - clearing storage and redirecting');
            localStorage.clear();
            sessionStorage.clear();
            // Immediate redirect without any delay
            window.location.replace('login.html');
        });
        
        userSection.appendChild(textContainer);
        userSection.appendChild(logoutLink);
        
        // Assemble header
        header.appendChild(brandSection);
        header.appendChild(navSection);
        header.appendChild(userSection);
        
        // Insert header at top of body
        document.body.insertBefore(header, document.body.firstChild);
        
        // Add top padding to body to account for fixed header
        document.body.style.paddingTop = '50px';
        
        console.log('[HEADER] Header created successfully');
    }
    
    // Initialize immediately without waiting for DOM
    try {
        if (document.readyState === 'loading') {
            // If still loading, wait for DOM ready
            document.addEventListener('DOMContentLoaded', createBasicHeader);
        } else {
            // DOM is ready, create immediately
            createBasicHeader();
        }
    } catch (error) {
        console.error('[HEADER] Initialization error:', error);
    }
    
    // Export global refresh function
    window.refreshHeader = function() {
        try {
            createBasicHeader();
        } catch (error) {
            console.error('[HEADER] Refresh error:', error);
        }
    };
    
})();
