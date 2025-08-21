# Path: api/routes/monitoring.py

from flask import Blueprint, request, jsonify, current_app
import jwt
import requests
import logging
from functools import wraps
from datetime import datetime, timedelta

from models.server_registry import ServerRegistry
from models.user_session import UserSession
from models.api_log import ApiLog

monitoring_bp = Blueprint('monitoring', __name__)
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            session_record = UserSession.query.filter_by(
                user_id=current_user_id,
                token=token,
                is_active=True
            ).first()
            
            if not session_record:
                return jsonify({'message': 'Token invalid or expired'}), 401
                
            session_record.last_activity = datetime.utcnow()
            from models.user_session import db
            db.session.commit()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

@monitoring_bp.route('/servers', methods=['GET'])
@token_required
def get_all_servers_status(current_user_id):
    """Get status semua server yang terdaftar"""
    try:
        servers = ServerRegistry.query.all()
        servers_status = []
        
        for server in servers:
            # Check real-time status
            try:
                server_url = f"http://{server.host}:{server.port}/api/health"
                response = requests.get(server_url, timeout=5)
                
                if response.status_code == 200:
                    server.status = 'online'
                    server.last_ping = datetime.utcnow()
                    health_data = response.json()
                else:
                    server.status = 'offline'
                    health_data = None
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                server.status = 'offline'
                health_data = None
            
            # Get additional info if server is online
            additional_info = {}
            if server.status == 'online':
                try:
                    stats_url = f"http://{server.host}:{server.port}/api/stats"
                    stats_response = requests.get(stats_url, timeout=5)
                    if stats_response.status_code == 200:
                        additional_info = stats_response.json()
                except:
                    pass
            
            servers_status.append({
                'id': server.id,
                'server_name': server.server_name,
                'church_name': server.church_name,
                'host': server.host,
                'port': server.port,
                'status': server.status,
                'last_ping': server.last_ping.isoformat() if server.last_ping else None,
                'registered_at': server.registered_at.isoformat(),
                'is_online': server.is_online(),
                'health_data': health_data,
                'additional_info': additional_info
            })
        
        # Commit status updates
        from models.server_registry import db
        db.session.commit()
        
        # Count statistics
        total_servers = len(servers_status)
        online_servers = len([s for s in servers_status if s['status'] == 'online'])
        offline_servers = total_servers - online_servers
        
        return jsonify({
            'servers': servers_status,
            'statistics': {
                'total': total_servers,
                'online': online_servers,
                'offline': offline_servers,
                'uptime_percentage': (online_servers / total_servers * 100) if total_servers > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Get servers status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@monitoring_bp.route('/server/<int:server_id>/details', methods=['GET'])
@token_required
def get_server_details(current_user_id, server_id):
    """Get detail lengkap server tertentu"""
    try:
        server = ServerRegistry.query.get_or_404(server_id)
        
        # Get comprehensive server info
        server_details = {
            'basic_info': server.to_dict(),
            'health_status': None,
            'system_stats': None,
            'database_stats': None,
            'client_connections': None,
            'recent_logs': None
        }
        
        # Try to get detailed info if server is accessible
        try:
            base_url = f"http://{server.host}:{server.port}/api"
            
            # Health check
            health_response = requests.get(f"{base_url}/health", timeout=5)
            if health_response.status_code == 200:
                server_details['health_status'] = health_response.json()
                server.status = 'online'
                server.last_ping = datetime.utcnow()
            
            # System stats
            try:
                stats_response = requests.get(f"{base_url}/stats", timeout=5)
                if stats_response.status_code == 200:
                    server_details['system_stats'] = stats_response.json()
            except:
                pass
            
            # Database stats
            try:
                db_response = requests.get(f"{base_url}/database/stats", timeout=5)
                if db_response.status_code == 200:
                    server_details['database_stats'] = db_response.json()
            except:
                pass
            
            # Client connections
            try:
                clients_response = requests.get(f"{base_url}/clients", timeout=5)
                if clients_response.status_code == 200:
                    server_details['client_connections'] = clients_response.json()
            except:
                pass
            
            # Recent logs
            try:
                logs_response = requests.get(f"{base_url}/logs?limit=20", timeout=5)
                if logs_response.status_code == 200:
                    server_details['recent_logs'] = logs_response.json()
            except:
                pass
                
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            server.status = 'offline'
        
        # Commit status update
        from models.server_registry import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'server_details': server_details
        })
        
    except Exception as e:
        logger.error(f"Get server details error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@monitoring_bp.route('/logs', methods=['GET'])
@token_required
def get_api_logs(current_user_id):
    """Get log aktivitas API"""
    try:
        # Query parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        action = request.args.get('action')
        level = request.args.get('level')
        user_id = request.args.get('user_id')
        
        # Build query
        query = ApiLog.query
        
        if action:
            query = query.filter(ApiLog.action == action)
        if level:
            query = query.filter(ApiLog.level == level)
        if user_id:
            query = query.filter(ApiLog.user_id == int(user_id))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        logs = query.order_by(ApiLog.created_at.desc()).offset(offset).limit(limit).all()
        
        logs_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'logs': logs_data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        })
        
    except Exception as e:
        logger.error(f"Get API logs error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@monitoring_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user_id):
    """Get analytics data"""
    try:
        # Time range
        days = int(request.args.get('days', 7))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Server analytics
        servers = ServerRegistry.query.all()
        total_servers = len(servers)
        online_servers = len([s for s in servers if s.is_online()])
        
        # Activity analytics
        recent_logs = ApiLog.query.filter(
            ApiLog.created_at >= start_date
        ).all()
        
        # Group by action
        action_counts = {}
        for log in recent_logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        # Group by day
        daily_activity = {}
        for log in recent_logs:
            day = log.created_at.date().isoformat()
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        # User activity
        user_activity = {}
        for log in recent_logs:
            if log.user_id:
                user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
        
        # Error rate
        error_logs = [log for log in recent_logs if log.level in ['ERROR', 'CRITICAL']]
        error_rate = (len(error_logs) / len(recent_logs) * 100) if recent_logs else 0
        
        analytics_data = {
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'server_statistics': {
                'total_servers': total_servers,
                'online_servers': online_servers,
                'offline_servers': total_servers - online_servers,
                'uptime_percentage': (online_servers / total_servers * 100) if total_servers > 0 else 0
            },
            'activity_statistics': {
                'total_activities': len(recent_logs),
                'unique_actions': len(action_counts),
                'error_rate': round(error_rate, 2),
                'active_users': len(user_activity)
            },
            'activity_breakdown': {
                'by_action': action_counts,
                'by_day': daily_activity,
                'by_user': user_activity
            },
            'top_actions': sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'recent_errors': [log.to_dict() for log in error_logs[-10:]]
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        logger.error(f"Get analytics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
@token_required
def get_alerts(current_user_id):
    """Get system alerts"""
    try:
        alerts = []
        
        # Check for offline servers
        offline_servers = ServerRegistry.query.filter_by(status='offline').all()
        for server in offline_servers:
            if server.last_ping:
                time_offline = datetime.utcnow() - server.last_ping
                if time_offline.total_seconds() > 300:  # Offline lebih dari 5 menit
                    alerts.append({
                        'type': 'server_offline',
                        'severity': 'high',
                        'message': f'Server {server.server_name} has been offline for {int(time_offline.total_seconds() / 60)} minutes',
                        'server_id': server.id,
                        'timestamp': server.last_ping.isoformat()
                    })
        
        # Check for recent errors
        recent_errors = ApiLog.query.filter(
            ApiLog.level.in_(['ERROR', 'CRITICAL']),
            ApiLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).limit(5).all()
        
        for error in recent_errors:
            alerts.append({
                'type': 'api_error',
                'severity': 'medium' if error.level == 'ERROR' else 'high',
                'message': f'API Error: {error.action} - {error.details}',
                'log_id': error.id,
                'timestamp': error.created_at.isoformat()
            })
        
        # Check for high activity (potential DDoS)
        recent_activities = ApiLog.query.filter(
            ApiLog.created_at >= datetime.utcnow() - timedelta(minutes=10)
        ).count()
        
        if recent_activities > 1000:  # Lebih dari 1000 aktivitas dalam 10 menit
            alerts.append({
                'type': 'high_activity',
                'severity': 'medium',
                'message': f'Unusually high API activity detected: {recent_activities} requests in the last 10 minutes',
                'count': recent_activities,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Sort alerts by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'critical_count': len([a for a in alerts if a['severity'] == 'high']),
            'warning_count': len([a for a in alerts if a['severity'] == 'medium'])
        })
        
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@monitoring_bp.route('/cleanup', methods=['POST'])
@token_required
def cleanup_data(current_user_id):
    """Cleanup old data"""
    try:
        data = request.get_json()
        cleanup_type = data.get('type', 'logs')
        days_to_keep = int(data.get('days_to_keep', 30))
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        cleaned_count = 0
        
        if cleanup_type == 'logs':
            # Cleanup old logs
            old_logs = ApiLog.query.filter(ApiLog.created_at < cutoff_date).all()
            cleaned_count = len(old_logs)
            
            for log in old_logs:
                from models.api_log import db
                db.session.delete(log)
            
        elif cleanup_type == 'sessions':
            # Cleanup expired sessions
            cleaned_count = UserSession.cleanup_expired_sessions()
            cleaned_count += UserSession.cleanup_inactive_sessions(days_to_keep)
        
        # Commit changes
        from models.api_log import db
        db.session.commit()
        
        # Log cleanup activity
        ApiLog.log_activity(
            user_id=current_user_id,
            action='DATA_CLEANUP',
            details=f'Cleaned up {cleaned_count} {cleanup_type} records older than {days_to_keep} days',
            ip_address=request.remote_addr,
            endpoint=request.endpoint,
            method=request.method,
            status_code=200
        )
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_count} {cleanup_type} records',
            'cleaned_count': cleaned_count,
            'cleanup_type': cleanup_type,
            'days_to_keep': days_to_keep
        })
        
    except Exception as e:
        logger.error(f"Cleanup data error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500