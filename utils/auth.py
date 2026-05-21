from functools import wraps
from flask import request, jsonify, current_app
import jwt
import datetime

def token_required(f):
    """
    Decorator to verify JWT token in request headers
    Usage: @token_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # Note: In a real implementation, you would fetch the user from database here
            current_user_id = data['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        except Exception as e:
            return jsonify({'message': f'Token verification failed: {str(e)}'}), 401
        
        # Pass user_id to the decorated function
        return f(current_user_id, *args, **kwargs)
    
    return decorated

def generate_token(user_id):
    """
    Generate JWT token for user authentication
    
    Args:
        user_id (int): The user's ID
    
    Returns:
        str: JWT token string
    """
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        raise ValueError(f"Token generation failed: {str(e)}")

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(plain_password, hashed_password):
    """
    Verify a password against its hash
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to compare against
    
    Returns:
        bool: True if password matches, False otherwise
    """
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    return bcrypt.check_password_hash(hashed_password, plain_password)