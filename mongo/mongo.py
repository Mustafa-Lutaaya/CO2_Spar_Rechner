from pymongo import MongoClient # Imports the MongoClient class from the pymongo library.
import os # Accesses the environment variables..
import certifi # Imports the certifi library which is required by Atlas in terms of secure SSL/TLS connections
from dotenv import load_dotenv # Loads secrets from .env.
from datetime import datetime # Imports date time Library
from pydantic import BaseModel, EmailStr, Field # Validates request body structure using schemas
from config.mail_handler import EmailHandler

load_dotenv()

# Defines Schemas using Pydantics & Fully Validates Data
class Register(BaseModel): # Registration Schema
    name: str = Field(min_length=2)  # Name must be at least 2 characters
    email: EmailStr # Must be a valid email format

class Login(BaseModel): # User Login Schema
    email: EmailStr # Must be a valid email format
    password: str # Password as a string

# Mongo Class 2 Be Used to interact with the Database
class Co2:
    def __init__(self): # Constructor method i creates an instance of co2 & setsup references to the necessary collections
        try:
            uri = os.getenv("uri") # Loads the MongoDB URI (connection string) from environment variables
            if not uri:
                raise EnvironmentError("MongoDB URI not found in environment variables.")
            
            self.client = MongoClient(uri, tlsCAFile=certifi.where())  # Initializes the MongoClient to establish a connection to MongoDB

            # Accesses the database and the co2, sos, pending_users, authorized_users collections plus Event Logs after sign out
            self.db = self.client["YoungCaritas"]
            self.co2 = self.db["co2"]
            self.sos = self.db["sessions"] 
            self.pen = self.db["pending_users"]
            self.auth = self.db["authorized_users"]
            self.logs = self.db["Event_Logs"]

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
    
    def update_item(self, category, item_name, count, co2):  
        self.co2.update_one(
            {"category": category, "items.name": item_name}, # Filters to find the correct category & item
            {"$inc": { # $inc is used to increment/decerement the values
                "items.$.count": count, # Increments the count by the specified value
                "items.$.co2": co2, # Increments the co2 by the specified value
            }}
        )
    
    def get_updated_items(self):
        return list(self.co2.find())  # Returns all items (and their current counts & CO2) from the 'co2' collection
    
    def insert_session(self, total_co2, equivalents, exc_items):
        session = {
            "timestamp": datetime.now(),  # Records the exact time of the exchange
            "ingesamt": round(total_co2, 2),  # Total CO2 value for this session
            "wieauto": round(equivalents['wieauto'], 2),  # Equivalent CO2 in car travel
            "wieflugzeug": round(equivalents['wieflugzeug'], 2),  # Equivalent CO2 in flight
            "wiebus": round(equivalents['wiebus'], 2),  # Equivalent CO2 in bus travel
            "exc_items": exc_items # Exchanged Items
        }
        self.sos.insert_one({"session": [session]}) # Inserts the new exchange as a list inside a document into the 'Session' collection

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
    
    def clear_sessions(self):
        # Deletes all documents in the 'xchange' collection
        self.sos.delete_many({})
    
    def get_all_sessions(self):
        # Returns all session documents from the collection as a list
        return list(self.sos.find())
    
    def register_user(self, user:Register):
        if user:
            self.pen.insert_one(user.dict()) # Inserts the user data as a dictionary inside a document into the 'pending_users' collection
            print("User Profile Pending")

    def find_user_by_email(self, email: str):
        # Searches the 'pending_users' collection for a document matching the user's email
        user = self.pen.find_one({"email": email}) # Returns user data when found
        if user:
            return user
        else:
            print("User Not Found")
            return None
            
    def find_user_by_mail(self, email: str):
        # Searches the 'authorized_users' collection for a document matching the user's email
        user = self.auth.find_one({"email": email}) # Returns user data when found
        if user:
            return user
        else:
            print("User Not Found")
            return None
    
    def authenticate_user(self, auth_user):
        self.auth.insert_one(auth_user) # Inserts approved user into 'authorized_users'
    
    def delete_user_by_email(self, email:str,):
        result = self.pen.delete_one({"email": email})
        return result.deleted_count # Returns 1 if deleted, 0 if not found
    
    def log_out(self, user, sessions, sorted_items, total):
        logs = {
            "timestamp": datetime.now(),  # Records the exact time of logout
            "user_name": user, # Adds user name
            "sessions": sessions, # Adds number of sessions
            "sorted_items": sorted_items, # Adds sorted items
            "total": total # Adds total as well
        }
        self.logs.insert_one({"Logs": [logs]}) # Inserts the events logs as a list inside a document into the 'Event_Logs' collection                 