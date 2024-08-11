from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from . import BaseModel

class PlayerInjury(BaseModel):
    __tablename__ = 'player_injuries'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date_of_injury = Column(Date, nullable=True)  # Nullable date of injury
    venue = Column(String, nullable=True)
    injury_surface = Column(String, nullable=True)
    home_injury_surface = Column(String, nullable=True)
    home_facility = Column(String, nullable=True)
    game_in_injury_season = Column(String, nullable=True)
    position = Column(String, nullable=True)
    injury = Column(String, nullable=True)
    laterality = Column(String, nullable=True)
    footedness = Column(String, nullable=True)
    concomitant_injury = Column(String, nullable=True)
    activity_type = Column(Integer, nullable=True)
    mechanism = Column(Integer, nullable=True)
    minutes_played = Column(Integer, nullable=True)
    active_nwsl = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    return_date = Column(Date, nullable=True)

    # Relationship with Player model
    player = relationship("Player", backref="player_injuries")


