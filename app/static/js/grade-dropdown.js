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

function showSaveReminder() {
    let footer = document.getElementById('save-reminder-footer');
    if (!footer) {
        footer = document.createElement('div');
        footer.id = 'save-reminder-footer';
        footer.className = 'save-reminder show';
        footer.innerHTML = '⚠️ Changes detected. Please save ⚠️';
        document.body.appendChild(footer);
    }
}

function handleGradeChange(gradeSelect) {
    const row = gradeSelect.closest('tr');
    const secondarySelect = row.querySelector('.grade-secondary-select');
    const grade = gradeSelect.value;
    
    showSaveReminder();
    
    // Clear and reset secondary dropdown
    secondarySelect.innerHTML = '';
    
    if (!grade || grade === '') {
        secondarySelect.disabled = true;
        secondarySelect.innerHTML = '<option value="" disabled selected>Select Secondary Grade</option>';
        return;
    }
    
    if (grade === 'Neither satisfied nor dissatisfied') {
        secondarySelect.disabled = true;
        secondarySelect.innerHTML = '<option value="" disabled selected>N/A</option>';
        return;
    }
    
    secondarySelect.disabled = false;
    
    let options = [];
    if (grade === 'Very satisfied' || grade === 'Somewhat satisfied') {
        options = GRADE_SECONDARY_POS;
    } else if (grade === 'Somewhat dissatisfied' || grade === 'Very dissatisfied') {
        options = GRADE_SECONDARY_NEG;
    }
    
    secondarySelect.innerHTML = '<option value="" disabled selected>Select Secondary Grade</option>' +
        options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
}

function handleSecondaryGradeChange(secondarySelect) {
    const customerId = secondarySelect.dataset.customerId;
    const row = secondarySelect.closest('tr');
    const gradeSelect = row.querySelector('.grade-select');
    const grade = gradeSelect.value;
    const gradeSecondary = secondarySelect.value;
    
    showSaveReminder();
    
    console.log('Secondary grade changed:', { customerId, grade, gradeSecondary });
}

// Initialize on page load - set up any pre-selected grades
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.grade-select').forEach(select => {
        if (!select.disabled && select.value && select.value !== '') {
            const row = select.closest('tr');
            const secondarySelect = row.querySelector('.grade-secondary-select');
            const grade = select.value;
            
            // Manually populate secondary without triggering change
            secondarySelect.innerHTML = '';
            
            if (grade === 'Neither satisfied nor dissatisfied') {
                secondarySelect.disabled = true;
                secondarySelect.innerHTML = '<option value="" disabled selected>N/A</option>';
            } else {
                secondarySelect.disabled = false;
                
                let options = [];
                if (grade === 'Very satisfied' || grade === 'Somewhat satisfied') {
                    options = GRADE_SECONDARY_POS;
                } else if (grade === 'Somewhat dissatisfied' || grade === 'Very dissatisfied') {
                    options = GRADE_SECONDARY_NEG;
                }
                
                secondarySelect.innerHTML = '<option value="" disabled selected>Select Secondary Grade</option>' +
                    options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
                
                const savedSecondary = secondarySelect.dataset.savedValue;
                if (savedSecondary) {
                    secondarySelect.value = savedSecondary;
                }
            }
        }
    });
});
