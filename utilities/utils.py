from operator import itemgetter
from datetime import datetime

class AppUtils:
    @staticmethod
    def current_time():
        return datetime.now().strftime('%Y-%m-%d %H:%M') # Returns current time in selected format
    
    @staticmethod
    def calculate_sessions(total_CO2):  # Calculates CO2 equivalents for different modes of transport
        return{
            "wieauto": round(total_CO2 / 0.2, 2), # 0.2Kg CO2 per Km
            "wieflugzeug": round(total_CO2 / 0.2, 2), # 0.2Kg CO2 per Km
            "wiebus": round(total_CO2 / 0.05, 2) # 0.05Kg CO2 per Km
        }
    