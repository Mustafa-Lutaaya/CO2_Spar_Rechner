from sqlalchemy import Column, Integer, String, Float # Defines columns and their data types in the database table
from database.database import Base  # Imports the declarative base from the database module

# ORM Model representing a row in the "items" table
class CO2(Base):
    __tablename__ = "items" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    category = Column(String)  # Adds a Category column that stores strings
    name = Column(String, unique=True)  # Adds a Name column that stores strings & ensures its unique
    count = Column(Integer, default=0) # Adds a Count column which holds integers
    base_co2 = Column(Float) # Adds a Base_CO2 column which stores float numbers    