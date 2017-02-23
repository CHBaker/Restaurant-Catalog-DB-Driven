import sys

# import alchemy orm database 
# classes for mapper
from sqlalchemy import( 
    Column, ForeignKey, Integer, String)

# declarative base for 
# configuration and class code
from sqlalchemy.ext.declarative import(
    declarative_base)

# used for foreing key relationships
from sqlalchemy.orm import relationship

# used in configuration at end of file
from sqlalchemy import create_engine

# instance of base class tells alchemy
# classes correspond to tables in db
Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(
        Integer, primary_key = True
        )
    name = Column(
        String(180), nullable = False
        )


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(
        String(80), nullable = False
        )
    id = Column(
        Integer, primary_key = True
        )
    description = Column(
        String(250)
        )
    price = Column(
        String(8)
        )
    course = Column(
        String(250)
        )
    restaurant_id = Column(
        Integer, ForeignKey('restaurant.id')
        )
    restaurant = relationship(Restaurant)

# serialized function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }

####### end of file #######

# allows us of db similar to more robust
# db like mySQL or postgreSQL
engine = create_engine('sqlite:///restaurantmenu.db')

# adds tables to our db
Base.metadata.create_all(engine)