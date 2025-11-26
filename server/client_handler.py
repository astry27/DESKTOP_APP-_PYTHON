# Path: server/client_handler.py

import json
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class ClientRegistrationHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            path = urlparse(self.path).path
            
            if path == '/client/register':
                self.handle_client_register(data)
            elif path == '/client/heartbeat':
                self.handle_client_heartbeat(data)
            elif path == '/client/disconnect':
                self.handle_client_disconnect(data)
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urlparse(self.path).path
            
            if path == '/client/active':
                self.handle_get_active_clients()
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def handle_client_register(self, data):
        """Handle client registration - register to remote API to ensure database persistence"""
        try:
            # Forward registration to remote Flask API to ensure data is persisted in database
            # This is critical because local memory storage alone doesn't create database records
            import requests

            client_ip = data.get('client_ip')
            hostname = data.get('hostname', '')
            session_id = data.get('session_id', '')

            if not client_ip:
                response = {
                    "status": "error",
                    "message": "Client IP required"
                }
                self.send_json_response(400, response)
                return

            # Prepare data for remote API registration
            api_data = {
                'client_ip': client_ip,
                'hostname': hostname,
                'session_id': session_id
            }

            try:
                # Try to register with remote Flask API
                # This ensures the client is stored in the database
                api_response = requests.post(
                    "http://localhost:5000/client/register",
                    json=api_data,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )

                if api_response.status_code == 200:
                    api_result = api_response.json()
                    if api_result.get('status') == 'success':
                        # Get the real connection_id from API
                        connection_id = api_result.get('connection_id')

                        # Also register locally for memory cache
                        if hasattr(self.server, 'database_manager') and self.server.database_manager:
                            db_manager = self.server.database_manager
                            data_with_conn_id = data.copy()
                            data_with_conn_id['connection_id'] = connection_id
                            db_manager.register_client_session(data_with_conn_id)

                        response = {
                            "status": "success",
                            "message": "Client registered successfully",
                            "connection_id": connection_id
                        }
                        self.send_json_response(200, response)
                        print(f"[CLIENT HANDLER] Client registered in database: {client_ip} - {hostname} (ID: {connection_id})")
                        return

                # If API returns error
                error_msg = api_result.get('message', 'Registration failed')
                response = {
                    "status": "error",
                    "message": f"API registration failed: {error_msg}"
                }
                self.send_json_response(400, response)

            except requests.exceptions.ConnectionError:
                # If cannot connect to local Flask API, try to register via database directly
                print("[CLIENT HANDLER] Cannot connect to Flask API, attempting direct database registration")

                if hasattr(self.server, 'database_manager') and self.server.database_manager:
                    db_manager = self.server.database_manager
                    success, message = db_manager.register_client_session(data)

                    if success:
                        # Use session_id as connection_id since we're registering directly
                        response = {
                            "status": "success",
                            "message": "Client registered via local database",
                            "connection_id": session_id
                        }
                        self.send_json_response(200, response)
                        print(f"[CLIENT HANDLER] Client registered locally: {client_ip} - {hostname}")
                    else:
                        response = {
                            "status": "error",
                            "message": f"Local registration failed: {message}"
                        }
                        self.send_json_response(400, response)
                else:
                    response = {
                        "status": "error",
                        "message": "Database manager not available"
                    }
                    self.send_json_response(500, response)

        except Exception as e:
            print(f"Error in handle_client_register: {e}")
            response = {
                "status": "error",
                "message": f"Registration error: {str(e)}"
            }
            self.send_json_response(500, response)
    
    def handle_client_heartbeat(self, data):
        """Handle client heartbeat - forward to database to update last_activity"""
        try:
            import requests

            connection_id = data.get('connection_id')
            client_ip = data.get('client_ip')

            if not (connection_id or client_ip):
                response = {
                    "status": "error",
                    "message": "Connection ID or Client IP required"
                }
                self.send_json_response(400, response)
                return

            try:
                # Try to update heartbeat via Flask API for database persistence
                heartbeat_response = requests.post(
                    "http://localhost:5000/client/heartbeat",
                    json=data,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )

                if heartbeat_response.status_code == 200:
                    result = heartbeat_response.json()
                    response = {
                        "status": result.get('status', 'success'),
                        "message": result.get('message', 'Heartbeat updated')
                    }
                    self.send_json_response(200, response)
                else:
                    response = {
                        "status": "error",
                        "message": f"Flask API heartbeat failed: {heartbeat_response.status_code}"
                    }
                    self.send_json_response(heartbeat_response.status_code, response)

            except requests.exceptions.ConnectionError:
                # Fallback to local database manager
                print("[CLIENT HANDLER] Cannot connect to Flask API, using local heartbeat update")

                if hasattr(self.server, 'database_manager') and self.server.database_manager:
                    db_manager = self.server.database_manager
                    success, message = db_manager.update_client_activity(connection_id, client_ip)

                    response = {
                        "status": "success" if success else "error",
                        "message": message
                    }
                    self.send_json_response(200, response)
                else:
                    response = {
                        "status": "error",
                        "message": "Database manager not available"
                    }
                    self.send_json_response(500, response)

        except Exception as e:
            print(f"Error in handle_client_heartbeat: {e}")
            response = {
                "status": "error",
                "message": f"Heartbeat error: {str(e)}"
            }
            self.send_json_response(500, response)
    
    def handle_client_disconnect(self, data):
        """Handle client disconnection - forward to database to mark as disconnected"""
        try:
            import requests

            connection_id = data.get('connection_id')
            client_ip = data.get('client_ip')

            if not (connection_id or client_ip):
                response = {
                    "status": "error",
                    "message": "Connection ID or Client IP required"
                }
                self.send_json_response(400, response)
                return

            try:
                # Try to disconnect via Flask API for database persistence
                disconnect_response = requests.post(
                    "http://localhost:5000/client/disconnect",
                    json=data,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )

                if disconnect_response.status_code == 200:
                    result = disconnect_response.json()
                    response = {
                        "status": result.get('status', 'success'),
                        "message": result.get('message', 'Client disconnected')
                    }
                    self.send_json_response(200, response)
                    print(f"[CLIENT HANDLER] Client disconnected via Flask API: {client_ip}")
                else:
                    response = {
                        "status": "error",
                        "message": f"Flask API disconnect failed: {disconnect_response.status_code}"
                    }
                    self.send_json_response(disconnect_response.status_code, response)

            except requests.exceptions.ConnectionError:
                # Fallback to local database manager
                print("[CLIENT HANDLER] Cannot connect to Flask API, using local disconnect")

                if hasattr(self.server, 'database_manager') and self.server.database_manager:
                    db_manager = self.server.database_manager
                    success, message = db_manager.remove_client_session(connection_id, client_ip or '')

                    response = {
                        "status": "success" if success else "error",
                        "message": message
                    }
                    self.send_json_response(200, response)
                    print(f"[CLIENT HANDLER] Client disconnected locally: {client_ip}")
                else:
                    response = {
                        "status": "error",
                        "message": "Database manager not available"
                    }
                    self.send_json_response(500, response)

        except Exception as e:
            print(f"Error in handle_client_disconnect: {e}")
            response = {
                "status": "error",
                "message": f"Disconnect error: {str(e)}"
            }
            self.send_json_response(500, response)
    
    def handle_get_active_clients(self):
        """Handle getting active clients"""
        try:
            if hasattr(self.server, 'database_manager') and self.server.database_manager:
                db_manager = self.server.database_manager
                success, clients = db_manager.get_active_sessions()
                
                if success:
                    response = {
                        "status": "success",
                        "data": clients,
                        "count": len(clients) if isinstance(clients, list) else 0
                    }
                    self.send_json_response(200, response)
                else:
                    response = {
                        "status": "error",
                        "message": clients,
                        "data": []
                    }
                    self.send_json_response(500, response)
            else:
                response = {
                    "status": "error",
                    "message": "Database manager not available",
                    "data": []
                }
                self.send_json_response(500, response)
                
        except Exception as e:
            print(f"Error in handle_get_active_clients: {e}")
            response = {
                "status": "error",
                "message": f"Get clients error: {str(e)}",
                "data": []
            }
            self.send_json_response(500, response)
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        response = json.dumps(data).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class ClientRegistrationServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.database_manager = None
    
    def set_database_manager(self, database_manager):
        """Set database manager for handling client operations"""
        self.database_manager = database_manager
        if self.server:
            self.server.database_manager = database_manager
    
    def start(self):
        """Start the HTTP server in a separate thread"""
        try:
            self.server = HTTPServer(('localhost', self.port), ClientRegistrationHandler)
            self.server.database_manager = self.database_manager
            
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            print(f"[CLIENT HANDLER] Server started on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            print(f"[CLIENT HANDLER] Error starting server: {e}")
            return False
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("[CLIENT HANDLER] Server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.server is not None and self.thread is not None and self.thread.is_alive()