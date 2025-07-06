        function filterUsersForSupervisor(allUsers, currentUserId) {
            console.log('🎯 Filtering users for supervisor view');
            console.log('🔍 Current supervisor ID:', currentUserId);
            console.log('🔍 Total users available:', allUsers.length);
            
            const visibleUsers = [];
            
            // Add ONLY unassigned admins (admins with no supervisor_id or manager_id)
            const unassignedAdmins = allUsers.filter(user =>
                ((user.role && user.role.toLowerCase() === 'admin') ||
                 (user.secondary_role && user.secondary_role.toLowerCase() === 'admin')) &&
                !user.supervisor_id && !user.manager_id
            );
            visibleUsers.push(...unassignedAdmins);
            console.log('👑 Added unassigned admins to supervisor view:', unassignedAdmins.length, unassignedAdmins.map(a => a.email));
            
            // Add ONLY the current supervisor themselves (not other supervisors)
            const currentSupervisor = allUsers.find(user => user.id === currentUserId);
            if (currentSupervisor) {
                visibleUsers.push(currentSupervisor);
                console.log('👤 Added current supervisor themselves:', currentSupervisor.email, 'ID:', currentSupervisor.id);
            } else {
                console.warn('⚠️ Current supervisor not found in user list! Looking for ID:', currentUserId);
                console.log('📋 Available user IDs:', allUsers.map(u => ({ id: u.id, email: u.email, role: u.role })));
            }
            
            // Add all users (including admins) assigned directly to this supervisor
            const usersUnderSupervisor = allUsers.filter(user =>
                user.supervisor_id === currentUserId &&
                user.role && user.role.toLowerCase() !== 'manager' // Exclude managers, they have their own section
            );
            visibleUsers.push(...usersUnderSupervisor);
            console.log('👥 Added users/admins directly assigned to supervisor:', usersUnderSupervisor.length, usersUnderSupervisor.map(u => `${u.email} (${u.role})`));
            
            // Find managers (including admins with manager role) assigned to this supervisor
            const managersUnderSupervisor = allUsers.filter(user => 
                user.supervisor_id === currentUserId &&
                user.role && user.role.toLowerCase() === 'manager'
            );
            visibleUsers.push(...managersUnderSupervisor);
            console.log('👔 Added managers assigned to supervisor:', managersUnderSupervisor.length, managersUnderSupervisor.map(m => `${m.email} (${m.role})`));
            
            // Find users (including admins) under those managers
            const managerIds = managersUnderSupervisor.map(m => m.id);
            const usersUnderManagers = allUsers.filter(user =>
                managerIds.includes(user.manager_id)
            );
            visibleUsers.push(...usersUnderManagers);
            console.log('👤 Added users/admins under assigned managers:', usersUnderManagers.length, usersUnderManagers.map(u => `${u.email} (${u.role})`));
            
            // Remove duplicates by creating a Set based on user IDs
            const uniqueVisibleUsers = visibleUsers.filter((user, index, self) => 
                index === self.findIndex(u => u.id === user.id)
            );
            
            console.log('🔍 Supervisor can see:', uniqueVisibleUsers.length, 'users total');
            return uniqueVisibleUsers;
        }
