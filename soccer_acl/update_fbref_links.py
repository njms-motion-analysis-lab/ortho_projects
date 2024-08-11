import os
import csv
from models import Player, Session
from helpers import flexible_name_search

# Define the path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), 'data/injured_players_before.csv')

def update_fbref_links(csv_file_path):
    unmatched_players = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                player_name = row['Player'].strip()

                # Use flexible name search to find the player
                player = flexible_name_search(Session, Player, player_name)

                if not player:
                    print(f"No match found for {player_name}. Skipping this entry.")
                    unmatched_players.append(player_name)
                    continue
                import pdb;pdb.set_trace()
                # Update player's fbref_link
                # fbref_link = row['Stats Link'].strip()
                # if fbref_link:
                #     player.fbref_link = fbref_link
                #     Session.add(player)

            # Commit all changes
        print(unmatched_players)
            # Session.commit()

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        Session.rollback()  # Rollback in case of error
    finally:
        Session.close()  # Close the session

if __name__ == '__main__':
    update_fbref_links(csv_file_path)