from models import Base, Session, PlayerInjury, Player

def update_player_and_create_injury_table():
    session = Session()

    # Add the stats_link column to the Player table
    if not hasattr(Player, 'stats_link'):
        Base.metadata.create_all(session.bind)  # This will create the table if it doesn't exist
        print("Updated Player table with stats_link column.")

    # Create the PlayerInjury table
    Base.metadata.create_all(session.bind)
    print("PlayerInjury table created successfully.")
    
    session.close()

if __name__ == '__main__':
    update_player_and_create_injury_table()