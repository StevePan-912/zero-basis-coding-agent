# backend/app/routes.py
"""
REST API Routes for the zero-basis-coding-agent backend.

Provides endpoints for:
- Health checks
- User authentication (register, login)
- Chat functionality
- Mode management
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.auth import AuthService
from app.chains.mode_switching_chain import ModeSwitchingChain
from app.chains.conversation_management_chain import ConversationManagementChain
from app.adapters.difficulty_adapter import DifficultyAdapter
from app.adapters.prompt_builder import PromptBuilder


# In-memory storage for user sessions (will be replaced with database later)
user_sessions = {}
user_modes = {}
user_conversations = {}


def get_or_create_user_mode(user_id: str) -> ModeSwitchingChain:
    """Get or create a ModeSwitchingChain for the user."""
    if user_id not in user_modes:
        user_modes[user_id] = ModeSwitchingChain(mode='teaching')
    return user_modes[user_id]


def get_or_create_user_conversation(user_id: str) -> ConversationManagementChain:
    """Get or create a ConversationManagementChain for the user."""
    if user_id not in user_conversations:
        user_conversations[user_id] = ConversationManagementChain(user_id=user_id)
    return user_conversations[user_id]


# Health Check Blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with status 'healthy'.
    """
    return jsonify({'status': 'healthy'}), 200


# Auth Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request body:
        - username: User's username (3-20 characters)
        - password: User's password (min 6 characters)
        - email: User's email address

    Returns:
        - 201: User registered successfully
        - 400: Validation error
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'error': 'No data provided'
        }), 400

    result = AuthService.register_user(data, mock=True)

    if result.success:
        return jsonify({
            'success': True,
            'message': result.message,
            'data': result.data
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': result.message,
            'error': result.error
        }), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user and return a JWT token.

    Request body:
        - username: User's username
        - password: User's password

    Returns:
        - 200: Login successful with JWT token
        - 400: Validation error
        - 401: Authentication failed
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'error': 'No data provided'
        }), 400

    result = AuthService.login_user(data, mock=True)

    if result.success:
        # Create JWT token using Flask-JWT-Extended
        access_token = create_access_token(identity=result.data['user_id'])
        return jsonify({
            'success': True,
            'message': result.message,
            'data': {
                'user_id': result.data['user_id'],
                'username': result.data['username'],
                'token': access_token
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result.message,
            'error': result.error
        }), 401


# Chat Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api')


@chat_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """
    Send a chat message.

    Requires JWT authentication.

    Request body:
        - message: User's message
        - mode: Optional mode override ('teaching' or 'practical')

    Returns:
        - 200: Chat response
        - 400: Validation error
        - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'error': 'No data provided'
        }), 400

    message = data.get('message', '')
    mode_override = data.get('mode', None)

    if not message or not message.strip():
        return jsonify({
            'success': False,
            'message': 'Message is required',
            'error': 'Message cannot be empty'
        }), 400

    # Get user's mode chain
    mode_chain = get_or_create_user_mode(user_id)

    # Override mode if provided
    if mode_override:
        try:
            mode_chain.switch_mode(mode_override)
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': 'Invalid mode',
                'error': str(e)
            }), 400

    # Get conversation chain
    conversation_chain = get_or_create_user_conversation(user_id)

    # Add user message to conversation
    conversation_chain.add_message('user', message)

    # Get difficulty adapter and assess difficulty
    difficulty_adapter = DifficultyAdapter()
    difficulty = difficulty_adapter.assess_difficulty(user_id)

    # Build response strategy
    response_strategy = mode_chain.build_response_strategy(message)

    # Build prompt using prompt builder
    prompt_builder = PromptBuilder()
    full_prompt = prompt_builder.build_prompt(
        base_prompt=message,
        difficulty=difficulty,
        mode=mode_chain.get_current_mode()
    )

    # In a real implementation, we would call the LLM here
    # For now, return a mock response
    response = f"[{mode_chain.get_current_mode().upper()} MODE] "
    response += f"[{difficulty.upper()} LEVEL] "
    response += f"Response to: {message}"

    # Add assistant response to conversation
    conversation_chain.add_message('assistant', response)

    return jsonify({
        'success': True,
        'response': response,
        'difficulty': difficulty,
        'mode': mode_chain.get_current_mode()
    }), 200


# Mode Blueprint
mode_bp = Blueprint('mode', __name__, url_prefix='/api/mode')


@mode_bp.route('/switch', methods=['POST'])
@jwt_required()
def switch_mode():
    """
    Switch the user's current mode.

    Requires JWT authentication.

    Request body:
        - mode: Target mode ('teaching' or 'practical')

    Returns:
        - 200: Mode switched successfully
        - 400: Invalid mode
        - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'error': 'No data provided'
        }), 400

    mode = data.get('mode', '')

    if not mode:
        return jsonify({
            'success': False,
            'message': 'Mode is required',
            'error': 'Mode cannot be empty'
        }), 400

    # Get user's mode chain
    mode_chain = get_or_create_user_mode(user_id)

    try:
        mode_chain.switch_mode(mode)
        return jsonify({
            'success': True,
            'current_mode': mode_chain.get_current_mode(),
            'message': f"Mode switched to {mode}"
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Invalid mode',
            'error': str(e)
        }), 400


@mode_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_mode():
    """
    Get the user's current mode.

    Requires JWT authentication.

    Returns:
        - 200: Current mode
        - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    mode_chain = get_or_create_user_mode(user_id)

    return jsonify({
        'success': True,
        'current_mode': mode_chain.get_current_mode(),
        'config': mode_chain.get_mode_config()
    }), 200


def register_routes(app):
    """
    Register all blueprints with the Flask app.

    Args:
        app: Flask application instance
    """
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(mode_bp)