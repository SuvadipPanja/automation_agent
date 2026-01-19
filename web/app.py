from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import logging
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ai_engine import AIEngine
from core.voice_engine import VoiceEngine

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'ares-secret-key-change-in-production'
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize engines
ai_engine = AIEngine()
voice_engine = VoiceEngine()

# Store conversation history per session
conversations = {}

@app.route('/')
def index():
    """Render the modern UI"""
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        conversations[session['session_id']] = []
    
    return render_template('index_modern.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = session.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize conversation history for this session if needed
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Add user message to history
        conversations[session_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response
        ai_response = ai_engine.process(user_message)
        
        # Add AI response to history
        conversations[session_id].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/listen', methods=['POST'])
def voice_listen():
    """Listen for voice input"""
    try:
        transcribed_text = voice_engine.listen()
        
        if transcribed_text:
            return jsonify({
                'text': transcribed_text,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'No speech detected'}), 400
            
    except Exception as e:
        logger.error(f"Error in voice listen: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/speak', methods=['POST'])
def voice_speak():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        voice_engine.speak(text)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in voice speak: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for current session"""
    try:
        session_id = session.get('session_id')
        history = conversations.get(session_id, [])
        
        return jsonify({
            'history': history,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history for current session"""
    try:
        session_id = session.get('session_id')
        if session_id in conversations:
            conversations[session_id] = []
        
        return jsonify({
            'status': 'success',
            'message': 'History cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing history: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_engine': 'active',
        'voice_engine': 'active'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)