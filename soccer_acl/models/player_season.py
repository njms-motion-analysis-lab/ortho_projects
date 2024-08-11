from gettext import npgettext
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from models.player import Player
from . import Base, BaseModel, Session
import np
from sqlalchemy.orm import relationship

class PlayerSeason(BaseModel):
    __tablename__ = 'player_seasons'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    season_id = Column(Integer, ForeignKey('seasons.id'))
    age = Column(Integer)
    gls = Column(Integer)
    mp = Column(Integer)
    min = Column(Integer)
    n90s = Column(Float)
    starts = Column(Integer)
    subs = Column(Integer)
    unsub = Column(Integer)
    ast = Column(Integer)
    g_a = Column(Integer)
    g_pk = Column(Integer)
    pk = Column(Integer)
    pk_att = Column(Integer)
    pk_m = Column(Integer)
    pos = Column(String)
    player_code = Column(String)

    # Relationships
    player = relationship('Player', back_populates='seasons')
    season = relationship('Season', back_populates='player_seasons')



    def find_control_matches(self, top_n=5):
        session = Session()
        # Define the statistics to compare
        stats_columns = ['gls', 'mp', 'min', 'n90s', 'starts', 'subs', 'ast', 'g_a', 'g_pk']

        # Get the statistics for this player season, handling None or empty values
        current_stats = np.array([
            self.safe_convert(getattr(self, col), float, 0) for col in stats_columns
        ], dtype=np.float64)

        # Query to find potential control player seasons, excluding the same player
        potential_controls = session.query(PlayerSeason).join(Player).filter(
            PlayerSeason.id != self.id,
            Player.unique_id != self.player.unique_id  # Exclude same player by unique_id
        ).all()

        distances = []

        for control in potential_controls:
            control_stats = np.array([
                self.safe_convert(getattr(control, col), float, 0) for col in stats_columns
            ], dtype=np.float64)

            # Calculate Euclidean distance
            distance = np.linalg.norm(current_stats - control_stats)

            distances.append((control, distance))

        # Sort by distance and return the top N matches
        distances.sort(key=lambda x: x[1])
        top_matches = [match for match, _ in distances[:top_n]]

        return top_matches

    @staticmethod
    def safe_convert(value, target_type, default=0):
        """Safely convert values to the target type, returning a default if conversion fails."""
        try:
            return target_type(value) if value is not None and value != '' else default
        except (ValueError, TypeError):
            return default
    

    def get_fbref_stats(self):
        
        shooting = json.loads(self.player.fbref_stats[0].shooting_stats)
        playing_time


