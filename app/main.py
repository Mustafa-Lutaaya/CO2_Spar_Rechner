# FastAPI Components to build the web app.
from fastapi import FastAPI, Request, Form, HTTPException , Response # Imports FastAPI , Request for handling HTTP requests & Form to accept data submitted via POST Requests plus HTTPException & Response
from fastapi.responses import HTMLResponse, RedirectResponse # Specifies that a route returns HTML
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support

# Utilities & Database Connection Classes
from dotenv import load_dotenv # Loads secrets from .env.
import os# Accesses the environment variables..
from datetime import datetime
from pathlib import Path # Provides object-oriented file system paths
from sqlite.sql_lite import CO2 # Imports the CO2Connection Class for sql
from mongo.mongo import Co2, Register, Login # Imports the Co2Connection Class for MongoDB Together With Login & Registration Schemas
from utilities.utils import AppUtils # Imports the data processing functions

from config.jwt_handler import JWTHandler
from config.pwd_handler import PWDHandler
from config.mail_handler import EmailHandler

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

# Route for the landingpage ('/') that returns an HTML response displaying
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
       
    context = {
        "request": request, # Passes the request for Jinja2 to access
    }
    return templates.TemplateResponse(request, "index.html", context)  # Renders the 'index.html' template with data from the context dictionary

# Registraton Route
@app.post("/", response_class=HTMLResponse)
def register_user(name: str = Form(...), email: str = Form(...), action: str = Form(...)):
    if action == 'register':
        user = Register(name=name, email=email) # Extracts data accordingly
        mongo.register_user(user) # Stores user data in Database
        EmailHandler.send_to_admin(user.name, user.email) # Notifies Admin of New Registrant
    return RedirectResponse(url="/", status_code=303) # Redirects to back to landing page

# Login route to redirect to homepage
@app.post("/login", response_class=HTMLResponse)
def login_user(user: Login):
    return RedirectResponse(url="/main", status_code=303) # Redirects to homepage

# Approve User Route 
@app.get("/approve_user")
def approve_user(request: Request):
    user = None # Sets user as none 

    token = request.query_params.get("token") # Gets token from string
    if not token:
        raise HTTPException(status_code=400, detail="Token not provided") # Returns a 400 Bad Request error, if token is missing
    
    try:
        # Decodes token and extracts email, name and action
        payload = JWTHandler.decode_token(token)
        email = payload["sub"] # Extracts user's email from token payload
        name = payload["name"] # Extracts user's name
        action = payload["action"] # Extracts action

        if action != "approve":
            raise HTTPException(status_code=403, detail="Invalid action") # Validates that the action in token is "approve"
        
        user = mongo.find_user_by_email(email) # Finds the user in the pending_users collection by email
        if not user:
            raise HTTPException(status_code=404, detail="User not found") # Raises 404 Not Found error, If no user found

        password = PWDHandler.generate_password() # Generates a random password for the approved user
        hash_pwd = PWDHandler.hash_password(password)  # Hashes the generated password before storing it

        # Prepares the user document to insert into authorized_users collection
        auth_user = {
            "name": user["name"],
            "email": user["email"],
            "hash_pwd": hash_pwd,
            "approved": datetime.utcnow()  # Timestamp of approval
        }

        mongo.authenticate_user(auth_user) # Insert the authenticated user data into the authenticated_users collection
        mongo.delete_user_by_email(email) # Deletes user from pending collection

        EmailHandler.send_to_user(name, email, password) # Notifies user of approval and provides them with login data

        return Response(content="User approved successfully!", status_code=200)
    
    except Exception as e:
        print(f"Error approving user: {e}")
        raise HTTPException(status_code=400, detail=str(e)) # Catches any exception and return a 400 error with the exception message

# Route for the homepage ('/main') that returns an HTML response displaying items
@app.get("/main", response_class=HTMLResponse)
def root(request: Request):
    global total_co2

    # Calculates the total CO2 emission based on item's counts and CO2 per item
    total_co2 = sum(
        (item.get('co2', 0))
        for category in items
        for item in category['items'])
    
    equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how mmuch C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function
    totals, session_count = AppUtils.calculate_total(mongo.get_all_sessions()) # Gets All Sessions Function loops through all stored sessions in the Database, then passes them to AppUtils, calculates total function to calculate cumulative totals and number of sessions
    updated_items = mongo.get_updated_items() # Fetches the latest items data from the MongoDB database
    rearranged_items = AppUtils.rearrange_updated_items(updated_items)  # Single Lists MongoDB items
    sorted_items = AppUtils.sort_updated_items(rearranged_items) # Sorts items by 'count' in descending order with most used items coming first

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items,  # Passes items data to be rendered
        "equivalents": equivalents, # C02 equivalent in different modes of transport
        "total_co2": total_co2, # Total C02 emitted based on selected items
        "totals": totals, # Cumulative totals of all sessions
        "session_count": session_count,  # Number of sessions stored
        "sorted_items": sorted_items # Sorted list of updated items for display
    }
    return templates.TemplateResponse(request, "main.html", context)  # Renders the 'index.html' template with data from the context dictionary

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
                item['co2'] = item['count'] * item['base_CO2']
                break # Stops searching once the item is found and updates it

    # Redirects back to homepage after form submission to display updated data & to prevent resubission on refresh
    return RedirectResponse(url="/main", status_code=303)

# Route to save items data to database and reset all items locally
@app.post("/reset", response_class=HTMLResponse)
def renew(request: Request):
    # Saves all items data from session to database before resetting
    try:
        exc_items = {} 

        # Update items and collects exchanged items
        for category in items:
            for item in category['items']:
                if item.get('count', 0) > 0 or item.get('co2', 0) > 0: # Tries to get 'CO2', if it doesn't exist, it returns 0 instead , to prevent crashes
                    mongo.update_item(category["category"], item["name"], item['count'], item['co2']) # Updates items count and CO2 by category using the MongoCO2 class defined function
                    
                    # Ensures a list exists for each category
                    if category['category'] not in exc_items:
                        exc_items[category["category"]] = []
                    
                    exc_items[category["category"]].append({
                        "name": item["name"],
                        "count": item["count"],
                        "co2": item["co2"]
                    })

        if total_co2 > 0:
            equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how much C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function
            mongo.insert_session(total_co2, equivalents, exc_items) # Inserts exchanged items and sessions for a participant

        # Resets locally displayed items
        for category in items:
            for item in category['items']:
                item['count'] = 0 # Resets local count to 0
                item['co2'] = 0 # Resets local CO2 to 0  

    except Exception as e:
        print(f"Error in /reset: {e}")
        raise e
    
    return RedirectResponse(url="/main", status_code=303) # Redirects back to mainpage

# SECURE ROUTES
# Route to reset item counts in database to zero
@app.get("/reset_DBS", response_class=HTMLResponse)
def reset_count(request: Request):
    mongo.reset_counts(items)
    return RedirectResponse(url="/main", status_code=303) # Redirects back to homepage after resetting counts

# Route to clear all exchange sessions from the database
@app.get("/clear_SOS", response_class=HTMLResponse)
def clear_sessions(request: Request):
    mongo.clear_sessions() # Deletes all documents inside the sessions collection
    return RedirectResponse(url="/main", status_code=303) # Redirects back to homepage after clearing sessions