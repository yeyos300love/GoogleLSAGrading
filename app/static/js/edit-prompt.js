const PROMPT_GET_URL = '/get-prompt';
const PROMPT_SAVE_URL = '/save-prompt';

function openPromptModal() {
    const modal = document.getElementById('promptModal');
    const promptText = document.getElementById('promptText');
    const editButton = document.getElementById('editButton');
    const promptForm = document.getElementById('promptForm');
    
    fetch(PROMPT_GET_URL)
        .then(r => r.json())
        .then(data => {
            // Clear previous content
            promptText.innerHTML = '';
            
            // Create editable section
            const editableDiv = document.createElement('div');
            editableDiv.contentEditable = 'true';
            editableDiv.textContent = data.prompt.trim();
            editableDiv.style.outline = 'none';
            editableDiv.style.display = 'inline';
            
            // Create uneditable footer
            const footerDiv = document.createElement('div');
            footerDiv.contentEditable = 'false';
            footerDiv.style.color = '#9ca3af';
            footerDiv.style.userSelect = 'none';
            footerDiv.style.outline = 'none';
            footerDiv.style.display = 'inline';
            footerDiv.textContent = '\n\nUse this transcript:\n{transcript}';
            
            // Append both to promptText
            promptText.appendChild(editableDiv);
            promptText.appendChild(footerDiv);
            
            // Start in edit mode
            promptText.contentEditable = false;
            editButton.style.display = 'none';
            promptForm.style.display = 'flex';
            modal.classList.add('editing');
            
            modal.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Focus editable section
            editableDiv.focus();
        });
}

function closePromptModal() {
    const modal = document.getElementById('promptModal');
    const promptText = document.getElementById('promptText');
    const editButton = document.getElementById('editButton');
    const promptForm = document.getElementById('promptForm');
    
    promptText.contentEditable = false;
    editButton.style.display = 'flex';
    promptForm.style.display = 'none';
    
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
}

function enablePromptEdit() {
    const promptText = document.getElementById('promptText');
    const editButton = document.getElementById('editButton');
    const promptForm = document.getElementById('promptForm');
    const modal = document.getElementById('promptModal');
    
    promptText.contentEditable = true;
    promptText.focus();
    
    editButton.style.display = 'none';
    promptForm.style.display = 'flex';
    modal.classList.add('editing');
}

function savePrompt(event) {
    event.preventDefault();
    const editableDiv = document.querySelector('#promptText div[contenteditable="true"]');
    const promptText = editableDiv.textContent;
    const formData = new FormData();
    formData.append('prompt', promptText);
    
    fetch(PROMPT_SAVE_URL, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            closePromptModal();
            alert('Prompt saved successfully!');
        }
    });
}
