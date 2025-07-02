// JavaScript validation script for contacts_new.html
console.log('Starting validation of contacts page...');

// Check for required functions
const requiredFunctions = [
    'loadContacts',
    'renderContacts', 
    'handleAdd',
    'handleDelete',
    'handleAssign',
    'handleImport',
    'handleExport',
    'getSelectedContacts',
    'updateHeaderCheckboxAndDeleteButton',
    'showAlert',
    'handleFileSelect'
];

requiredFunctions.forEach(funcName => {
    if (typeof window[funcName] === 'function') {
        console.log(`✓ Function ${funcName} is defined`);
    } else {
        console.error(`✗ Function ${funcName} is missing`);
    }
});

// Check for required DOM elements
const requiredElements = [
    'contacts-table-body',
    'delete-btn', 
    'assign-btn',
    'add-btn',
    'import-btn',
    'export-btn',
    'search-input'
];

requiredElements.forEach(elementId => {
    const element = document.getElementById(elementId);
    if (element) {
        console.log(`✓ Element ${elementId} found`);
    } else {
        console.error(`✗ Element ${elementId} missing`);
    }
});

// Test Supabase connection
if (typeof supabase !== 'undefined') {
    console.log('✓ Supabase client is defined');
    
    // Test connection
    supabase.from('contacts').select('count').then(response => {
        if (response.error) {
            console.error('✗ Supabase connection failed:', response.error);
        } else {
            console.log('✓ Supabase connection successful');
        }
    });
} else {
    console.error('✗ Supabase client is not defined');
}

console.log('Validation complete.');
