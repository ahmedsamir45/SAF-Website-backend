import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def drop_token_blacklist_tables():
    """Drop all token_blacklist tables"""
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Disable foreign key checks temporarily
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Drop tables if they exist
        cursor.execute("""
            DROP TABLE IF EXISTS token_blacklist_outstandingtoken CASCADE;
            DROP TABLE IF EXISTS token_blacklist_blacklistedtoken CASCADE;
        """)
        
        conn.commit()
        print("✓ Dropped token_blacklist tables")
        
    except Exception as e:
        print(f"Error dropping tables: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def run_migrations():
    """Run Django migrations"""
    import subprocess
    try:
        # Run migrations
        subprocess.run(['python', 'manage.py', 'migrate', 'token_blacklist', 'zero'], check=True)
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)
        print("✓ Migrations completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")

if __name__ == "__main__":
    print("=== Fixing token_blacklist tables ===")
    drop_token_blacklist_tables()
    run_migrations()
    print("=== Fix completed successfully ===")
