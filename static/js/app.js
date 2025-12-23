let currentNoteId = null;
let encryptedData = '';
let saveTimeout;

const textarea = document.getElementById('note');
const passwordInput = document.getElementById('password');
const readOnce = document.getElementById('readOnce');
const shareUrl = document.getElementById('shareUrl');

// Auto-save every 2 seconds
textarea.addEventListener('input', function() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(autoSave, 2000);
});

function encryptNote(content, password) {
    const key = password ? CryptoJS.SHA256(password).toString() : CryptoJS.lib.WordArray.random(32);
    return CryptoJS.AES.encrypt(content, key).toString();
}

async function autoSave() {
    if (currentNoteId) {
        const password = passwordInput.value;
        const content = textarea.value;
        encryptedData = encryptNote(content, password);
        
        await fetch(`/api/save`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                encrypted_data: encryptedData,
                password: password,
                read_once: readOnce.checked
            })
        });
    }
}

async function saveNote() {
    const content = textarea.value;
    if (!content.trim()) return;
    
    const password = passwordInput.value;
    encryptedData = encryptNote(content, password);
    
    const response = await fetch('/api/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            encrypted_data: encryptedData,
            password: password,
            read_once: readOnce.checked
        })
    });
    
    const data = await response.json();
    currentNoteId = data.id;
    shareUrl.innerHTML = `<strong>Share: </strong><a href="/note/${data.id}" target="_blank">${window.location.origin}/note/${data.id}</a>`;
}
