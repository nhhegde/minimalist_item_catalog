"""
Fundamental Orm/database setup

Configuration: import relevant objects
Class - class (OOP) representation of database
Table - the table to be created, (optional, you
        could also connect to an existing database)
Mapper - creates database or connects to existing
         database and maps class params and methods
         to the database


"""

import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship  # foregin key relationship
from sqlalchemy import create_engine  # maps

# declarative_base is a function
# that returns an sqlalchemy.ext.declarative.api.Base class.
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    # This is part of the mapper I Guess mapping the class to the table.
    username = Column(String(80), nullable=False)
    id = Column(String(2500), primary_key=True)
    password = Column(String(80))


class Item(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category = Column(String(250))
    user_id = Column(String(2500), ForeignKey('user.id'))
    user = relationship(User)


# At end of file
if __name__ == '__main__':
    engine = create_engine('postgresql:///user_item_catalog.db')
    # Drop existing database
    User.__table__.drop(engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
