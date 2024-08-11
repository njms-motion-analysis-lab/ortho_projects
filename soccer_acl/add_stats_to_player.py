import os
from sqlalchemy import create_engine, MetaData, Table, text

# Define the database URL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'soccer_acl.db')  # Ensure this is correct

# Check if the database file exists
if not os.path.exists(db_path):
    raise FileNotFoundError(f"The database file at {db_path} does not exist.")

DATABASE_URL = f'sqlite:///{db_path}'

# Create an engine and reflect the metadata
engine = create_engine(DATABASE_URL)
meta = MetaData()

# Reflect existing database schema
meta.reflect(bind=engine)

# Access the players table
players_table = Table('players', meta, autoload_with=engine)

# Check if the 'stats_link' column exists, and add it if it doesn't
if 'stats_link' not in players_table.c:
    with engine.connect() as connection:
        connection.execute(text('ALTER TABLE players ADD COLUMN stats_link VARCHAR'))

print("Database schema updated successfully.")