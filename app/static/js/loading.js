// Get job info from window (set in HTML)
const jobId = window.jobId;
const action = window.action;

const eventSource = new EventSource(`/${jobId}/analyze-all-stream`);

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.message) {
        document.getElementById('progress-message').textContent = data.message;
    }
    
    if (data.done) {
        eventSource.close();
        
        document.getElementById('progress-message').textContent = 'Analysis complete! Redirecting...';
        
        setTimeout(() => {
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = `/jobs/${jobId}`;
            }
        }, 1000);
    }
};

eventSource.onerror = function(error) {
    console.error('EventSource error:', error);
    eventSource.close();
    document.getElementById('progress-message').textContent = 'An error occurred. Redirecting...';
    setTimeout(() => {
        window.location.href = `/job/${jobId}`;
    }, 2000);
};
