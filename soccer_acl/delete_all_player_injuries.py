from models import PlayerInjury, Session

def delete_all_player_injuries():
    try:
        Session.query(PlayerInjury).delete()
        Session.commit()
        print("All PlayerInjury records deleted.")
    except Exception as e:
        print(f"An error occurred while deleting records: {str(e)}")
        Session.rollback()
    finally:
        Session.close()


delete_all_player_injuries()