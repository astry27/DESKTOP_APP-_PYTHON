# Path: api/models/api_log.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class ApiLog(db.Model):
    """Model untuk logging aktivitas API"""
    
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # Nullable untuk system logs
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    
    # Request info
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    
    # Response info
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # dalam milliseconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Level logging
    level = db.Column(db.Enum('INFO', 'WARNING', 'ERROR', 'CRITICAL'), default='INFO')
    
    # Additional data (JSON format)
    extra_data = db.Column(db.Text)  # JSON string
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_action', 'action'),
        db.Index('idx_created_at', 'created_at'),
        db.Index('idx_level', 'level'),
        db.Index('idx_ip_address', 'ip_address'),
    )
    
    def __init__(self, user_id, action, details, **kwargs):
        self.user_id = user_id
        self.action = action
        self.details = details
        
        # Set optional fields
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.endpoint = kwargs.get('endpoint')
        self.method = kwargs.get('method')
        self.status_code = kwargs.get('status_code')
        self.response_time = kwargs.get('response_time')
        self.level = kwargs.get('level', 'INFO')
        
        # Set extra data if provided
        if 'extra_data' in kwargs:
            self.set_extra_data(kwargs['extra_data'])
    
    def set_extra_data(self, data):
        """Set extra data as JSON string"""
        if data:
            self.extra_data = json.dumps(data)
    
    def get_extra_data(self):
        """Get extra data as Python object"""
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except json.JSONDecodeError:
                return None
        return None
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'level': self.level,
            'extra_data': self.get_extra_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log_activity(cls, user_id, action, details, **kwargs):
        """Helper method untuk logging aktivitas"""
        log = cls(user_id=user_id, action=action, details=details, **kwargs)
        db.session.add(log)
        try:
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            print(f"Error logging activity: {str(e)}")
            return None
    
    @classmethod
    def get_user_activities(cls, user_id, limit=50):
        """Get aktivitas user tertentu"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_activities(cls, limit=100):
        """Get aktivitas terbaru"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_activities_by_action(cls, action, limit=50):
        """Get aktivitas berdasarkan action"""
        return cls.query.filter_by(action=action).order_by(cls.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<ApiLog {self.action} by {self.user_id} at {self.created_at}>'