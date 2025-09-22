from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Simple in-memory storage (in production, use a proper database)
notes = []
notes_file = 'notes.json'

# Load notes from file on startup
def load_notes():
    global notes
    if os.path.exists(notes_file):
        try:
            with open(notes_file, 'r') as f:
                notes = json.load(f)
        except json.JSONDecodeError:
            notes = []

# Save notes to file
def save_notes():
    with open(notes_file, 'w') as f:
        json.dump(notes, f, indent=2)

# Initialize notes
load_notes()

@app.route('/')
def home():
    """Serve a simple HTML interface for testing"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Note Taking App</title>
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
        <h1>Greg's Musings</h1>
        
        <div>
            <h2>Add New Note</h2>
            <input type="text" id="noteTitle" placeholder="Note title">
            <textarea id="noteContent" rows="4" placeholder="Note content"></textarea>
            <button onclick="addNote()">Add Note</button>
        </div>
        
        <div id="notesList">
            <h2>Your Notes</h2>
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
                        notesList.innerHTML = '<h2>Your Notes</h2>';
                        
                        notes.forEach(note => {
                            const noteDiv = document.createElement('div');
                            noteDiv.className = 'note';
                            noteDiv.innerHTML = `
                                <h3>${note.title}</h3>
                                <p>${note.content}</p>
                                <small>Created: ${new Date(note.created_at).toLocaleString()}</small>
                                <br><br>
                                <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
                            `;
                            notesList.appendChild(noteDiv);
                        });
                    })
                    .catch(error => console.error('Error loading notes:', error));
            }

            function addNote() {
                const title = document.getElementById('noteTitle').value;
                const content = document.getElementById('noteContent').value;
                
                if (!title || !content) {
                    alert('Please fill in both title and content');
                    return;
                }

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
                    }
                })
                .catch(error => console.error('Error adding note:', error));
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
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Generate simple ID
    note_id = len(notes) + 1 if notes else 1
    while any(note['id'] == note_id for note in notes):
        note_id += 1
    
    new_note = {
        'id': note_id,
        'title': data['title'],
        'content': data['content'],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    notes.append(new_note)
    save_notes()
    
    return jsonify({'success': True, 'note': new_note}), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    note = next((note for note in notes if note['id'] == note_id), None)
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return jsonify(note)

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    note = next((note for note in notes if note['id'] == note_id), None)
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        note['title'] = data['title']
    if 'content' in data:
        note['content'] = data['content']
    
    note['updated_at'] = datetime.now().isoformat()
    save_notes()
    
    return jsonify({'success': True, 'note': note})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    global notes
    original_length = len(notes)
    notes = [note for note in notes if note['id'] != note_id]
    
    if len(notes) == original_length:
        return jsonify({'error': 'Note not found'}), 404
    
    save_notes()
    return jsonify({'success': True, 'message': 'Note deleted'})

@app.route('/api/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    filtered_notes = [
        note for note in notes 
        if query in note['title'].lower() or query in note['content'].lower()
    ]
    
    return jsonify(filtered_notes)

if __name__ == '__main__':
    print("Starting Note-Taking Backend Server...")
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