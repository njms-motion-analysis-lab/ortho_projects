from operator import and_
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Define the base class for models
Base = declarative_base()

# Define the DATABASE_URL with the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(BASE_DIR, '../data')  # Adjusted to be relative to the soccer_acl folder

# Ensure the data directory exists
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

DATABASE_URL = f'sqlite:///{os.path.join(db_dir, "soccer_acl.db")}'

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = scoped_session(sessionmaker(bind=engine))

# Ensure that the models create the necessary tables in the database
Base.metadata.create_all(engine)

# BaseModel definition with Active Record-like methods
class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def find(cls, record_id):
        return cls.query().filter_by(id=record_id).first()

    @classmethod
    def find_all(cls, *record_ids):
        return cls.query().filter(cls.id.in_(record_ids)).all()

    @classmethod
    def all(cls):
        return cls.query().all()

    @classmethod
    def where(cls, **kwargs):
        return cls.query().filter_by(**kwargs).all()

    @classmethod
    def select(cls, *columns):
        return cls.query().with_entities(*[getattr(cls, col) for col in columns]).all()

    @classmethod
    def update(cls, record_id, **kwargs):
        cls.query().filter_by(id=record_id).update(kwargs)
        Session.commit()

    @classmethod
    def destroy(cls, record_id):
        instance = cls.find(record_id)
        if instance:
            Session.delete(instance)
            Session.commit()
            return True
        return False
    
    @classmethod
    def where_like(cls, **kwargs):
        filters = [getattr(cls, attr).like(f"%{value}%") for attr, value in kwargs.items()]
        if len(filters) == 1:
            return Session.query(cls).filter(filters[0]).all()
        else:
            return Session.query(cls).filter(and_(*filters)).all()

    @classmethod
    def query(cls):
        return Session.query(cls)
    
    def attrs(self):
        # Print each attribute of the instance on a new line
        for column in self.__table__.columns:
            print(f"{column.name}: {getattr(self, column.name)}")

    def save(self):
        """Save the current instance to the database."""
        Session.add(self)
        Session.commit()
    
    def update(self, **kwargs):
        """Update the current instance with provided kwargs."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    def destroy(self):
        """Delete the current instance from the database."""
        Session.delete(self)
        Session.commit()

# Import models to ensure they are registered properly with SQLAlchemy
from .player import Player
from .season import Season
from .player_season import PlayerSeason
from .player_injury import PlayerInjury
from .fbref_player_stats import FbrefPlayerStats  