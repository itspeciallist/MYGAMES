import os
import secrets
from PIL import Image
from flask import current_app
from functools import wraps
from flask_login import current_user
from flask import abort

def save_picture(form_picture, folder='uploads'):
    """Save uploaded picture with random filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image
    output_size = (200, 200)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    """Decorator for moderator and admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['moderator', 'admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def can_manage_users(user):
    """Check if user can manage other users"""
    return user.is_authenticated and user.role in ['moderator', 'admin']

def can_manage_games(user):
    """Check if user can manage games"""
    return user.is_authenticated and user.role in ['moderator', 'admin']

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return 'Never'

def get_genre_display_name(genre):
    """Get display name for genre"""
    genre_map = {
        'action': 'Action',
        'adventure': 'Adventure',
        'rpg': 'RPG',
        'strategy': 'Strategy',
        'simulation': 'Simulation',
        'sports': 'Sports',
        'racing': 'Racing',
        'puzzle': 'Puzzle',
        'horror': 'Horror',
        'shooter': 'Shooter',
        'platformer': 'Platformer',
        'indie': 'Indie',
        'mmo': 'MMO',
        'casual': 'Casual',
        'other': 'Other'
    }
    return genre_map.get(genre, genre.title())
