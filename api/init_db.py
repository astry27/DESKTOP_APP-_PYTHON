# Path: api/init_db.py

from app import app, db
from models.server_registry import ServerRegistry
from models.api_log import ApiLog
from models.user_session import UserSession
from datetime import datetime
import sys

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            return True
    except Exception as e:
        print(f"✗ Error creating tables: {str(e)}")
        return False

def create_indexes():
    """Create additional indexes if needed"""
    try:
        with app.app_context():
            # Additional indexes can be created here if needed
            # Most indexes are defined in the models
            print("✓ Database indexes created successfully")
            return True
    except Exception as e:
        print(f"✗ Error creating indexes: {str(e)}")
        return False

def seed_sample_data():
    """Insert sample data for testing"""
    try:
        with app.app_context():
            # Check if data already exists
            if ServerRegistry.query.count() > 0:
                print("! Sample data already exists, skipping...")
                return True
            
            # Sample server registry
            sample_server = ServerRegistry(
                server_name="Gereja Sample",
                church_name="Paroki Santa Maria",
                host="192.168.1.100",
                port=9000,
                registered_by=1,
                description="Sample server for testing"
            )
            
            db.session.add(sample_server)
            
            # Sample API log
            sample_log = ApiLog(
                user_id=1,
                action="INIT_DATABASE",
                details="Database initialized with sample data",
                ip_address="127.0.0.1",
                level="INFO"
            )
            
            db.session.add(sample_log)
            
            db.session.commit()
            print("✓ Sample data inserted successfully")
            return True
            
    except Exception as e:
        print(f"✗ Error inserting sample data: {str(e)}")
        db.session.rollback()
        return False

def cleanup_old_data():
    """Cleanup old data"""
    try:
        with app.app_context():
            # Cleanup expired sessions
            cleaned_sessions = UserSession.cleanup_expired_sessions()
            print(f"✓ Cleaned up {cleaned_sessions} expired sessions")
            
            # Cleanup old logs (older than 90 days)
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            old_logs = ApiLog.query.filter(ApiLog.created_at < cutoff_date).all()
            
            for log in old_logs:
                db.session.delete(log)
            
            db.session.commit()
            print(f"✓ Cleaned up {len(old_logs)} old log entries")
            return True
            
    except Exception as e:
        print(f"✗ Error cleaning up data: {str(e)}")
        db.session.rollback()
        return False

def verify_database():
    """Verify database setup"""
    try:
        with app.app_context():
            # Test basic operations
            server_count = ServerRegistry.query.count()
            log_count = ApiLog.query.count()
            session_count = UserSession.query.count()
            
            print(f"✓ Database verification complete:")
            print(f"  - Servers: {server_count}")
            print(f"  - Logs: {log_count}")
            print(f"  - Sessions: {session_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ Database verification failed: {str(e)}")
        return False

def main():
    """Main initialization function"""
    print("Flask API Database Initialization")
    print("=" * 40)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "init"
    
    if command == "init":
        print("Initializing database...")
        success = True
        success &= create_tables()
        success &= create_indexes()
        success &= verify_database()
        
        if success:
            print("\n✓ Database initialization completed successfully!")
        else:
            print("\n✗ Database initialization failed!")
            sys.exit(1)
    
    elif command == "seed":
        print("Seeding sample data...")
        success = seed_sample_data()
        
        if success:
            print("\n✓ Sample data seeding completed successfully!")
        else:
            print("\n✗ Sample data seeding failed!")
            sys.exit(1)
    
    elif command == "cleanup":
        print("Cleaning up old data...")
        success = cleanup_old_data()
        
        if success:
            print("\n✓ Data cleanup completed successfully!")
        else:
            print("\n✗ Data cleanup failed!")
            sys.exit(1)
    
    elif command == "verify":
        print("Verifying database...")
        success = verify_database()
        
        if success:
            print("\n✓ Database verification completed successfully!")
        else:
            print("\n✗ Database verification failed!")
            sys.exit(1)
    
    elif command == "reset":
        print("WARNING: This will delete all data!")
        confirm = input("Are you sure? Type 'yes' to continue: ")
        
        if confirm.lower() == 'yes':
            try:
                with app.app_context():
                    db.drop_all()
                    print("✓ All tables dropped")
                    
                    create_tables()
                    print("✓ Tables recreated")
                    
                print("\n✓ Database reset completed successfully!")
            except Exception as e:
                print(f"\n✗ Database reset failed: {str(e)}")
                sys.exit(1)
        else:
            print("Database reset cancelled.")
    
    else:
        print("Usage: python init_db.py [command]")
        print("Commands:")
        print("  init     - Initialize database (default)")
        print("  seed     - Insert sample data")
        print("  cleanup  - Clean up old data")
        print("  verify   - Verify database setup")
        print("  reset    - Reset database (WARNING: deletes all data)")

if __name__ == "__main__":
    main()