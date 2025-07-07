/*
 * HEADER.JS - WORKING FINAL VERSION
 * Created: January 2025
 * 
 * This is the WORKING version of the header.js file.
 * 
 * Key Features:
 * - Admin button works correctly for users with 'admin' role
 * - Shows "Switch to: Admin" button on all pages except admin.html
 * - Shows "Switch to: [Role]" button only when on admin.html
 * - Handles role switching with localStorage
 * - Includes proper cache busting for debugging
 * - Works with Supabase authentication
 * - Responsive header with navigation, logo, and user info
 * 
 * Important Logic:
 * - currentPagePath detection: window.location.pathname.split('/').pop()
 * - Admin button only shows for users with role 'admin', 'manager', 'supervisor', or users with secondary_role 'admin'
 * - Role switching is based on actual page location, not localStorage state
 * 
 * DO NOT MODIFY THIS FILE - USE AS BACKUP/REFERENCE ONLY
 */

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
            
            // Show role switching based on role and secondary_role
            if (profile && profile.role) {
                const userRole = profile.role.toLowerCase();
                const hasSecondaryRole = profile.secondary_role && profile.secondary_role.trim() !== '';
                
                // Check current view from localStorage - default to user's actual role
                const currentView = localStorage.getItem('currentView') || userRole;
                const currentPagePath = window.location.pathname.split('/').pop() || 'index.html';
                
                // CACHE BUSTER - Version 6
                console.log('[HEADER] === CACHE BUSTER VERSION 6 ===');
                console.log('[HEADER] currentView:', currentView);
                console.log('[HEADER] userRole:', userRole);
                console.log('[HEADER] hasSecondaryRole:', hasSecondaryRole);
                console.log('[HEADER] currentPagePath:', currentPagePath);
                
                // Show role switching for managers, supervisors, and admins
                if (userRole === 'manager' || userRole === 'supervisor' || userRole === 'admin') {
                    
                    // Only show role switch if actually on admin page, otherwise always show admin button
                    console.log(`[HEADER] Checking condition: currentPagePath ('${currentPagePath}') === 'admin.html'`);
                    if (currentPagePath === 'admin.html') {
                        // On admin page - toggle between admin and user's role
                        console.log('[HEADER] CONDITION TRUE: On admin page, showing toggle');
                        
                        if (currentView === 'admin') {
                            // Currently viewing as admin, show switch to user's role
                            const roleToShow = userRole.charAt(0).toUpperCase() + userRole.slice(1);
                            const linkId = 'roleSwitchLink_' + Date.now();
                            roleElement.innerHTML = `<span style="color: #d32f2f; font-size: 10px;">Switch to:</span> <a href="#" id="${linkId}" style="font-size: 12px; color: #1976ff; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${roleToShow}</a>`;
                            
                            // Add event listener for role switch
                            setTimeout(() => {
                                const roleSwitchLink = document.getElementById(linkId);
                                if (roleSwitchLink) {
                                    roleSwitchLink.addEventListener('click', function(e) {
                                        e.preventDefault();
                                        console.log('Setting currentView to ' + userRole);
                                        localStorage.setItem('currentView', userRole);
                                        window.location.reload();
                                    });
                                }
                            }, 10);
                        } else {
                            // Currently viewing as user's role, show switch to admin
                            const linkId = 'adminSwitchLink_' + Date.now();
                            roleElement.innerHTML = `<span style="color: #d32f2f; font-size: 10px;">Switch to:</span> <a href="#" id="${linkId}" style="font-size: 12px; color: #1976ff; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">Admin</a>`;
                            
                            // Add event listener for admin switch
                            setTimeout(() => {
                                const adminSwitchLink = document.getElementById(linkId);
                                if (adminSwitchLink) {
                                    adminSwitchLink.addEventListener('click', function(e) {
                                        e.preventDefault();
                                        console.log('Setting currentView to admin');
                                        localStorage.setItem('currentView', 'admin');
                                        window.location.reload();
                                    });
                                }
                            }, 10);
                        }
                    } else {
                        // Not on admin page - always show admin button
                        console.log('[HEADER] CONDITION FALSE: Not on admin page, showing admin button');
                        const linkId = 'adminLink_' + Date.now();
                        roleElement.innerHTML = `<span style="color: #d32f2f; font-size: 10px;">Switch to:</span> <a href="#" id="${linkId}" style="font-size: 12px; color: #1976ff; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">Admin</a>`;
                        
                        // Add event listener for admin link
                        setTimeout(() => {
                            const adminLink = document.getElementById(linkId);
                            if (adminLink) {
                                adminLink.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    console.log('Admin button clicked!');
                                    window.location.href = 'admin.html';
                                });
                            }
                        }, 10);
                    }
                } else if (hasSecondaryRole) {
                    // For users with secondary role, offer switch to their role (looks dumb but effective)
                    console.log('[HEADER] User has secondary role, showing role switch');
                    const linkId = 'roleOnlyLink_' + Date.now();
                    const roleToShow = userRole.charAt(0).toUpperCase() + userRole.slice(1);
                    roleElement.innerHTML = `<span style="color: #d32f2f; font-size: 10px;">Switch to:</span> <a href="#" id="${linkId}" style="font-size: 12px; color: #1976ff; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${roleToShow}</a>`;
                    
                    // Add event listener for role switch (even though it does nothing)
                    setTimeout(() => {
                        const roleOnlyLink = document.getElementById(linkId);
                        if (roleOnlyLink) {
                            roleOnlyLink.addEventListener('click', function(e) {
                                e.preventDefault();
                                console.log('Setting currentView to ' + userRole + ' (same as current)');
                                localStorage.setItem('currentView', userRole);
                                window.location.reload();
                            });
                        }
                    }, 10);
                } else {
                    // Regular users with no secondary role - no role switching
                    console.log('[HEADER] Regular user with no secondary role - no role switching offered');
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
        logo.src = 'static/SparkyAI2.gif';
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
        roleText.className = 'roleText';
        roleText.style.cssText = `
            color: #333;
            font-weight: 600;
            line-height: 1;
        `;
        
        const welcomeText = document.createElement('span');
        welcomeText.className = 'welcomeText';
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
        logoutLink.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('[HEADER] Logout clicked - clearing storage and redirecting');
            
            // Show immediate feedback
            logoutLink.innerHTML = 'Logging<br>out...';
            logoutLink.style.pointerEvents = 'none';
            
            try {
                // Sign out from Supabase if available with timeout
                if (supabase) {
                    console.log('[HEADER] Signing out from Supabase...');
                    const signOutPromise = supabase.auth.signOut();
                    const timeoutPromise = new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Signout timeout')), 2000)
                    );
                    
                    await Promise.race([signOutPromise, timeoutPromise]);
                    console.log('[HEADER] Supabase signout completed');
                }
            } catch (error) {
                console.warn('[HEADER] Supabase signout error (continuing anyway):', error);
            }
            
            // Clear local storage
            console.log('[HEADER] Clearing storage...');
            localStorage.clear();
            sessionStorage.clear();
            
            // Immediate redirect without any delay
            console.log('[HEADER] Redirecting to login...');
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
    
    // Export function to refresh just the role switching
    window.refreshHeaderRole = function() {
        try {
            const roleElement = document.querySelector('#app-header .roleText');
            const welcomeElement = document.querySelector('#app-header .welcomeText');
            if (roleElement && welcomeElement) {
                loadUserDisplayName(welcomeElement, roleElement).catch(error => {
                    console.error('[HEADER] Failed to refresh user data:', error);
                });
            }
        } catch (error) {
            console.error('[HEADER] Role refresh error:', error);
        }
    };
    
    // Listen for page navigation changes
    window.addEventListener('popstate', function() {
        console.log('[HEADER] Page navigation detected, refreshing header');
        setTimeout(() => {
            const roleElement = document.querySelector('#app-header .roleText');
            const welcomeElement = document.querySelector('#app-header .welcomeText');
            if (roleElement && welcomeElement) {
                loadUserDisplayName(welcomeElement, roleElement).catch(error => {
                    console.error('[HEADER] Failed to refresh user data:', error);
                });
            }
        }, 100);
    });
    
    // Also listen for hash changes
    window.addEventListener('hashchange', function() {
        console.log('[HEADER] Hash change detected, refreshing header');
        setTimeout(() => {
            const roleElement = document.querySelector('#app-header .roleText');
            const welcomeElement = document.querySelector('#app-header .welcomeText');
            if (roleElement && welcomeElement) {
                loadUserDisplayName(welcomeElement, roleElement).catch(error => {
                    console.error('[HEADER] Failed to refresh user data:', error);
                });
            }
        }, 100);
    });
    
})();
