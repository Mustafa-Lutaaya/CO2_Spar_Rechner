# FastAPI Components to build the web app.
from fastapi import FastAPI, Request, Form  # Imports FastAPI , Request for handling HTTP requests & Form to accept data submitted via POST Requests
from fastapi.responses import HTMLResponse, RedirectResponse # Specifies that a route returns HTML
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support

# Utilities & CO2 Connection Class
from datetime import datetime
from sqlite.sql_lite import CO2
from pathlib import Path # Provides object-oriented file system paths

# Initializes FastAPI Web Application
app = FastAPI() 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

# Database Initialization
berechner_db = CO2("Berechner.db") # Creates an instance of  CO2 class from sqlite.sql_lite.
table_name = "CO2_Spar" # Stores Table Name
items = berechner_db.get_data_by_category(table_name) # Retrieves data grouped by category from table

# Route for the homepage ('/') that returns an HTML response displaying items
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items  # Passes items data to be rendered
    }
    return templates.TemplateResponse(request, "index.html", context)  # Renders the 'index.html' template with data from the context dictionary