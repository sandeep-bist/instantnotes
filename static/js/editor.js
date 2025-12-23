document.addEventListener('DOMContentLoaded', function() {
    const noteId = window.noteId;
    const textarea = document.getElementById('note');
    const status = document.getElementById('status');
    
    // Update share URL
    document.querySelector('.share-url').textContent = `${window.hostUrl}${noteId}`;
    
    // Socket.IO connection
    const socket = io();
    
    // Join room
    socket.emit('join_note', { note_id: noteId });
    
    // Real-time updates from other users
    socket.on('text_update', function(data) {
        if (data.content !== textarea.value) {
            textarea.value = data.content;
        }
    });
    
    // Send changes instantly (debounced)
    let timeout;
    textarea.addEventListener('input', function() {
        clearTimeout(timeout);
        const content = textarea.value;
        
        timeout = setTimeout(() => {
            socket.emit('text_change', {
                note_id: noteId,
                content: content,
                password: document.getElementById('password').value
            });
        }, 100); // 100ms debounce
    });
    
    window.copyUrl = function() {
        const url = document.querySelector('.share-url').textContent;
        navigator.clipboard.writeText(url).then(() => {
            alert('✅ URL copied! Share with anyone - live editing!');
        });
    };
    
    // Connection status
    socket.on('connect', () => status.textContent = 'Connected ✓');
    socket.on('disconnect', () => status.textContent = 'Disconnected ✗');
});
