import os
import sqlite3
import contextlib

class DBwrapper:
    """
    Example Usage:
        db = DBwrapper()

        # Insert data
        db.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                ('First Post', 'Content for the first post'))

        db.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                ('Second Post', 'Content for the second post'))
    """
    sql_file ='small_db.sql'
    db_name ='/home/shegoo/strathmore/ProjectC/backend/chat.db'

    def __init__(self):
        if not os.path.exists(self.db_name):
            conn = sqlite3.connect(self.db_name)
            with open(self.sql_file) as f:
                conn.executescript(f.read())
                print('DB created')
                conn.commit()
            conn.close()
        else:
            print('DB already exists')
    
    @contextlib.contextmanager
    def connect(self):
        try:
            conn = sqlite3.connect(self.db_name)
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        with self.connect() as conn:
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
            return cur.lastrowid

    def executemany(self, query, params_list):
        with self.connect() as conn:
            conn.executemany(query, params_list)
            conn.commit()

    def select(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            return results

        
        
    
    