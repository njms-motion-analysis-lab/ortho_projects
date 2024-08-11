import os
import sqlite3


def create_database():
    # Get the base directory of the script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the database file relative to the base directory
    db_dir = os.path.join(BASE_DIR, '../../data')
    db_path = os.path.join(db_dir, 'soccer_acl.db')

    # Create the directory if it doesn't exist
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Player table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nation TEXT,
        unique_id TEXT UNIQUE
    )
    ''')

    # Create Season table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Season (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        comp TEXT,
        team TEXT
    )
    ''')

    # Create PlayerSeason table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PlayerSeason (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        season_id INTEGER,
        age INTEGER,
        gls INTEGER,
        mp INTEGER,
        min INTEGER,
        n90s REAL,
        starts INTEGER,
        subs INTEGER,
        unsub INTEGER,
        ast INTEGER,
        g_a INTEGER,
        g_pk INTEGER,
        pk INTEGER,
        pk_att INTEGER,
        pk_m INTEGER,
        pos TEXT,
        player_code TEXT,
        FOREIGN KEY(player_id) REFERENCES Player(id),
        FOREIGN KEY(season_id) REFERENCES Season(id)
    )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and tables created successfully.")