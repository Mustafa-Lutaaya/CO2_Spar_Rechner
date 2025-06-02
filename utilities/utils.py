from operator import itemgetter # Sorts specific dictionary values by key.
from datetime import datetime #  Used to get the current date and time
from sqlalchemy.orm import Session
from collections import defaultdict
from models.models import CO2 # Imports CO2 model class

class AppUtils:
    @staticmethod
    def current_time():
        return datetime.now().strftime('%Y-%m-%d %H:%M') # Returns current time in selected format
    
    @staticmethod
    def calculate_equivalents(total_co2):  # Calculates CO2 equivalents for different modes of transport
        return{
            "wieauto": round(total_co2 / (170.65 / 1000), 2), # 0.2Kg CO2 per Km
            "wieflugzeug": round(total_co2 / (181.59 / 1000), 2), # 0.2Kg CO2 per Km
            "wiebus": round(total_co2 /(27.33 / 1000), 2) # 0.05Kg CO2 per Km
        }
    
    @staticmethod
    def rearrange_updated_items(co2_docs:list):
        rearranged = []

        # Iterates over each document & its items list retrieved from MongoDB 
        for obj in co2_docs:
            for item in obj['items']:
                # Appends each item as a dictionary with only the relevant fields
                rearranged.append({
                    "name": item['name'],
                    "count":item['count'],
                    "co2": item.get("co2",0)
                })
        return rearranged # Returns final list
    
    @staticmethod
    def sort_updated_items(updated_items): # Flattens and sorts items by 'count in descending order
        return sorted(updated_items, key=itemgetter('count'), reverse=True) # Sorts the fetched updated items by 'count' in descending order
    
    @staticmethod
    def calculate_total(session_list):
        totals = {"ingesamt": 0, "wieauto": 0, "wieflugzeug": 0, "wiebus": 0}
        session_count = 0
        for doc in session_list:  # Loops through all stored sessions in the Database to calculate cumulative totals and number of sessions
                session = doc['session'][0]
                totals["ingesamt"] += session.get("ingesamt", 0)
                totals["wieauto"] += session.get("wieauto", 0)
                totals["wieflugzeug"] += session.get("wieflugzeug", 0)
                totals["wiebus"] += session.get("wiebus", 0)
                session_count += 1 # Each time the for loop finds a doc, the session count is increased by 1

        # Rounds off all totals to 2 decimal places before returning
        for key in totals:
            totals[key] = round(totals[key], 2)

        return totals, session_count
    
    @staticmethod
    def get_data_grouped_by_category(db: Session):
        items = db.query(CO2).all() # Fetches all CO2 records from the database
        grouped = defaultdict(list) # Creates a dictionary where each key is a category and the value is a list of items

        # Adds item details into the category group
        for item in items:
            grouped[item.category].append({
                "name": item.name,
                "base_co2": item.base_co2,
                "count": 0, # Default count value
                "co2": 0 # Default CO2 value
            })
        
        # Converts the grouped dictionary into a list of dictionaries
        return [
            {"category": category, "items": items_list} 
                for category, items_list in grouped.items()
                ]