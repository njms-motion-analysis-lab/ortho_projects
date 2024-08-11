import csv
import os
from models import Player, PlayerInjury, Session
from helpers import parse_date, flexible_name_search

# Define the path to the CSV file

def populate_injured_players(csv_file_path):
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                player_name = row['Player'].strip()

                # Find player using flexible name search
                player = flexible_name_search(Session, Player, player_name)

                if not player:
                    print(f"No match found for {player_name}. Skipping this entry.")
                    continue

            #     # Update or create player's stats_link
            #     player.stats_link = row['Link'].strip() if row['Link'].strip() else None
            #     Session.add(player)

            #     # Create a PlayerInjury record
            #     player_injury = PlayerInjury(
            #         player_id=player.id,
            #         date_of_injury=parse_date(row['Date of Injury'].strip()),
            #         venue=row['Venue'].strip(),
            #         injury_surface=row['Injury Surface'].strip(),
            #         home_injury_surface=row['Home = Injury Surface?'].strip(),
            #         home_facility=row['Home Facility?'].strip(),
            #         game_in_injury_season=row['Game in Injury Season'].strip(),
            #         position=row['Position'].strip(),
            #         injury=row['Injury'].strip(),
            #         laterality=row['Laterality'].strip(),
            #         footedness=row['Footedness'].strip(),
            #         concomitant_injury=row['Concomitant injury'].strip(),
            #         activity_type=int(row['Activity Type (1 = NWSL regular season game, 2 = preseason game, 3 = international game, 4 = practice, 5 = Challenge cup, 6 = nwsl playoff)'].strip() or 0),
            #         mechanism=int(row['Mechanism (0 = non-contact; 1 = contact)'].strip() or 0),
            #         minutes_played=int(row['Minutes Played'].strip() or 0),
            #         active_nwsl=row['Active NWSL player?'].strip(),
            #         notes=row['Notes'].strip(),
            #         return_date=parse_date(row['Return Date'].strip())
            #     )
            #     Session.add(player_injury)

            # # Commit all changes
            # Session.commit()

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        Session.rollback()  # Rollback in case of error
    finally:
        Session.close()  # Close the session

if __name__ == '__main__':
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data/NWSL ACL Injuries(ACL Injuries 2013-2023).csv')
    populate_injured_players(csv_file_path)






    