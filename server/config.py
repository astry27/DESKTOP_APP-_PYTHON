# Path: server/config.py

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class ServerConfig:
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'entf7819_db-client-server')
    DB_USER = os.getenv('DB_USER', 'entf7819_db-client-server')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
    
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 9000))
    SERVER_MAX_CONNECTIONS = int(os.getenv('SERVER_MAX_CONNECTIONS', 100))
    
    API_HOST = os.getenv('API_HOST', 'enternal.my.id')
    API_PORT = int(os.getenv('API_PORT', 80))
    API_BASE_URL = f"http://{API_HOST}/flask"
    
    APP_NAME = "Server Gereja Katolik"
    APP_VERSION = "2.1.0"
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'server.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', str(BASE_DIR / 'uploads'))
    BACKUP_DIR = os.getenv('BACKUP_DIR', str(BASE_DIR / 'backups'))
    TEMP_DIR = os.getenv('TEMP_DIR', str(BASE_DIR / 'temp'))
    
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif']
    
    ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'true').lower() == 'true'
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'gereja-katolik-secret-key-2024')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'gereja-salt')
    
    AUTO_BACKUP = os.getenv('AUTO_BACKUP', 'true').lower() == 'true'
    BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL', 86400))
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    
    MYSQLDUMP_PATH = os.getenv('MYSQLDUMP_PATH', 'mysqldump')
    MYSQL_PATH = os.getenv('MYSQL_PATH', 'mysql')
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': cls.DB_CHARSET,
            'autocommit': True,
            'raise_on_warnings': True,
            'connection_timeout': 10,
            'allow_local_infile': True,
            'ssl_disabled': True
        }
    
    @classmethod
    def get_connection_pool_config(cls) -> Dict[str, Any]:
        return {
            'pool_name': 'gereja_pool',
            'pool_size': cls.DB_POOL_SIZE,
            'pool_reset_session': True,
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': cls.DB_CHARSET
        }
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        return {
            'host': cls.SERVER_HOST,
            'port': cls.SERVER_PORT,
            'max_connections': cls.SERVER_MAX_CONNECTIONS,
            'debug': cls.DEBUG
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        return {
            'base_url': cls.API_BASE_URL,
            'timeout': 30,
            'max_retries': 3,
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': f'{cls.APP_NAME}/{cls.APP_VERSION}'
            }
        }
    
    @classmethod
    def create_directories(cls):
        directories = [
            cls.LOG_DIR,
            cls.UPLOAD_DIR,
            cls.BACKUP_DIR,
            cls.TEMP_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def load_from_file(cls, config_file: str = 'server_config.json') -> Dict[str, Any]:
        config_path = cls.BASE_DIR / config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        return {}
    
    @classmethod
    def save_to_file(cls, config_data: Dict[str, Any], config_file: str = 'server_config.json'):
        config_path = cls.BASE_DIR / config_file
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        errors = []
        
        if not cls.DB_HOST:
            errors.append("DB_HOST tidak boleh kosong")
        
        if not cls.DB_NAME:
            errors.append("DB_NAME tidak boleh kosong")
        
        if not cls.DB_USER:
            errors.append("DB_USER tidak boleh kosong")
        
        if cls.SERVER_PORT < 1000 or cls.SERVER_PORT > 65535:
            errors.append("SERVER_PORT harus antara 1000-65535")
        
        try:
            cls.create_directories()
        except Exception as e:
            errors.append(f"Gagal membuat direktori: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_environment_info(cls) -> Dict[str, Any]:
        return {
            'app_name': cls.APP_NAME,
            'app_version': cls.APP_VERSION,
            'debug_mode': cls.DEBUG,
            'database_host': cls.DB_HOST,
            'database_name': cls.DB_NAME,
            'server_host': cls.SERVER_HOST,
            'server_port': cls.SERVER_PORT,
            'api_base_url': cls.API_BASE_URL,
            'upload_dir': cls.UPLOAD_DIR,
            'backup_dir': cls.BACKUP_DIR,
            'log_dir': cls.LOG_DIR
        }

class DevelopmentConfig(ServerConfig):
    DEBUG = True
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'entf7819_db-client-server')
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(ServerConfig):
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    AUTO_BACKUP = True
    BACKUP_INTERVAL = 21600

def get_config(environment: str = 'development') -> ServerConfig:
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'default': ServerConfig
    }
    
    return configs.get(environment, ServerConfig)

config = get_config(os.getenv('ENVIRONMENT', 'development'))

is_valid, validation_errors = config.validate_config()
if not is_valid:
    print("KONFIGURASI ERROR")
    for error in validation_errors:
        print(f"- {error}")
    print("========================")