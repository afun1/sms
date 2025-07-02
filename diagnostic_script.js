// Quick diagnostic script for contacts page
// Run this in browser console on the contacts page

console.log('=== CONTACTS PAGE DIAGNOSTIC ===');

// Check if key functions exist
const functions = [
    'handleFileSelect', 'loadContacts', 'renderContacts', 
    'handleAdd', 'handleDelete', 'handleAssign', 'handleImport', 'handleExport'
];

console.log('Function availability check:');
functions.forEach(func => {
    if (typeof window[func] === 'function') {
        console.log(`✓ ${func} is defined`);
    } else {
        console.error(`✗ ${func} is NOT defined`);
    }
});

// Check if Supabase is working
if (typeof supabase !== 'undefined') {
    console.log('✓ Supabase client is available');
    
    // Test connection
    supabase.from('contacts').select('count', { count: 'exact', head: true })
        .then(result => {
            if (result.error) {
                console.error('✗ Supabase connection failed:', result.error.message);
            } else {
                console.log('✓ Supabase connection working');
            }
        });
} else {
    console.error('✗ Supabase client not available');
}

// Check key DOM elements
const elements = ['contacts-tbody', 'delete-btn', 'add-btn', 'search-input'];
console.log('DOM elements check:');
elements.forEach(id => {
    if (document.getElementById(id)) {
        console.log(`✓ Element ${id} found`);
    } else {
        console.error(`✗ Element ${id} missing`);
    }
});

console.log('=== DIAGNOSTIC COMPLETE ===');
console.log('If you see any ✗ errors above, those need to be fixed.');
console.log('If all ✓ green, the page should work correctly!');
