# FastAPI Components to build the web app.
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

# Utilities & CO2 Connection Class
from datetime import datetime
from sqlite.sql_lite import CO2

# Initializes FastAPI Web Application
app = FastAPI() 

# Database Initialization
berechner_db = CO2("Berechner.db") # Creates an instance of  CO2 class from sqlite.sql_lite.
table_name = "CO2_Spar" # Stores Table Name
items = berechner_db.get_data_by_category(table_name) # Retrieves data grouped by category from table
print(items) 