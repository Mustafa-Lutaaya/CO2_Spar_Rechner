from operator import itemgetter # Sorts specific dictionary values by key.
from datetime import datetime #  Used to get the current date and time

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
                    "co2": item["co2"]
                })
            else:
                print(f"Warning: Missing 'co2' in item: {item}")
                rearranged.append({
                    "name": item.get('name', 'Unknown'),
                    "count": item.get('count', 0),
                    "co2": 0  # Default to 0 if missing
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
        return totals, session_count