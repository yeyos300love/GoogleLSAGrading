/**
 * Grade dropdown logic with cascading secondary grade options
 */

const GRADE_SECONDARY_POS = [
    "Booked",
    "Could convert to a booked client",
    "Relevant",
    "High value to the business",
    "Other"
];

const GRADE_SECONDARY_NEG = [
    "Outside service area",
    "Service not offered",
    "Not ready to book services",
    "Spam/Robocall",
    "Duplicate lead",
    "Employment/Sales Pitch",
    "Other"
];

function handleGradeChange(gradeSelect) {
    const row = gradeSelect.closest('tr');
    const secondarySelect = row.querySelector('.grade-secondary-select');
    const grade = gradeSelect.value;
    
    // Clear and reset secondary dropdown
    secondarySelect.innerHTML = '';
    
    if (!grade || grade === '') {
        // No grade selected - disable and show placeholder
        secondarySelect.disabled = true;
        secondarySelect.innerHTML = '<option value="" disabled selected>Select Secondary Grade</option>';
        return;
    }
    
    if (grade === 'Neither satisfied nor dissatisfied') {
        // Neutral grade - disable and show N/A
        secondarySelect.disabled = true;
        secondarySelect.innerHTML = '<option value="" disabled selected>N/A</option>';
        return;
    }
    
    // Enable dropdown
    secondarySelect.disabled = false;
    
    // Determine which options to show
    let options = [];
    if (grade === 'Very satisfied' || grade === 'Somewhat satisfied') {
        options = GRADE_SECONDARY_POS;
    } else if (grade === 'Somewhat dissatisfied' || grade === 'Very dissatisfied') {
        options = GRADE_SECONDARY_NEG;
    }
    
    // Build dropdown options
    secondarySelect.innerHTML = '<option value="" disabled selected>Select Secondary Grade</option>' +
        options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
}

function handleSecondaryGradeChange(secondarySelect) {
    const customerId = secondarySelect.dataset.customerId;
    const row = secondarySelect.closest('tr');
    const gradeSelect = row.querySelector('.grade-select');
    const grade = gradeSelect.value;
    const gradeSecondary = secondarySelect.value;
    
    console.log('Secondary grade changed:', { customerId, grade, gradeSecondary });
    // Database save will be handled by save button later
}

// Initialize on page load - set up any pre-selected grades
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.grade-select').forEach(select => {
        // If a grade is already selected, trigger the cascade
        if (!select.disabled && select.value && select.value !== '') {
            handleGradeChange(select);
            
            // Restore the secondary selection if it exists
            const row = select.closest('tr');
            const secondarySelect = row.querySelector('.grade-secondary-select');
            const savedSecondary = secondarySelect.dataset.savedValue;
            
            if (savedSecondary) {
                // Wait a tick for options to populate
                setTimeout(() => {
                    secondarySelect.value = savedSecondary;
                }, 0);
            }
        }
    });
});
