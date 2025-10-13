// Get job info from window (set in HTML)
const jobId = window.jobId;

//console.log(jobId, "YES IT WORKED");

function submitTuring() {
    // Simply redirect to the loading page which will trigger the stream
    window.location.href = `/${jobId}/loading?action=form-completion`;
}

