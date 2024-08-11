from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import BaseModel

class FbrefPlayerStats(BaseModel):
    __tablename__ = 'fbref_player_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    playing_time_stats = Column(Text)  # JSON or stringified version of the playing_time_stats data
    shooting_stats = Column(Text)  # JSON or stringified version of the shooting_stats data

    # Relationship back to Player
    player = relationship("Player", back_populates="fbref_stats")