// Get job info from window (set in HTML)
const jobId = window.jobId;

//console.log(jobId, "YES IT WORKED");

function submit2FA() {
    const code = document.getElementById('tfa-code').value;
    
    if (code.length !== 6) {
        //document.getElementById('tfa-error').textContent = 'Code must be 6 digits';
        //document.getElementById('tfa-error').style.display = 'block';
        return;
    }
    
    // Send code to backend
    fetch(`/${jobId}/submit-2fa`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: code})
    })
    .then(response => response.json())
    .then(data => {
       if (data.success) {         
            // Redirect to your loading page
            window.location.href = `/${jobId}/loading?action=fetch-transcripts`;
        }
    })
}

// Allow Enter key to submit
document.getElementById('tfa-code').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        submit2FA();
    }
});
