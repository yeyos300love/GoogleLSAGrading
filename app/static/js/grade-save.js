function collectGrades(form) {
    const updates = [];
    
    // Collect all rows with grade data
    document.querySelectorAll('tbody tr').forEach(row => {
        const phone = row.querySelector('td:first-child').textContent.trim();
        const gradeSelect = row.querySelector('.grade-select');
        const secondarySelect = row.querySelector('.grade-secondary-select');
        
        // Only include if grade is selected
        if (gradeSelect && gradeSelect.value) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'updates';
            input.value = JSON.stringify({
                phone: phone,
                grade: gradeSelect.value,
                grade_secondary: secondarySelect && secondarySelect.value ? secondarySelect.value : null
            });
            form.appendChild(input);
        }
    });
    
    return true; // Allow form to submit
}
