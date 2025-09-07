from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, moderator, admin
    profile_image = db.Column(db.String(120), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_name_change = db.Column(db.DateTime)
    is_banned = db.Column(db.Boolean, default=False)
    ban_expires_at = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')
    reactions = db.relationship('GameReaction', backref='user', lazy=True, cascade='all, delete-orphan')
    bans_issued = db.relationship('UserBan', foreign_keys='UserBan.banned_by_id', backref='banned_by', lazy=True)
    user_bans = db.relationship('UserBan', foreign_keys='UserBan.user_id', backref='banned_user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def can_change_username(self):
        if not self.last_name_change:
            return True
        return datetime.utcnow() > self.last_name_change + timedelta(days=30)
    
    def is_active_ban(self):
        if not self.is_banned:
            return False
        if self.ban_expires_at and datetime.utcnow() > self.ban_expires_at:
            # Ban has expired, update the user
            self.is_banned = False
            self.ban_expires_at = None
            db.session.commit()
            return False
        return True

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    download_link = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    added_by = db.relationship('User', backref='added_games')
    comments = db.relationship('Comment', backref='game', lazy=True, cascade='all, delete-orphan')
    reactions = db.relationship('GameReaction', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Game {self.title}>'
    
    def get_like_count(self):
        return GameReaction.query.filter_by(game_id=self.id, reaction_type='like').count()
    
    def get_dislike_count(self):
        return GameReaction.query.filter_by(game_id=self.id, reaction_type='dislike').count()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class GameReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, dislike
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'game_id', name='unique_user_game_reaction'),)
    
    def __repr__(self):
        return f'<GameReaction {self.reaction_type}>'

class UserBan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    banned_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserBan {self.user_id}>'
