from flask import Flask, request, jsonify, render_template, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3, uuid, datetime, hashlib
from datetime import timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    conn = sqlite3.connect('notess.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id TEXT PRIMARY KEY, encrypted_data TEXT, 
                  password_hash TEXT, expires_at INTEGER, 
                  read_once BOOLEAN, created_at INTEGER)''')
    conn.commit()
    conn.close()

def delete_note(note_id):
    conn = sqlite3.connect('notess.db')
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<note_id>')
def editor(note_id):
    """Handles BOTH new notes and existing: /abc12345"""
    # Validate note_id format (8 chars alphanumeric)
    if len(note_id) < 3 or not note_id.isalnum():
        return "Invalid note ID", 404
    
    conn = sqlite3.connect('notess.db')
    c = conn.cursor()
    c.execute("SELECT encrypted_data FROM notes WHERE id=?", (note_id,))
    result = c.fetchone()
    conn.close()
    print(result,"-------------------")
    existing_content = ""
    if result:
        existing_content = "✅ Note loaded and synced across all tabs!"
    
    return render_template('editor.html', note_id=note_id, existing_content=existing_content)



# @socketio.on('join_note')
# def on_join(data):
#     note_id = data['note_id']
#     join_room(note_id)
#     emit('status', {'msg': f'User joined {note_id}'}, room=note_id)

@socketio.on('join_note')
def on_join(data):
    print(f"🔗 JOIN: {data}")  # Terminal check
    note_id = data['note_id']
    join_room(note_id)
    emit('status', {'msg': f'User joined {note_id}'}, room=note_id)

@socketio.on('text_change')
def handle_text_change(data):
    print(f"📝 CHANGE: {data['note_id'][:10]}...") 
    print("getiiiiiiiii----***",data)
    note_id = data['note_id']
    content = data['content']
    password = data.get('password', '')
    
    # Save to DB
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
    conn = sqlite3.connect('notess.db')
    c = conn.cursor()
    expires_at = int((datetime.datetime.now() + timedelta(hours=24)).timestamp())
    c.execute("""INSERT OR REPLACE INTO notes VALUES (?, ?, ?, ?, ?, ?)""",
              (note_id, content, password_hash, expires_at, False, int(datetime.datetime.now().timestamp())))
    conn.commit()
    conn.close()
    
    # Broadcast to all tabs in real-time
    emit('text_update', {'content': content}, room=note_id)

@app.route('/new')
def create_new():
    """Generate unique note URL"""
    unique_id = str(uuid.uuid4())[:8]
    return render_template('editor.html', note_id=unique_id, existing_content="")



if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
