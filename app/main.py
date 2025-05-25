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
from typing import Optional

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

# Inserts Items into Mongo DB co2 Database if documents empty
if mongo.co2.count_documents({}) == 0:
    mongo.insert_items(items) 

# DEMP PAGE ROUTES
# Route for the demopage ('/') that returns an HTML response displaying items
@app.get("/", response_class=HTMLResponse)
def demo(request: Request):

    # Calculates the total CO2 emission based on item's counts and CO2 per item
    total_co2 = sum(
        (item.get('co2', 0))
        for category in items
        for item in category['items'])
    
    equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how mmuch C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items,  # Passes items data to be rendered
        "equivalents": equivalents, # C02 equivalent in different modes of transport
        "total_co2": total_co2, # Total C02 emitted based on selected items
    }
    # Renders the response
    response = templates.TemplateResponse("demo.html", context)
    return response 

# Route to handle form submissions of incrementing & decrementing counts on demo page
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
    return RedirectResponse(url="/", status_code=303)

# Route to reset all items locally
@app.post("/reset", response_class=HTMLResponse)
def renew(request: Request):
    # Resets locally displayed items
    for category in items:
        for item in category['items']:
            item['count'] = 0 # Resets local count to 0
            item['co2'] = 0 # Resets local CO2 to 0  

    return RedirectResponse(url="/", status_code=303) # Redirects back to demo page

@app.get("/welcome", response_class=HTMLResponse)
def root(request: Request, error: str = None,):
    # Initializes variable to store alert message
    alert = None

    # Checks if an error code was passed and returns an alert message
    if error == "missing_name":
        alert = "Name is required for registration."
    elif error == "user_not_found":
        alert = "User not found or not approved."
    elif error == "missing_password":
        alert = "Password is required for login."
    elif error == "incorrect_password":
        alert = "Incorrect password."
    elif error == "invalid_action":
        alert = "Invalid action."

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "alert": alert # Adds alert to context so it's accessible in the HTML template
    }
    return templates.TemplateResponse(request, "index.html", context)  # Renders the 'index.html' template with data from the context dictionary

# Form Handling Route (Registration & Login)
@app.post("/welcome", response_class=HTMLResponse, )
def handle_form(
    name: Optional[str] = Form(None), 
    email: str = Form(...), 
    action: str = Form(...),
    password: Optional[str] = Form(None),
    ):
    
    # Handles registration form submission
    if action == 'register':
        if not name:
            return RedirectResponse(url="/welcome?error=missing_name", status_code=303) # RedirectS with error code in URL, if name is missing 
        
        # Proceeds with registration
        user = Register(name=name, email=email) # Extracts data accordingly
        mongo.register_user(user) # Stores user data in Database
        EmailHandler.send_to_admin(user.name, user.email) # Notifies Admin of New Registrant
        return RedirectResponse(url="/", status_code=303) # Redirects to back to form page
    
    # Handles login form submission
    elif action == 'login':
        user = mongo.find_user_by_mail(email) # Fetch user info from Database
        if not user:
            return RedirectResponse(url="/welcome?error=user_not_found", status_code=303) # Redirects with error code in URL, if user not found
        
        if not password:
            return RedirectResponse(url="/welcome?error=missing_password", status_code=303) # Redirects with error code in URL, if password is missing
        
        hash_pwd = user.get("hash_pwd") # Gets hashed password then checks it for verficiation
        if not PWDHandler.verify_password(password, hash_pwd):
            return RedirectResponse(url="/welcome?error=incorrect_password", status_code=303)
        
        # Sets cookie with user_name
        response = RedirectResponse(url="/main", status_code=303) # Redirects to homepage if all checks out
        response.set_cookie(key="user_name", # Cookie key used to identify user session
                            value=user.get("name"),  # Store the user's name as the value
                            max_age=1800, # Cookie expires in 30 minutes
                            httponly=True, # Cookie cant be accesed by JS and protects from XSS .. Cross-Site Scripting attacks
                            samesite="lax", # Prevents Cross-Site Request Forgery (CSRF) attacks where bad sites try to trick the browser into making unwanted requests with the cookie.
                            secure=True # Cookie is never sent over unencrpted HTTP 
                            )
        response.set_cookie(key="welcome_message", value=f"Welcome {user.get('name')}!", max_age=1) # Sets cookie to display short-lived welcome message
        return response
    
    else:
        return RedirectResponse(url="/welcome?error=invalid_action", status_code=303)  # Handles unknown form action

# Approval User Route 
@app.get("/approve_user")
def approve_user(request: Request):

    token = request.query_params.get("token") # Gets token from string
    if not token:
        return RedirectResponse(url="/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email, name and action
        payload = JWTHandler.decode_token(token)
        email = payload["sub"] # Extracts user's email from token payload
        name = payload["name"] # Extracts user's name
        action = payload["action"] # Extracts action

        user = mongo.find_user_by_email(email) # Finds the user in the pending_users collection by email
        if not user:
            return RedirectResponse(url="/unfound", status_code=303) # Redirects to unfound page

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

        return RedirectResponse(url="/approved", status_code=303) # Redirects to approved page
    
    except Exception as e:
        print(f"Error approving user: {e}")
        return RedirectResponse(url="/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid
    
# Rejection User Route 
@app.get("/reject_user")
def reject_user(request: Request):

    token = request.query_params.get("token") # Gets token from string 
    if not token:
        return RedirectResponse(url="/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email, name and action
        payload = JWTHandler.decode_token(token)
        email = payload["sub"] # Extracts user's email from token payload
        action = payload["action"] # Extracts action


        user = mongo.find_user_by_email(email) # Finds the user in the pending_users collection by email
        if not user:
            return RedirectResponse(url="/unfound", status_code=303) # Redirects to unfound page

        mongo.delete_user_by_email(email) # Deletes user from pending collection

        return RedirectResponse(url="/rejected", status_code=303) # Redirects to rejected page
    
    except Exception as e:
        print(f"Error approving user: {e}")
        return RedirectResponse(url="/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid

# Route for the homepage ('/main') that returns an HTML response displaying items
@app.get("/main", response_class=HTMLResponse)
def main(request: Request):

    # Personalized welcome text initialization
    user_name = request.cookies.get("user_name")
    welcome_message = request.cookies.get("welcome_message")

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
        "sorted_items": sorted_items, # Sorted list of updated items for display
        "welcome_message": welcome_message # Displays welcome text
    }
    # Renders the response
    response = templates.TemplateResponse("main.html", context)

    # Clears welcome text after first display
    if welcome_message:
        response.delete_cookie("welcome_message")
    return response 

# Route to handle form submissions of incrementing & decrementing counts
@app.post("/main", response_class=HTMLResponse)
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
@app.post("/main/reset", response_class=HTMLResponse)
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

# Route to save events data to database and reset all items locally
@app.post("/main/logout", response_class=HTMLResponse)
def logout(request: Request):

    user_name = request.cookies.get("user_name") # Uses cookie to get user name

    # Checks if there were actual calculations during sessions
    totals, session_count = AppUtils.calculate_total(mongo.get_all_sessions()) # Gets All Sessions Function loops through all stored sessions in the Database, then passes them to AppUtils, calculates total function to calculate cumulative totals and number of sessions

    # If data was exchanged during the event, then its collected and saved into the logs event collection
    if session_count > 0:
        updated_items = mongo.get_updated_items() # Fetches the latest items data from the MongoDB database
        rearranged_items = AppUtils.rearrange_updated_items(updated_items)  # Single Lists MongoDB items
        sorted_items = AppUtils.sort_updated_items(rearranged_items) # Sorts items by 'count' in descending order with most used items coming first
        mongo.log_out(user_name, sessions=session_count, sorted_items=sorted_items, total=totals)
        mongo.reset_counts(items) # Resets items database count 
        mongo.clear_sessions() # Deletes all documents inside the sessions collection

    # Prepares redirect response and clears the cookie
    response = RedirectResponse(url="/", status_code=303) 
    response.delete_cookie("user_name") # Clears cookie
    return response # Redirects to landing page 
    
# SECURE ROUTES
# Route to reset item counts in database to zero
@app.get("/main/reset_DBS", response_class=HTMLResponse)
def reset_count(request: Request):
    mongo.reset_counts(items)
    return RedirectResponse(url="/main", status_code=303) # Redirects back to homepage after resetting counts

# Route to clear all exchange sessions from the database
@app.get("/main/clear_SOS", response_class=HTMLResponse)
def clear_sessions(request: Request):
    mongo.clear_sessions() # Deletes all documents inside the sessions collection
    return RedirectResponse(url="/main", status_code=303) # Redirects back to homepage after clearing sessions


# ROUTES WITH HTML CODE
@app.get("/approved", response_class=HTMLResponse)
def approved_page():
    return """
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Approved</title>

    <!-- Bootstrap CSS Loader For Responsive Styling & Layout -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap CSS FOr Loading Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Custom CSS File in 'static' Folder -->
    <link rel="stylesheet" href="/static/styles.css">

    <!-- Site Favicon Displayed In The Browser Tab -->
    <link href="/static/favicon.png" rel="icon">
    </head>

    <body>
    <div class="container mt-5 text-center text-danger">
        <div class="row align-items-center">
            <div class="col">
                <img id="logo" class="WLogo" src="/static/logo1.png" alt="Logo">
            </div>
        </div>
    </div>

    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>

    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>


    <!-- Message Placement -->
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h4 class="text-center"><strong>youngcaritas x Kleidertausch CO₂-Rechner</strong></h4>
                <br/>
                <div class="alert alert-success text-center" role="alert">
                <h6>User approved successfully</h6>
                </div>
                <h6 class="text-center"><strong>You may now close this window.</strong></h6>
            </div>
        </div>
    </div>

</body>
</html>
    """


@app.get("/rejected", response_class=HTMLResponse)
def rejected_page():
    return """
   <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Rejected</title>

    <!-- Bootstrap CSS Loader For Responsive Styling & Layout -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap CSS FOr Loading Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Custom CSS File in 'static' Folder -->
    <link rel="stylesheet" href="/static/styles.css">

    <!-- Site Favicon Displayed In The Browser Tab -->
    <link href="/static/favicon.png" rel="icon">
    </head>

    <body>
    <div class="container mt-5 text-center text-danger">
        <div class="row align-items-center">
            <div class="col">
                <img id="logo" class="WLogo" src="/static/logo1.png" alt="Logo">
            </div>
        </div>
    </div>


    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>

    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>


    <!-- Message Placement -->
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h4 class="text-center"><strong>youngcaritas x Kleidertausch CO₂-Rechner</strong></h4>
                <br/>
                <div class="alert alert-success text-center" role="alert">
                <h6>User rejected successfully</h6>
                </div>
                <h6 class="text-center">You may now close this window.</h6>
            </div>
        </div>
    </div>

    </body>
    </html>
    """

@app.get("/unfound", response_class=HTMLResponse)
def unfound_page():
    return """
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Not Found</title>

    <!-- Bootstrap CSS Loader For Responsive Styling & Layout -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap CSS FOr Loading Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Custom CSS File in 'static' Folder -->
    <link rel="stylesheet" href="/static/styles.css">

    <!-- Site Favicon Displayed In The Browser Tab -->
    <link href="/static/favicon.png" rel="icon">
    </head>

    <body>
    <div class="container mt-5 text-center text-danger">
        <div class="row align-items-center">
            <div class="col">
                <img id="logo" class="WLogo" src="/static/logo1.png" alt="Logo">
            </div>
        </div>
    </div>

    
    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>
    
    <div class="container mt-5 text-center">
        <div class="row align-items-center">
            <div class="col">
            </div>
        </div>
    </div>



    <!-- Message Placement -->
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h4 class="text-center"><strong>youngcaritas x Kleidertausch CO₂-Rechner</strong></h4>
                <br/>
                <div class="alert alert-danger text-center" role="alert">
                <h6>User not found</h6>
                </div>
                <h6 class="text-center"><strong>You may now close this window.</strong></h6>
            </div>
        </div>
    </div>

    </body>
    </html>
    """

@app.get("/invalid_token", response_class=HTMLResponse)
def invalid_token_page():
    return """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invalid Token</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <link rel="stylesheet" href="/static/styles.css">
        <link href="/static/favicon.png" rel="icon">
    </head>
    <body>
        <div class="container mt-5 text-center text-danger">
            <div class="row align-items-center">
                <div class="col">
                    <img id="logo" class="WLogo" src="/static/logo1.png" alt="Logo">
                </div>
            </div>
        </div>
        
        
        <div class="container mt-5 text-center">
            <div class="row align-items-center">
                <div class="col">
                </div>
            </div>
        </div>

        <div class="container mt-5 text-center">
            <div class="row align-items-center">
                <div class="col">
                </div>
            </div>
        </div>

        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <h4 class="text-center"><strong>youngcaritas x Kleidertausch CO₂-Rechner</strong></h4>
                    <br/>
                    <div class="alert alert-danger text-center" role="alert">
                        <h6>Invalid or expired token</h6>
                    </div>
                    <h6 class="text-center">Please restart the registration process or close this window.</h6>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
