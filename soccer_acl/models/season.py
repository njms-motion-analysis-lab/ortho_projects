from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import BaseModel

class Season(BaseModel):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    comp = Column(String)
    team = Column(String)

    # Relationships
    player_seasons = relationship('PlayerSeason', back_populates='season')
