import json
import requests
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from helpers import parse_date
from bs4 import BeautifulSoup

from models.fbref_player_stats import FbrefPlayerStats

from . import BaseModel, Session

class Player(BaseModel):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nation = Column(String)
    unique_id = Column(String, unique=True)
    fbref_link = Column(String)

    # Relationship with PlayerInjury and PlayerSeason
        # Relationship with PlayerInjury and PlayerSeason
    injuries = relationship("PlayerInjury", backref="injured_player", cascade="all, delete-orphan")
    seasons = relationship("PlayerSeason", backref="season_player")  # Adjusted backref name
    fbref_stats = relationship("FbrefPlayerStats", back_populates="player", cascade="all, delete-orphan")

    def pre_injury_seasons(self):
        injury_dates = [injury.date_of_injury for injury in self.injuries if injury.date_of_injury]
        if not injury_dates:
            return []
        first_injury_date = min(injury_dates)
        injury_year = first_injury_date.year
        return [season for season in self.seasons if season.season.year < injury_year]

    def post_injury_seasons(self):
        injury_dates = [injury.date_of_injury for injury in self.injuries if injury.date_of_injury]
        if not injury_dates:
            return []
        first_injury_date = min(injury_dates)
        injury_year = first_injury_date.year
        return [season for season in self.seasons if season.season.year >= injury_year]
    
    def control_pre_seasons(self, player_season):
        """
        Calculate average stats for control player's seasons from the first season up to the given player_season.
        """
        if not player_season:
            return {}

        # Get the year of the given player_season
        target_year = player_season.season.year

        # Get the seasons up to the target year
        pre_seasons = [season for season in self.seasons if season.season.year < target_year]

        # Collect and average the stats for these seasons
        if pre_seasons:
            return self.collect_fbref_stats_multiple(pre_seasons)
        return {}

    def control_post_seasons(self, player_season):
        """
        Calculate average stats for control player's seasons following the given player_season.
        """
        if not player_season:
            return {}

        # Get the year of the given player_season
        target_year = player_season.season.year

        # Get the seasons following the target year
        post_seasons = [season for season in self.seasons if season.season.year > target_year]

        # Collect and average the stats for these seasons
        if post_seasons:
            return self.collect_fbref_stats_multiple(post_seasons)
        return {}

    def collect_fbref_stats_multiple(self, player_seasons):
        """
        Collect and average stats for multiple seasons.
        """
        shooting_stats = []
        playing_time_stats = []

        for season in player_seasons:
            stats = self.collect_fbref_stats(season)
            shooting_stats.extend(stats['shooting_stats'])  # extend the list instead of append
            playing_time_stats.extend(stats['playing_time_stats'])  # extend the list instead of append

        # Initialize empty dictionaries to store the sum of stats
        summed_shooting_stats = {}
        summed_playing_time_stats = {}

        # Sum the stats across all seasons
        for stats_list in shooting_stats:
            for key, value in stats_list.items():
                try:
                    numeric_value = float(value) if value and value.replace('.', '', 1).isdigit() else 0
                except ValueError:
                    numeric_value = 0  # Handle the case where the value cannot be converted to a float

                if key in summed_shooting_stats:
                    summed_shooting_stats[key] += numeric_value
                else:
                    summed_shooting_stats[key] = numeric_value

        for stats_list in playing_time_stats:
            for key, value in stats_list.items():
                try:
                    numeric_value = float(value) if value and value.replace('.', '', 1).isdigit() else 0
                except ValueError:
                    numeric_value = 0  # Handle the case where the value cannot be converted to a float

                if key in summed_playing_time_stats:
                    summed_playing_time_stats[key] += numeric_value
                else:
                    summed_playing_time_stats[key] = numeric_value

        # Average the stats
        avg_shooting_stats = {key: summed_shooting_stats[key] / len(shooting_stats) for key in summed_shooting_stats}
        avg_playing_time_stats = {key: summed_playing_time_stats[key] / len(playing_time_stats) for key in summed_playing_time_stats}

        return {
            'shooting_stats': avg_shooting_stats,
            'playing_time_stats': avg_playing_time_stats
        }


    def collect_avg_fbref_stats(self, player_seasons=None):
        shooting_stats = json.loads(self.fbref_stats[0].shooting_stats)
        playing_time_stats = json.loads(self.fbref_stats[0].playing_time_stats)

        if player_seasons:
            season_years = [str(season.season.year) for season in player_seasons]

            # Filter and accumulate shooting stats
            filtered_shooting_stats = [
                stat for stat in shooting_stats if stat.get('season') in season_years
            ]
            # Filter and accumulate playing time stats
            filtered_playing_time_stats = [
                stat for stat in playing_time_stats if stat.get('season') in season_years
            ]

            # Calculate average stats
            avg_shooting_stats = self.calculate_average_stats(filtered_shooting_stats)
            avg_playing_time_stats = self.calculate_average_stats(filtered_playing_time_stats)

            return {
                'avg_shooting_stats': avg_shooting_stats,
                'avg_playing_time_stats': avg_playing_time_stats
            }

        # If no specific player_seasons provided, return all stats
        return {
            'shooting_stats': shooting_stats,
            'playing_time_stats': playing_time_stats
        }

    def calculate_average_stats(self, stats_list):
        if not stats_list:
            return {}

        # Initialize dictionaries to accumulate totals
        totals = {}
        count = len(stats_list)

        # Accumulate totals for each stat
        for stat in stats_list:
            for key, value in stat.items():
                # Convert numeric strings to floats for averaging
                try:
                    value = float(value.replace(',', '')) if value else 0.0
                except ValueError:
                    value = 0.0

                if key in totals:
                    totals[key] += value
                else:
                    totals[key] = value

        # Calculate averages
        averages = {key: total / count for key, total in totals.items()}

        return averages
    
    def fetch_player_data(self):
        url = self.fbref_link
        try:
            response = requests.get(url)
        except Exception:
            alt_url = self.construct_fbref_link()
            response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract relevant stats from Playing Time table
        playing_time_table = soup.select_one('table#stats_playing_time_dom_lg')
        shooting_table = soup.select_one('table#stats_shooting_dom_lg')

        # Parse the tables
        def parse_table(table):
            data = []
            if table:
                rows = table.select('tbody tr')
                for row in rows:
                    season = row.select_one('th[data-stat="year_id"]').text if row.select_one('th[data-stat="year_id"]') else ''
                    stats = {col['data-stat']: col.text for col in row.select('td')}
                    stats['season'] = season
                    data.append(stats)
            return data

        playing_time_stats = parse_table(playing_time_table)
        shooting_stats = parse_table(shooting_table)

        return playing_time_stats, shooting_stats

    def store_fbref_stats(self):
        # Fetch the player by name
        session = Session()
        player = session.query(Player).filter(Player.name == self.name).first()

        if player:
            # Fetch the player stats from fbref
            playing_time_stats, shooting_stats = self.fetch_player_data()

            # Convert the stats to JSON strings for storage
            playing_time_stats_json = json.dumps(playing_time_stats)
            shooting_stats_json = json.dumps(shooting_stats)

            # Create a new FbrefPlayerStats record
            fbref_stats = FbrefPlayerStats(
                player_id=player.id,
                playing_time_stats=playing_time_stats_json,
                shooting_stats=shooting_stats_json
            )

            # Add and commit the new stats to the database
            session.add(fbref_stats)
            session.commit()
            print(f"Fbref stats for {self.name} have been added.")
        else:
            print(f"Player {self.name} not found in the database.")
        
    def construct_fbref_link(self) -> str:
        """
        Construct the fbref link for a player using their name and unique ID.

        :param player_name: The player's name (e.g., "Dana Foederer").
        :param unique_id: The player's unique ID (e.g., "2e6a5e3e").
        :return: The constructed fbref link.
        """
        # Replace spaces with underscores in the player's name
        name_with_underscores = self.name.replace(" ", "-")
        
        # Construct the URL
        fbref_link = f"https://fbref.com/en/players/{self.unique_id}/{name_with_underscores}#all_stats_standard"
        
        return fbref_link
    
    def collect_fbref_stats(self, player_season=None):
        shooting_stats = json.loads(self.fbref_stats[0].shooting_stats)
        playing_time_stats = json.loads(self.fbref_stats[0].playing_time_stats)

        # If player_season is provided, filter the stats for just those years
        if player_season:
            season_year = player_season.season.year

            # Filter shooting stats
            shooting_stats_filtered = [
                stat for stat in shooting_stats if stat.get('season') == str(season_year)
            ]

            # Filter playing time stats
            playing_time_stats_filtered = [
                stat for stat in playing_time_stats if stat.get('season') == str(season_year)
            ]

            return {
                'shooting_stats': shooting_stats_filtered,
                'playing_time_stats': playing_time_stats_filtered
            }

        # If no player_season is provided, return all stats
        return {
            'shooting_stats': shooting_stats,
            'playing_time_stats': playing_time_stats
        }





    
        



