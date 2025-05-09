from pymongo import MongoClient # Imports the MongoClient class from the pymongo library.
import os # Accesses the environment variables..
import certifi # Imports the certifi library which is required by Atlas in terms of secure SSL/TLS connections
from dotenv import load_dotenv # Loads secrets from .env.
from datetime import datetime # Imports date time Library

load_dotenv()

# Mongo Class 2 Be Used to interact with the Database
class Co2:
    def __init__(self): # Constructor method i creates an instance of co2 & setsup references to the necessary collections
        try:
            uri = os.getenv("uri") # Loads the MongoDB URI (connection string) from environment variables
            if not uri:
                raise ValueError("MongoDB URI not found in environment variables.")
            
            self.client = MongoClient(uri, tlsCAFile=certifi.where())  # Initializes the MongoClient to establish a connection to MongoDB

            # Accesses the database and the collections
            self.db = self.client["YoungCaritas"]
            self.co2 = self.db["co2"]

            print("Database Connected")

        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise # Re-raises the exception to stop the program
        
    def insert_items(self, items):
        self.co2.insert_one(items)