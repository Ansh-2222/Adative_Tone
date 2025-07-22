from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
from database import db, create_user, get_user, update_user
from memory_manager import MemoryManager
from tone_engine import ToneEngine
import os

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing
CORS(app)

# --- SQLAlchemy Configuration ---
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = f"sqlite:///{os.path.join(project_dir, 'tone_system.db')}"
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# --- Create Database Tables ---
@app.before_request
def create_tables():
    # Use before_request instead of before_first_request which is deprecated
    # This function will run once before the first request
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True


# In-memory storage for session-based memory
user_memory_managers = {}

def get_memory_manager(user_id):
    """Retrieves or creates a MemoryManager for a user."""
    if user_id not in user_memory_managers:
        user_profile = get_user(user_id)
        user_memory_managers[user_id] = MemoryManager(user_id, user_profile)
    return user_memory_managers[user_id]

# --- MODIFIED: Updated HTML with new UI and fields ---
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive Tone AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #121212; }
        .chat-bubble { max-width: 75%; padding: 0.75rem 1rem; border-radius: 1.25rem; word-wrap: break-word; line-height: 1.5; }
        .chat-bubble.user { background-color: #6366f1; color: white; border-bottom-right-radius: 0.25rem; }
        .chat-bubble.ai { background-color: #374151; color: #e5e7eb; border-bottom-left-radius: 0.25rem; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1f2937; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        .form-select {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.5rem center;
            background-repeat: no-repeat;
            background-size: 1.5em 1.5em;
            padding-right: 2.5rem;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
        }
    </style>
</head>
<body class="text-gray-200 flex h-screen">

    <div class="w-1/3 bg-[#1f2937] p-6 flex flex-col h-full shadow-lg">
        <header class="mb-6">
            <h1 class="text-3xl font-bold text-white">Adaptive AI</h1>
            <p class="text-gray-400 mt-1">Fine-tune your AI's personality.</p>
        </header>

        <div class="flex-grow space-y-6">
            <h2 class="text-xl font-semibold border-b border-gray-600 pb-2 text-gray-300">User Configuration</h2>
            <div>
                <label for="user_id" class="block text-sm font-medium text-gray-400 mb-1">User ID</label>
                <input type="text" id="user_id" class="w-full bg-gray-800 border-gray-600 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 text-white" placeholder="e.g., user_alex">
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label for="formality" class="block text-sm font-medium text-gray-400 mb-1">Formality</label>
                    <select id="formality" class="form-select w-full bg-gray-800 border-gray-600 rounded-md shadow-sm p-2 text-white">
                        <option>casual</option>
                        <option selected>professional</option>
                        <option>formal</option>
                    </select>
                </div>
                <div>
                    <label for="enthusiasm" class="block text-sm font-medium text-gray-400 mb-1">Enthusiasm</label>
                    <select id="enthusiasm" class="form-select w-full bg-gray-800 border-gray-600 rounded-md shadow-sm p-2 text-white">
                        <option>low</option>
                        <option selected>medium</option>
                        <option>high</option>
                    </select>
                </div>
                <div>
                    <label for="verbosity" class="block text-sm font-medium text-gray-400 mb-1">Verbosity</label>
                    <select id="verbosity" class="form-select w-full bg-gray-800 border-gray-600 rounded-md shadow-sm p-2 text-white">
                        <option>concise</option>
                        <option selected>balanced</option>
                        <option>detailed</option>
                    </select>
                </div>
                 <div>
                    <label for="persona" class="block text-sm font-medium text-gray-400 mb-1">Persona</label>
                    <select id="persona" class="form-select w-full bg-gray-800 border-gray-600 rounded-md shadow-sm p-2 text-white">
                        <option>neutral</option>
                        <option>friendly</option>
                        <option>witty</option>
                        <option>professional</option>
                    </select>
                </div>
                 <div>
                    <label for="humor" class="block text-sm font-medium text-gray-400 mb-1">Humor</label>
                    <select id="humor" class="form-select w-full bg-gray-800 border-gray-600 rounded-md shadow-sm p-2 text-white">
                        <option>none</option>
                        <option>punny</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="mt-auto">
            <button onclick="createProfile()" class="w-full bg-indigo-600 text-white py-2.5 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-indigo-500 transition-all font-semibold">
                Set Profile & Start Chat
            </button>
            <p id="profile_status" class="text-sm text-center mt-3"></p>
        </div>
    </div>

    <div class="w-2/3 flex flex-col h-full bg-[#121212]">
        <div id="chat_window" class="flex-grow p-6 overflow-y-auto flex flex-col space-y-4">
            <div id="welcome_message_container" class="flex justify-center items-center h-full">
                <p class="text-gray-500">Please set a User ID to begin your session.</p>
            </div>
        </div>
        <div class="p-4 bg-transparent border-t border-gray-800">
            <div class="flex items-center bg-[#1f2937] rounded-lg p-2">
                <input type="text" id="message_input" class="flex-grow bg-transparent text-white placeholder-gray-500 focus:outline-none px-2" placeholder="Type your message..." disabled>
                <button onclick="sendMessage()" id="send_button" class="bg-indigo-600 text-white p-2 rounded-md hover:bg-indigo-700 focus:outline-none disabled:bg-gray-600 disabled:cursor-not-allowed" disabled>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        const API_URL = 'http://127.0.0.1:5000';

        async function createProfile() {
            const userId = document.getElementById('user_id').value;
            const formality = document.getElementById('formality').value;
            const enthusiasm = document.getElementById('enthusiasm').value;
            const verbosity = document.getElementById('verbosity').value;
            // --- NEW: Get values from new dropdowns ---
            const persona = document.getElementById('persona').value;
            const humor = document.getElementById('humor').value;
            const profileStatus = document.getElementById('profile_status');

            if (!userId) {
                profileStatus.textContent = 'User ID cannot be empty.';
                profileStatus.className = 'text-sm text-center text-red-500 mt-3';
                return;
            }

            const profileData = {
                user_id: userId,
                preferences: {
                    // --- MODIFIED: Include new attributes in the payload ---
                    tone_preferences: { formality, enthusiasm, verbosity, persona, humor },
                    communication_style: { technical_level: "intermediate" }
                }
            };

            try {
                const response = await fetch(`${API_URL}/api/profile`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(profileData)
                });
                const result = await response.json();
                profileStatus.textContent = result.message;
                profileStatus.className = 'text-sm text-center text-green-500 mt-3';
                
                document.getElementById('message_input').disabled = false;
                document.getElementById('send_button').disabled = false;
                document.getElementById('welcome_message_container').innerHTML = '<p class="text-gray-500">You can now chat with the AI.</p>';
            } catch (error) {
                profileStatus.textContent = 'Error creating profile.';
                profileStatus.className = 'text-sm text-center text-red-500 mt-3';
                console.error('Profile creation error:', error);
            }
        }

        async function sendMessage() {
            const userId = document.getElementById('user_id').value;
            const messageInput = document.getElementById('message_input');
            const message = messageInput.value.trim();

            if (!message || !userId) return;
            
            const welcomeMsg = document.getElementById('welcome_message_container');
            if (welcomeMsg) welcomeMsg.remove();

            addMessageToChat('user', message);
            messageInput.value = '';
            addMessageToChat('ai', '...', 'thinking-bubble'); // Typing indicator

            try {
                const response = await fetch(`${API_URL}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, message: message, context: 'personal' })
                });
                
                const thinkingBubble = document.getElementById('thinking-bubble');
                if (thinkingBubble) thinkingBubble.remove();

                const result = await response.json();
                if (response.ok) {
                    addMessageToChat('ai', result.response);
                } else {
                    addMessageToChat('ai', `Error: ${result.error}`);
                }
            } catch (error) {
                const thinkingBubble = document.getElementById('thinking-bubble');
                if (thinkingBubble) thinkingBubble.remove();
                addMessageToChat('ai', 'An unexpected network error occurred.');
                console.error('Chat error:', error);
            }
        }
        
        function addMessageToChat(role, text, id = null) {
            const chatWindow = document.getElementById('chat_window');
            const bubbleWrapper = document.createElement('div');
            const alignment = role === 'user' ? 'justify-end' : 'justify-start';
            const bubbleClasses = role === 'user' ? 'user' : 'ai';
            
            const wrapperDiv = document.createElement('div');
            wrapperDiv.className = `flex w-full ${alignment}`;

            bubbleWrapper.className = `chat-bubble ${bubbleClasses}`;
            if (id) bubbleWrapper.id = id;
            if (text === '...') bubbleWrapper.classList.add('animate-pulse');
            
            bubbleWrapper.textContent = text;
            
            wrapperDiv.appendChild(bubbleWrapper);
            chatWindow.appendChild(wrapperDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

        document.getElementById('message_input').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template_string(INDEX_HTML)

# --- API Endpoints ---

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main conversation endpoint."""
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    context = data.get('context', 'personal')
    feedback = data.get('feedback_on_previous')

    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    user_profile = get_user(user_id)
    if not user_profile:
        return jsonify({"error": "User profile not found. Please create a profile first."}), 404

    memory_manager = get_memory_manager(user_id)
    tone_engine = ToneEngine(user_profile, memory_manager)

    if feedback:
        tone_engine.process_feedback(feedback)
        update_user(user_id, user_profile)

    memory_manager.add_to_short_term_memory({"role": "user", "message": message})
    response_text, applied_tone = tone_engine.generate_response(message, context)
    memory_manager.add_to_short_term_memory({"role": "assistant", "message": response_text})
    
    update_user(user_id, user_profile) # Save interaction count
    conversation_id = str(uuid.uuid4())

    return jsonify({
        "response": response_text,
        "tone_applied": applied_tone,
        "memory_updated": True,
        "conversation_id": conversation_id
    })

@app.route('/api/profile', methods=['POST'])
def profile_create_update():
    """Create or update a user profile."""
    data = request.json
    user_id = data.get('user_id')
    preferences = data.get('preferences')

    if not user_id or not preferences:
        return jsonify({"error": "user_id and preferences are required"}), 400

    existing_user_profile = get_user(user_id)
    
    # --- MODIFIED: More robust handling of preference updates ---
    if existing_user_profile:
        # Update preferences, keeping existing ones if new ones aren't provided
        existing_user_profile['tone_preferences'] = preferences.get('tone_preferences', existing_user_profile.get('tone_preferences', {}))
        existing_user_profile['communication_style'] = preferences.get('communication_style', existing_user_profile.get('communication_style', {}))
        update_user(user_id, existing_user_profile)
        # Update the profile in the in-memory manager if it exists
        if user_id in user_memory_managers:
            user_memory_managers[user_id].profile = existing_user_profile
        return jsonify({"message": f"Profile updated for {user_id}", "user_id": user_id})
    else:
        new_profile = {
            "user_id": user_id,
            "tone_preferences": preferences.get('tone_preferences', {}),
            "communication_style": preferences.get('communication_style', {}),
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0,
                "last_interaction": None
            }
        }
        create_user(new_profile)
        return jsonify({"message": f"Profile created for {user_id}", "user_id": user_id}), 201


@app.route('/api/profile/<user_id>', methods=['GET'])
def profile_retrieve(user_id):
    """Retrieve a user profile."""
    user = get_user(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/memory/<user_id>', methods=['GET'])
def memory_retrieve(user_id):
    """Get conversation memory for a user."""
    memory_manager = get_memory_manager(user_id)
    if memory_manager:
        memory_data = {
            "short_term_memory": list(memory_manager.short_term_memory),
            "long_term_summary": "Long-term summary not yet implemented in this version."
        }
        return jsonify(memory_data)
    return jsonify({"error": "Memory not found for user"}), 404

@app.route('/api/memory/<user_id>', methods=['DELETE'])
def memory_clear(user_id):
    """Clear user memory."""
    if user_id in user_memory_managers:
        user_memory_managers[user_id].clear_short_term_memory()
    return jsonify({"message": f"Short-term memory cleared for user_id: {user_id}"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)