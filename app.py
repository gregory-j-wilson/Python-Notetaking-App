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
            body { font-family: Arial, sans-serif; margin: 40px; }
            .note { border: 1px solid #ccc; margin: 10px 0; padding: 15px; border-radius: 5px; }
            .note h3 { margin-top: 0; color: #333; }
            textarea, input { width: 100%; padding: 8px; margin: 5px 0; }
            button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .delete-btn { background: #dc3545; }
            .delete-btn:hover { background: #c82333; }
        </style>
    </head>
    <body>
        <h1>Note Taking App</h1>
        
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
    print("Visit http://localhost:5000 for the web interface")
    print("API endpoints:")
    print("  GET    /api/notes          - Get all notes")
    print("  POST   /api/notes          - Create new note")
    print("  GET    /api/notes/<id>     - Get specific note")
    print("  PUT    /api/notes/<id>     - Update note")
    print("  DELETE /api/notes/<id>     - Delete note")
    print("  GET    /api/notes/search?q=query - Search notes")
    
    app.run(debug=True, host='0.0.0.0', port=5000)