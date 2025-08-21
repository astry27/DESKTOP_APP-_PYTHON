# Path: api/models/user_session.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

class UserSession(db.Model):
    """Model untuk mengelola session user"""
    
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    
    # Session info
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    device_info = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_token', 'token'),
        db.Index('idx_is_active', 'is_active'),
        db.Index('idx_expires_at', 'expires_at'),
        db.Index('idx_last_activity', 'last_activity'),
    )
    
    def __init__(self, user_id, token, **kwargs):
        self.user_id = user_id
        self.token = token
        
        # Set optional fields
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.device_info = kwargs.get('device_info')
        
        # Set expiration (default 24 jam)
        expiry_hours = kwargs.get('expiry_hours', 24)
        self.expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if session is valid (active and not expired)"""
        return self.is_active and not self.is_expired()
    
    def extend_session(self, hours=24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
    
    def invalidate(self):
        """Invalidate session"""
        self.is_active = False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'device_info': self.device_info,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }
    
    @classmethod
    def create_session(cls, user_id, token, **kwargs):
        """Create new session"""
        session = cls(user_id=user_id, token=token, **kwargs)
        db.session.add(session)
        try:
            db.session.commit()
            return session
        except Exception as e:
            db.session.rollback()
            print(f"Error creating session: {str(e)}")
            return None
    
    @classmethod
    def get_user_sessions(cls, user_id, active_only=True):
        """Get all sessions for a user"""
        query = cls.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.last_activity.desc()).all()
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Cleanup expired sessions"""
        try:
            expired_sessions = cls.query.filter(
                cls.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired_sessions:
                session.invalidate()
            
            db.session.commit()
            return len(expired_sessions)
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up sessions: {str(e)}")
            return 0
    
    @classmethod
    def cleanup_inactive_sessions(cls, days=7):
        """Cleanup sessions that haven't been active for specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            inactive_sessions = cls.query.filter(
                cls.last_activity < cutoff_date
            ).all()
            
            for session in inactive_sessions:
                session.invalidate()
            
            db.session.commit()
            return len(inactive_sessions)
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up inactive sessions: {str(e)}")
            return 0
    
    @classmethod
    def invalidate_user_sessions(cls, user_id, except_token=None):
        """Invalidate all sessions for a user except specified token"""
        try:
            query = cls.query.filter_by(user_id=user_id, is_active=True)
            if except_token:
                query = query.filter(cls.token != except_token)
            
            sessions = query.all()
            for session in sessions:
                session.invalidate()
            
            db.session.commit()
            return len(sessions)
        except Exception as e:
            db.session.rollback()
            print(f"Error invalidating user sessions: {str(e)}")
            return 0
    
    def __repr__(self):
        return f'<UserSession {self.user_id} - {self.ip_address}>'