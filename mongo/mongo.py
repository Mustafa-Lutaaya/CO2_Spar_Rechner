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
        # Creates a list of dictionaries, where each dictionary represents a category and its associated items
        grouped_items = [ # We first define the structure of the dictionary we want to create
            {
                "category": category['category'], # Gets the category name
                "items": category['items'] # Gets the list of items in that category
            }
            for category in items # Then specify the data to loop over 
        ]
        # Inserts the list of dictionaries into MongoDB using insert_many
        self.co2.insert_many(grouped_items)
    
    def update_item(self, category, item_name, count):  
        self.co2.update_one(
            {"category": category, "items.name": item_name}, # Filters to find the correct category & item
            {"$inc": { # $inc is used to increment/decerement the values
                "items.$.count": count, # Increments the count by the specified value
            }}
        )
    
    def get_updated_items(self):
        return list(self.co2.find())  # Returns all items (and their current counts & CO2) from the 'co2' collection
    
    def reset_counts(self, items):
        for category in items:
             # For each category, performs an update on the MongoDB collection
            self.co2.update_one(
                {"category": category["category"]}, # Filters the document based on category
                {"$set":{
                    "items":[ # Updates the 'items' field in the document
                        {**item, # Copies all key-value pairs from item then overwrites them.
                         "count":0,  # Reset 'count' to 0
                         "co2":0 # Resets 'co2' to 0
                         }  
                        for item in category["items"]  # Loops through each item in the category
                    ]
                }}
            )
