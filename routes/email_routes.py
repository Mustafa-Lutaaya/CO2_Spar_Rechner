# FastAPI Components to build the web app.
from fastapi import APIRouter, Request, Form,  Depends # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools s
from fastapi.responses import HTMLResponse, RedirectResponse # Imports response classes to return rendered HTML pages &  to redirect client to another URL after a POST 
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data

# Internal Modules
from schemas.schemas import co2_createitem, pen_user  # Imports request and response schemas respectively
from crud.operations import CRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables
from config.jwt_handler import JWTHandler # Imports JWT Handler Class 

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent
router = APIRouter() #  Creates a router instance to group related routes
crud = CRUD() # Initializes CRUD class instance to perorm DB Operations
templates = Jinja2Templates(directory="templates") # Initializes templates

# EMAIL ROUTES
# Approval User Route 
@router.get("/approve_user")
def approve_user(request: Request, db: Session = Depends(get_db)):

    token = request.query_params.get("token") # Gets token from string
    if not token:
        return RedirectResponse(url="/email/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email
        payload = JWTHandler.decode_token(token)
        email = payload["sub"]

        user = crud.verify_user(db, email) # Finds the user in the pending_users collection by email
        if not user:
            return RedirectResponse(url="/email/unfound", status_code=303) # Redirects to unfound page

        return RedirectResponse(url="/email/approved", status_code=303) # Redirects to approved page
    
    except Exception as e:
        print(f"Error approving user: {e}")
        return RedirectResponse(url="/email/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid
    
# Rejectionn User Route 
@router.get("/reject_user")
def reject_user(request: Request, db: Session = Depends(get_db)):

    token = request.query_params.get("token") # Gets token from string
    if not token:
        return RedirectResponse(url="/email/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email
        payload = JWTHandler.decode_token(token)
        email = payload["sub"]

        user = crud.delete_pen_user(db, email) # Finds the user in the pending_users collection by email
        if not user:
            return RedirectResponse(url="/email/unfound", status_code=303) # Redirects to unfound page

        return RedirectResponse(url="/email/rejected", status_code=303) # Redirects to approved page
    
    except Exception as e:
        print(f"Error approving user: {e}")
        return RedirectResponse(url="/email/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid

@router.get("/approved", response_class=HTMLResponse)
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

@router.get("/rejected", response_class=HTMLResponse)
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

@router.get("/unfound", response_class=HTMLResponse)
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

@router.get("/email/invalid_token", response_class=HTMLResponse)
def invalid_token_page():
    return """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invalid Token</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
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