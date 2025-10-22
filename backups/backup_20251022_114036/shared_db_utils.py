"""
Shared Database Utilities for Holly Hot Box
Connects to Postgres-OEMK database without interfering with Django's main database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_shared_db_connection():
    """Get connection to the shared Postgres-OEMK database"""
    try:
        conn = psycopg2.connect(
            host='postgres-oemk.railway.internal',
            port=5432,
            database='railway',
            user='postgres',
            password='IYblOgGeEuVcGtDvevcobxyriuqkGNeQ'
        )
        return conn
    except Exception as e:
        print(f"Failed to connect to shared database: {e}")
        return None

def query_shared_database(query, params=None):
    """Execute a query on the shared database and return results"""
    conn = get_shared_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Query failed: {e}")
        return None
    finally:
        conn.close()

def get_shared_user_data(user_id=None, username=None):
    """Get user data from the shared database"""
    if user_id:
        query = "SELECT * FROM auth_user WHERE id = %s"
        params = (user_id,)
    elif username:
        query = "SELECT * FROM auth_user WHERE username = %s"
        params = (username,)
    else:
        return None
    
    return query_shared_database(query, params)

def sync_user_to_shared_db(user_data):
    """Sync user data to the shared database"""
    # This would be used to sync HBB users to the shared database
    # Implementation depends on what data needs to be shared
    pass
