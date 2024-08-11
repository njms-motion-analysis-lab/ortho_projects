from models import Base, Session, PlayerInjury, Player, FbrefPlayerStats
 

def update_player_and_create_injury_table():
    session = Session()

    # Create the PlayerInjury table and ensure Player has stats_link
    Base.metadata.create_all(session.bind)
    
    session.close()

if __name__ == '__main__':
    update_player_and_create_injury_table()