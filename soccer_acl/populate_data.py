import csv
import os
from models import Player, Season, PlayerSeason, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import exc as orm_exc

# Define the path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), 'data/control_1.csv')

def safe_convert(value, target_type, default=None):
    """Safely convert values to the target type, returning a default if conversion fails."""
    try:
        return target_type(value) if value else default
    except ValueError:
        return default

# Function to read the CSV and populate the database
def populate_data(csv_file_path):
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            with Session.no_autoflush:
                for row in reader:
                    # Process each row in the CSV

                    # Check if the player already exists in the database
                    player = Session.query(Player).filter_by(name=row['Player'], unique_id=row['-9999']).first()
                    if not player:
                        player = Player(
                            name=row['Player'].strip(),
                            nation=row['Nation'].strip(),
                            unique_id=row['-9999'].strip()
                        )
                        Session.add(player)
                        Session.commit()  # Commit after adding the player to get the ID

                    # Check if the season already exists in the database
                    season = Session.query(Season).filter_by(year=row['Season'].strip(), team=row['Team'].strip(), comp=row['Comp'].strip()).first()
                    if not season:
                        season = Season(
                            year=row['Season'].strip(),
                            comp=row['Comp'].strip(),
                            team=row['Team'].strip()
                        )
                        Session.add(season)
                        Session.commit()  # Commit after adding the season to get the ID

                    # Create a PlayerSeason record
                    player_season = PlayerSeason(
                        player_id=player.id,
                        season_id=season.id,
                        age=safe_convert(row['Age'], int),
                        gls=safe_convert(row['Gls'], int),
                        mp=safe_convert(row['MP'], int),
                        min=safe_convert(row['Min'], int),
                        n90s=safe_convert(row['90s'], float),
                        starts=safe_convert(row['Starts'], int),
                        subs=safe_convert(row['Subs'], int),
                        unsub=safe_convert(row['unSub'], int),
                        ast=safe_convert(row['Ast'], int),
                        g_a=safe_convert(row['G+A'], int),
                        g_pk=safe_convert(row['G-PK'], int),
                        pk=safe_convert(row['PK'], int),
                        pk_att=safe_convert(row['PKatt'], int),
                        pk_m=safe_convert(row['PKm'], int),
                        pos=row['Pos'].strip(),
                        player_code=row['-9999'].strip()
                    )
                    Session.add(player_season)

            # Commit all player seasons at once
            Session.commit()

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except orm_exc.FlushError as e:
        print(f"Flush error occurred: {str(e)}")
        Session.rollback()  # Rollback in case of flush error
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        Session.rollback()  # Rollback in case of SQLAlchemy error
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        Session.rollback()  # Rollback in case of unexpected error
    finally:
        Session.close()  # Close the session

if __name__ == '__main__':
    populate_data(csv_file_path)
