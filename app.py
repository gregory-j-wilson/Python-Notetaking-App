from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Get database connection"""
    if DATABASE_URL:
        # Production: Use Render's PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
    else:
        # Development: Use SQLite fallback
        import sqlite3
        conn = sqlite3.connect('notes.db')
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL setup
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
        conn.commit()
    else:
        # SQLite setup for development
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.commit()
    
    conn.close()

# Initialize database
init_db()

@app.route('/')
def home():
    """Serve a simple HTML interface for testing"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Note Taking App</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                box-sizing: border-box;
            }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                line-height: 1.6;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
                font-weight: 600;
            }
            
            h2 {
                color: #444;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
                margin-top: 40px;
            }
            
            .add-note-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 30px;
                border: 1px solid #e9ecef;
            }
            
            .note { 
                border: 1px solid #ddd; 
                margin: 15px 0; 
                padding: 20px; 
                border-radius: 8px; 
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: box-shadow 0.2s ease;
            }
            
            .note:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .note h3 { 
                margin-top: 0; 
                color: #333; 
                font-weight: 600;
                word-wrap: break-word;
            }
            
            .note p {
                color: #666;
                margin: 10px 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .note small {
                color: #888;
                font-size: 0.9em;
            }
            
            textarea, input[type="text"] { 
                width: 100%; 
                padding: 12px; 
                margin: 8px 0; 
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: inherit;
                font-size: 14px;
                transition: border-color 0.2s ease;
                resize: vertical;
            }
            
            textarea:focus, input[type="text"]:focus {
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
            }
            
            textarea {
                min-height: 100px;
                font-family: inherit;
            }
            
            button { 
                background: #007bff; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 6px; 
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s ease;
                margin-right: 10px;
                margin-top: 10px;
            }
            
            button:hover { 
                background: #0056b3; 
                transform: translateY(-1px);
            }
            
            .delete-btn { 
                background: #dc3545; 
            }
            
            .delete-btn:hover { 
                background: #c82333; 
            }
            
            .note-actions {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            
            .empty-state {
                text-align: center;
                color: #666;
                padding: 40px 20px;
                font-style: italic;
            }
            
            /* Mobile Responsive Design */
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }
                
                .container {
                    padding: 20px;
                    margin: 0 10px;
                }
                
                h1 {
                    font-size: 1.8em;
                    margin-bottom: 20px;
                }
                
                h2 {
                    font-size: 1.3em;
                    margin-top: 25px;
                }
                
                .add-note-section {
                    padding: 15px;
                }
                
                .note {
                    padding: 15px;
                    margin: 10px 0;
                }
                
                textarea, input[type="text"] {
                    padding: 10px;
                    font-size: 16px; /* Prevents zoom on iOS */
                }
                
                button {
                    padding: 10px 16px;
                    margin-right: 5px;
                    margin-bottom: 5px;
                    width: auto;
                    min-width: 80px;
                }
            }
            
            /* Small mobile devices */
            @media (max-width: 480px) {
                .container {
                    margin: 0;
                    border-radius: 0;
                    min-height: 100vh;
                    padding: 15px;
                }
                
                .add-note-section {
                    padding: 12px;
                    margin-bottom: 20px;
                }
                
                .note {
                    padding: 12px;
                }
                
                button {
                    font-size: 13px;
                    padding: 8px 12px;
                }
                
                h1 {
                    font-size: 1.5em;
                }
            }
            
            /* Tablet landscape and small desktop */
            @media (min-width: 769px) and (max-width: 1024px) {
                .container {
                    padding: 35px;
                }
            }
            
            /* Large desktop */
            @media (min-width: 1200px) {
                .container {
                    max-width: 900px;
                    padding: 40px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Greg's Musings</h1>
            
            <div class="add-note-section">
                <h2>✏️ Add New Note</h2>
                <input type="text" id="noteTitle" placeholder="Enter note title...">
                <textarea id="noteContent" rows="4" placeholder="Write your note content here..."></textarea>
                <button onclick="addNote()">Add Note</button>
            </div>
            
            <div id="notesList">
                <h2>📚 Your Notes</h2>
                <div class="empty-state" id="emptyState">
                    No notes yet. Create your first note above! 
                </div>
            </div>
        </div>

        <script>
            // Load notes when page loads
            window.onload = function() {
                loadNotes();
            }

            function loadNotes() {
                fetch('/api/notes')
                    .then(response => response.json())
                    .then(notes => {
                        const notesList = document.getElementById('notesList');
                        const emptyState = document.getElementById('emptyState');
                        
                        if (notes.length === 0) {
                            notesList.innerHTML = '<h2>📚 Your Notes</h2><div class="empty-state">No notes yet. Create your first note above!</div>';
                            return;
                        }
                        
                        notesList.innerHTML = '<h2>📚 Your Notes</h2>';
                        
                        notes.forEach(note => {
                            const noteDiv = document.createElement('div');
                            noteDiv.className = 'note';
                            noteDiv.innerHTML = `
                                <h3>${escapeHtml(note.title)}</h3>
                                <p>${escapeHtml(note.content)}</p>
                                <small>Created: ${new Date(note.created_at).toLocaleString()}</small>
                                <div class="note-actions">
                                    <button class="delete-btn" onclick="deleteNote(${note.id})">🗑️ Delete</button>
                                </div>
                            `;
                            notesList.appendChild(noteDiv);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading notes:', error);
                        alert('Error loading notes. Please try again.');
                    });
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            function addNote() {
                const title = document.getElementById('noteTitle').value.trim();
                const content = document.getElementById('noteContent').value.trim();
                
                if (!title || !content) {
                    alert('Please fill in both title and content');
                    return;
                }

                // Disable button during request
                const addButton = event.target;
                addButton.disabled = true;
                addButton.textContent = 'Adding...';

                fetch('/api/notes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        content: content
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('noteTitle').value = '';
                        document.getElementById('noteContent').value = '';
                        loadNotes();
                    } else {
                        alert('Error adding note: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error adding note:', error);
                    alert('Error adding note. Please try again.');
                })
                .finally(() => {
                    addButton.disabled = false;
                    addButton.textContent = 'Add Note';
                });
            }

            function deleteNote(noteId) {
                if (confirm('Are you sure you want to delete this note?')) {
                    fetch(`/api/notes/${noteId}`, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadNotes();
                        }
                    })
                    .catch(error => console.error('Error deleting note:', error));
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM notes ORDER BY created_at DESC')
            notes = cursor.fetchall()
    else:
        # SQLite
        notes = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
        notes = [dict(note) for note in notes]
    
    conn.close()
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    now = datetime.now()
    conn = get_db_connection()
    
    try:
        if DATABASE_URL:
            # PostgreSQL
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    'INSERT INTO notes (title, content, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING *',
                    (data['title'], data['content'], now, now)
                )
                note = cursor.fetchone()
                conn.commit()
        else:
            # SQLite
            cursor = conn.execute(
                'INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)',
                (data['title'], data['content'], now.isoformat(), now.isoformat())
            )
            note_id = cursor.lastrowid
            conn.commit()
            note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            note = dict(note)
        
        conn.close()
        return jsonify({'success': True, 'note': dict(note)}), 201
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM notes WHERE id = %s', (note_id,))
            note = cursor.fetchone()
    else:
        # SQLite
        note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
        if note:
            note = dict(note)
    
    conn.close()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return jsonify(dict(note))

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    conn = get_db_connection()
    data = request.get_json()
    now = datetime.now()
    
    try:
        if DATABASE_URL:
            # PostgreSQL
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Check if note exists
                cursor.execute('SELECT * FROM notes WHERE id = %s', (note_id,))
                existing_note = cursor.fetchone()
                
                if not existing_note:
                    conn.close()
                    return jsonify({'error': 'Note not found'}), 404
                
                title = data.get('title', existing_note['title'])
                content = data.get('content', existing_note['content'])
                
                cursor.execute(
                    'UPDATE notes SET title = %s, content = %s, updated_at = %s WHERE id = %s RETURNING *',
                    (title, content, now, note_id)
                )
                note = cursor.fetchone()
                conn.commit()
        else:
            # SQLite
            existing_note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            
            if not existing_note:
                conn.close()
                return jsonify({'error': 'Note not found'}), 404
            
            title = data.get('title', existing_note['title'])
            content = data.get('content', existing_note['content'])
            
            conn.execute(
                'UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?',
                (title, content, now.isoformat(), note_id)
            )
            conn.commit()
            note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            note = dict(note)
        
        conn.close()
        return jsonify({'success': True, 'note': dict(note)})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    conn = get_db_connection()
    
    try:
        if DATABASE_URL:
            # PostgreSQL
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM notes WHERE id = %s', (note_id,))
                if cursor.rowcount == 0:
                    conn.close()
                    return jsonify({'error': 'Note not found'}), 404
                conn.commit()
        else:
            # SQLite
            cursor = conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'error': 'Note not found'}), 404
            conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Note deleted'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL (case-insensitive search)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM notes WHERE title ILIKE %s OR content ILIKE %s ORDER BY created_at DESC',
                (f'%{query}%', f'%{query}%')
            )
            notes = cursor.fetchall()
    else:
        # SQLite
        notes = conn.execute(
            'SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC',
            (f'%{query}%', f'%{query}%')
        ).fetchall()
        notes = [dict(note) for note in notes]
    
    conn.close()
    return jsonify(notes)

if __name__ == '__main__':
    print("Starting Note-Taking Backend Server...")
    if DATABASE_URL:
        print("✅ Using PostgreSQL database")
    else:
        print("⚠️  Using SQLite fallback (development mode)")
    
    print("API endpoints:")
    print("  GET    /api/notes          - Get all notes")
    print("  POST   /api/notes          - Create new note")
    print("  GET    /api/notes/<id>     - Get specific note")
    print("  PUT    /api/notes/<id>     - Update note")
    print("  DELETE /api/notes/<id>     - Delete note")
    print("  GET    /api/notes/search?q=query - Search notes")
    
    # Get port from environment variable (Render provides this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)