# FastAPI Components to build the web app.
from fastapi import APIRouter, Request, Form,  Depends # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools s
from fastapi.responses import HTMLResponse, RedirectResponse # Imports response classes to return rendered HTML pages &  to redirect client to another URL after a POST 
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data

# Internal Modules
from schemas.schemas import co2_createitem, pen_user  # Imports request and response schemas respectively
from crud.operations import CRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent
router = APIRouter() #  Creates a router instance to group related routes
crud = CRUD() # Initializes CRUD class instance to perorm DB Operations
templates = Jinja2Templates(directory="templates") # Initializes templates

# FORM PAGE ROUTES
# Form Handling Route (Registration & Login)
@router.get("/admin", response_class=HTMLResponse)
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
    elif error == "short_name":
        alert = "Name must be at least 4 characters."
    elif error == "user_exists":
        alert = "User Account already exists."

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "alert": alert # Adds alert to context so it's accessible in the HTML template
    }
    return templates.TemplateResponse("admin.html", context)  # Renders the 'index.html' template with data from the context dictionary


# Registration Route
@router.post("/admin/register", response_class=HTMLResponse)
def registration_route(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
    ):
    if len(name) < 4:
        return RedirectResponse(url="/UI/admin?error=short_name", status_code=303)
    
    if not name:
            return RedirectResponse(url="/UI/admin?error=missing_name", status_code=303) # Redirects with error code in URL, if name is missing 

    existing_user = crud.get_pen_user_by_email(db, email=email)  # Checks if user already exists
    if existing_user:
         return RedirectResponse(url="/UI/admin?error=user_exists", status_code=303)
    
        
    verified= crud.get_ver_user_by_email(db, email=email) # Checks if user is verified
    if verified:
         return RedirectResponse(url="/UI/admin?error=user_exists", status_code=303)
    
    new_user = pen_user(name=name, email=email)
    crud.register_user(db, new_user)
    
    return templates.TemplateResponse("admin.html", {"request": request, "success": "registered"})

# Login Route
@router.post("/admin/login", response_class=HTMLResponse)
def login_route(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    ):
    
    # Checks if email and password are provided
    if not email:
        return RedirectResponse(url="/UI/admin?error=missing_email", status_code=303)

    if not password:
        return RedirectResponse(url="/UI/admin?error=missing_password", status_code=303)

    # Checks if user exists and is verified
    user = crud.get_ver_user_by_email(db, email)
    if not user:
        return RedirectResponse(url="/UI/admin?error=user_not_found", status_code=303)

    # Confirms password is correct
    valid_user = crud.confirm_password(db, password=password, email=email)
    if not valid_user:
        return RedirectResponse(url="/UI/admin?error=incorrect_password", status_code=303)

    # Login successful
    return RedirectResponse(url="/UI", status_code=303)

# GET route for admin URL "/admin" returning an HTML page
@router.get("/", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db), msg: str = ""): # Injects DB Session dependency plus message to display back to user as a string
   items = crud.get_all_items(db) # Fetches all items from the database using the CRUD class.
   pen_users = crud.get_all_pen_users(db) # Fetches all pending users from the database using the CRUD class.
   con_users = crud.get_all_ver_users(db) # Fetches all verified users from the database using the CRUD class.
   # Renders to the template
   return templates.TemplateResponse("index.html",
                                     {"request": request, 
                                        "items": items,
                                        "msg": msg, 
                                        "pen_users":pen_users, 
                                        "con_users":con_users})

# GET route at "/search" to handle item lookup by name.
@router.get("/search", response_class=HTMLResponse)
def search_item(request: Request, name: str, db: Session = Depends(get_db)):
    item = crud.get_itemby_name(db, name)  # Searches for the item in the database by name.
    
    # Renders the main template with item and a success message, if item is found
    if item:
        return templates.TemplateResponse("index.html", {"request": request,"items": [item],"msg": "found"})
    
    # Redirects back to the main page with a "notfound" message, if item is not found
    return RedirectResponse("/UI?msg=notfound", status_code=303)

# POST route at "/admin/verify" to handle form submissions to create new users.
@router.post("/verify")  # Accepts form data for email for verification
def verify_user(email: str = Form(...), db: Session = Depends(get_db)):  
    verification = crud.verify_user(db, email)
    
    if not verification:  # Checks if a pending user with name already exists in the database.
        return RedirectResponse("/UI?msg=exists", status_code=303)  # Redirects back to home page without creating duplicate, if it exists
    
    return RedirectResponse("/UI?msg=created", status_code=303) # Redirects back to home page after successful creation

# POST route at "/admin/delete" to delete verified user
@router.post("/delete_con")  # Accepts form data for email for verification
def delete_user(email: str = Form(...),db: Session = Depends(get_db)):  
    deletion = crud.delete_ver_user(db, email)
    
    if not deletion:  # Checks if user was deleted
        return RedirectResponse("/UI?msg=notfound", status_code=303)  # Redirects back to home page without deleting
    
    return RedirectResponse("/UI?msg=deleted", status_code=303) # Redirects back to home page after successful deletion

# POST route at "/admin/delete" to delete pending user
@router.post("/delete_pen")  # Accepts form data for email for deletion
def delete_user(email: str = Form(...),db: Session = Depends(get_db)):  
    deletion = crud.delete_pen_user(db, email)
    
    if not deletion:  # Checks if user was deleted
        return RedirectResponse("/UI?msg=notfound", status_code=303)  # Redirects back to home page without deleting
    
    return RedirectResponse("/UI?msg=deleted", status_code=303) # Redirects back to home page after successful deletion

# POST route at "/create" to handle form submissions to create new items.
@router.post("/create")  # Accepts form data for either category or name or base_co2 or all and DB session.
def create_item(
    category: str = Form(...),
    name: str = Form(...),  
    base_co2: float = Form(...),
    db: Session = Depends(get_db)):  
    
    if crud.get_itemby_name(db, name):  # Checks if an item with this name already exists in the database.
        return RedirectResponse("/UI?msg=exists", status_code=303)  # Redirects back to home page without creating duplicate, if it exists
    
    crud.create_item(db, co2_createitem(category=category, name=name, base_co2=base_co2)) #  Or Else creates the new item by wrapping the data in the Pydantic schema.
    return RedirectResponse("/UI?msg=created", status_code=303) # Redirects back to home page after successful creation

# POST route at "/update" for updating existing items from form data.
@router.post("/update") 
def update_item(  # Accepts form data for either category or name or base_co2 or all and DB session.
    original_name: str = Form(...),
    category: str = Form(...),
    name: str = Form(...),  
    base_co2: float = Form(...),
    db: Session = Depends(get_db)):

    # Checks if the item to update exists
    if not crud.get_itemby_name(db, original_name):
        return RedirectResponse("/UI?msg=notfound", status_code=303)

    crud.update_item(db, original_name, co2_createitem(name=name, category=category, base_co2=base_co2))  # Performs the update operation using the original name
    return RedirectResponse("/UI?msg=updated", status_code=303)  # Redirects back to home page after update.

# POST route at "/delete" for deleting an item specified by name.
@router.post("/delete")
def delete_item(name: str = Form(...), db: Session = Depends(get_db)): # Accepts the name of the item to delete and DB session.
    # Checks if the item to delete exists
    if not crud.get_itemby_name(db, name):
        return RedirectResponse("/UI?msg=notfound", status_code=303)
    
    crud.delete_item(db, name)  # Performs the deletion from the database.
    return RedirectResponse("/UI?msg=deleted", status_code=303)  # Redirects back to home page after deletion.