/**
 * Transcript modal functions
 */

function showTranscript(buttonElement) { 
    const modal = document.getElementById('transcriptModal');
    const transcriptText = document.getElementById('transcriptText');
    const modalTitle = document.getElementById('modalTitle');
    
    // Get data from button attributes
    const transcript = buttonElement.dataset.transcript;
    const phoneNumber = buttonElement.dataset.phone;
    
    // Remove active class from all buttons
    document.querySelectorAll('.view-transcript-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Remove highlight from all rows
    document.querySelectorAll('tr.viewing-transcript').forEach(row => {
        row.classList.remove('viewing-transcript');
    });
    
    // Add active class to the clicked button
    buttonElement.classList.add('active');

    // Highlight the row
    const row = buttonElement.closest('tr');
    row.classList.add('viewing-transcript');
    
    // Display the transcript
    transcriptText.textContent = transcript;
    
    // Update title based on transcript type
    const isFailure = transcript.trim().startsWith('FAILED');
    const isWarning = transcript.trim().startsWith('WARNING');
    let status = 'Latest Call';
    if (isFailure) status = 'Failed';
    if (isWarning) status = 'Warning';
    
    modalTitle.textContent = `${phoneNumber} - ${status}`;
    
    // show modal
    modal.classList.add('show');
    document.body.classList.add('modal-open');
}

function closeTranscript() {
    const modal = document.getElementById('transcriptModal');
    const transcriptText = document.getElementById('transcriptText');
    const editButton = document.getElementById('editButton');
    const saveForm = document.getElementById('transcriptForm');

    // Remove active class from all buttons (both view and add)
    document.querySelectorAll('.view-transcript-btn, .add-transcript-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Remove highlight from any row
    document.querySelectorAll('tr.viewing-transcript').forEach(row => {
        row.classList.remove('viewing-transcript');
    });

    // Reset edit state
    transcriptText.contentEditable = false;
    editButton.style.display = 'flex';
    saveForm.style.display = 'none';

    // Hide modal
    modal.classList.remove('show');
    document.body.classList.remove('modal-open'); // Add this line!
}

function copyTranscript() {
    const text = document.getElementById('transcriptText').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const copyButton = document.querySelector('.copy-button');
        copyButton.classList.add('copied');
        setTimeout(() => copyButton.classList.remove('copied'), 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Click outside modal to close
document.addEventListener('click', function(event) {
    const modal = document.getElementById('transcriptModal');

    // Only trigger if modal is open
    if (!modal.classList.contains('show')) return;

    // Do NOT close if clicking a transcript button (view or add)
    if (event.target.closest('.view-transcript-btn, .add-transcript-btn')) return;

    // Close only if click is outside the modal
    if (!modal.contains(event.target)) {
        closeTranscript();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('transcriptModal');
        if (modal.classList.contains('show')) {
            closeTranscript();
        }
    }
});

function enableEdit() {
    const transcriptText = document.getElementById('transcriptText');
    const editButton = document.getElementById('editButton');
    const saveForm = document.getElementById('transcriptForm');
    
    transcriptText.contentEditable = true;
    transcriptText.focus();
    
    editButton.style.display = 'none';
    saveForm.style.display = 'flex';
}

function saveTranscript(event) {
    if (event) event.preventDefault();
    
    const transcriptText = document.getElementById('transcriptText');
    const activeButton = document.querySelector('.view-transcript-btn.active, .add-transcript-btn.active');
    
    if (!activeButton) return;
    
    document.getElementById('transcriptPhone').value = activeButton.dataset.phone;
    document.getElementById('transcriptContent').value = transcriptText.textContent;
    
    document.getElementById('transcriptForm').submit();
}
// Reopen modal after save
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const reopenPhone = urlParams.get('reopen');
    
    if (reopenPhone) {
        // Find the button with matching phone number (either view or add)
        const button = document.querySelector(`.view-transcript-btn[data-phone="${reopenPhone}"], .add-transcript-btn[data-phone="${reopenPhone}"]`);
        if (button) {
            if (button.classList.contains('add-transcript-btn')) {
                addTranscript(button);
            } else {
                showTranscript(button);
            }
        }
        
        // Clean up URL without reload
        window.history.replaceState({}, '', window.location.pathname);
    }
});

function addTranscript(buttonElement) {
    const modal = document.getElementById('transcriptModal');
    const transcriptText = document.getElementById('transcriptText');
    const modalTitle = document.getElementById('modalTitle');
    const editButton = document.getElementById('editButton');
    const saveForm = document.getElementById('transcriptForm');
    
    const phoneNumber = buttonElement.dataset.phone;
    
    // Remove active class from all buttons (both view and add)
    document.querySelectorAll('.view-transcript-btn, .add-transcript-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Remove highlight from all rows
    document.querySelectorAll('tr.viewing-transcript').forEach(row => {
        row.classList.remove('viewing-transcript');
    });
    
    // Add active class to the clicked button
    buttonElement.classList.add('active');

    // Highlight the row
    const row = buttonElement.closest('tr');
    row.classList.add('viewing-transcript');
    
    // Clear and set to edit mode
    transcriptText.textContent = '';
    transcriptText.contentEditable = true;
    transcriptText.focus();
    
    // Hide edit button, show save form
    editButton.style.display = 'none';
    saveForm.style.display = 'flex';
    
    // Update title
    modalTitle.textContent = `${phoneNumber} - Add Transcript`;
    
    // Show modal
    modal.classList.add('show');
    document.body.classList.add('modal-open');
}

