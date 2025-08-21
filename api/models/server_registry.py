# Path: api/models/server_registry.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ServerRegistry(db.Model):
    """Model untuk registry server lokal yang terdaftar"""
    
    __tablename__ = 'server_registry'
    
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(100), nullable=False)
    church_name = db.Column(db.String(200), nullable=False)
    host = db.Column(db.String(45), nullable=False)  # IP address
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('online', 'offline', 'maintenance'), default='offline')
    
    # Authentication info untuk server
    api_key = db.Column(db.String(255), unique=True)
    
    # Timestamps
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_ping = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User yang mendaftarkan server
    registered_by = db.Column(db.Integer, nullable=False)
    
    # Server configuration
    description = db.Column(db.Text)
    max_clients = db.Column(db.Integer, default=100)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_host_port', 'host', 'port'),
        db.Index('idx_status', 'status'),
        db.Index('idx_last_ping', 'last_ping'),
    )
    
    def __init__(self, server_name, church_name, host, port, registered_by, **kwargs):
        self.server_name = server_name
        self.church_name = church_name
        self.host = host
        self.port = port
        self.registered_by = registered_by
        
        # Set optional fields
        self.description = kwargs.get('description', '')
        self.max_clients = kwargs.get('max_clients', 100)
        self.status = kwargs.get('status', 'offline')
        
        # Generate API key untuk server
        import secrets
        self.api_key = secrets.token_urlsafe(32)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'server_name': self.server_name,
            'church_name': self.church_name,
            'host': self.host,
            'port': self.port,
            'status': self.status,
            'description': self.description,
            'max_clients': self.max_clients,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'last_ping': self.last_ping.isoformat() if self.last_ping else None,
            'registered_by': self.registered_by
        }
    
    def is_online(self):
        """Check if server is considered online"""
        if not self.last_ping:
            return False
        
        time_diff = datetime.utcnow() - self.last_ping
        return time_diff.total_seconds() < 300  # 5 menit
    
    def update_ping(self):
        """Update last ping timestamp"""
        self.last_ping = datetime.utcnow()
        self.status = 'online'
    
    def set_offline(self):
        """Set server status to offline"""
        self.status = 'offline'
    
    def get_server_url(self):
        """Get full server URL"""
        return f"http://{self.host}:{self.port}"
    
    def __repr__(self):
        return f'<ServerRegistry {self.server_name}@{self.host}:{self.port}>'