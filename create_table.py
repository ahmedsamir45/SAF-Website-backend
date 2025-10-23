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

# SQL to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS activities_contactmessage (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT false
);
"""

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    # Execute the SQL
    cursor.execute(create_table_sql)
    conn.commit()
    print("Table 'activities_contactmessage' created successfully!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        cursor.close()
        conn.close()