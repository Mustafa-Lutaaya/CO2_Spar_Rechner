# FastAPI Components to build the web app.
from fastapi import FastAPI, Request, Form  # Imports FastAPI , Request for handling HTTP requests & Form to accept data submitted via POST Requests
from fastapi.responses import HTMLResponse, RedirectResponse # Specifies that a route returns HTML
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support

# Utilities & Database Connection Classes
from dotenv import load_dotenv # Loads secrets from .env.
import os# Accesses the environment variables..
from datetime import datetime
from pathlib import Path # Provides object-oriented file system paths
from sqlite.sql_lite import CO2 # Imports the CO2Connection Class for sql
from mongo.mongo import Co2 # Imports the Co2Connection Class for MongoDB
from utilities.utils import AppUtils # Imports the data processing functions

# Loads enviroment variables from .env file to retrieve sensitive data securely
load_dotenv() # Loads secrets

# Initializes FastAPI Web Application
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") # Mounts the 'static' Files directory making it accessible via '/static' URL 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder


# Database Initialization
berechner_db = CO2("Berechner.db") # Creates an instance of  CO2 class from sqlite.sql_lite.
mongo = Co2() # Initializes the earlier imported MongoDB handler class & creates an instance of the Co2 class
table_name = "CO2_Spar" # Stores Table Name
items = berechner_db.get_data_by_category(table_name) # Retrieves data grouped by category from sql database table
# mongo.insert_items(items) # Inserted Items into Mongo DB

# Route for the homepage ('/') that returns an HTML response displaying items
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    total_CO2 = sum(
        (item.get('CO2', 0))
        for category in items
        for item in category['items'])
    
    sessions = AppUtils.calculate_sessions(total_CO2)  # Calculates how mmuch C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function
    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items,  # Passes items data to be rendered
        "sessions": sessions, # C02 equivalent in different modes of transport
        "total_CO2": total_CO2, # Total C02 emitted based on selected items
    }
    return templates.TemplateResponse(request, "index.html", context)  # Renders the 'index.html' template with data from the context dictionary

# Route to handle form submissions of incrementing & decrementing counts
@app.post("/", response_class=HTMLResponse)
def update_count(request: Request, action: str = Form(...), item_name: str = Form(...)): # request:Request accesses headers & cookies while the Form(...) tells FastAPI value must come from a form field
    for category in items:
        for item in category['items']: # Loops through each item within the current category
            if item['name'] == item_name: # If the item's name macthes submitted form value
                 # Updates item's count based on the action
                if action == 'increment':
                    item['count'] += 1 
                elif action == 'decrement':
                    item['count'] = max(0, item['count'] - 1)
                
                # Recalculates the total CO2 savings for the item using base_co2 as the fixed value and co2 as the updated total
                item['CO2'] = item['count'] * item['base_CO2']
                break # Stops searching once the item is found and updates it

    # Redirects back to homepage after form submission to display updated data & to prevent resubission on refresh
    return RedirectResponse(url="/", status_code=303)

# Route to save items data to database and reset all items locally
@app.post("/reset", response_class=HTMLResponse)
def renew(request: Request):
    # Saves all items data from session to database before resetting
    try:
        for category in items:
            for item in category['items']:
                if item.get('count', 0) > 0 or item.get('CO2', 0) > 0: # Tries to get 'CO2', if it doesn't exist, it returns 0 instead , to prevent crashes
                    mongo.update_item(category["category"], item["name"], item['count'], item['CO2']) # Updates items count and CO2 by category using the MongoCO2 class defined function

        # Resets locally displayed items
        for category in items:
            for item in category['items']:
                item['count'] = 0 # Resets local count to 0
                item['CO2'] = 0 # Resets local CO2 to 0  

    except Exception as e:
        print(f"Error in /reset: {e}")
        raise e
    
    return RedirectResponse(url="/", status_code=303) # Redirects back to mainpage

# SECURE ROUTE
# Route to reset item counts in database zero
@app.get("/reset_DBS", response_class=HTMLResponse)
def reset_count(request: Request):
    mongo.reset_counts(items)
    return RedirectResponse(url="/", status_code=303) # Redirects back to homepage after resetting counts