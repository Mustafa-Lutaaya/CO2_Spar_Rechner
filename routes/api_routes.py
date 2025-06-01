# FastAPI Components to build the web app.
from fastapi import APIRouter, HTTPException, Depends, Body # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools such as getting DB Session
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data
from typing import List

# Internal Modules
from schemas.schemas import co2_createitem, co2_itemread, pen_user, ver_user, user  # Imports request and response schemas respectively
from crud.operations import CRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports database configurations & dependency function to provide a database session for each request

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet present
router = APIRouter() #  Creates a router instance to group related routes
crud = CRUD() # Initializes CRUD class instance to perorm DB Operations

# Route to get all items from the database
@router.get("/items", response_model=list[co2_itemread]) # GET /items/ returns a list of items
def read_all(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return crud.get_all_items(db) # Calls Crud function to retrieve all items and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single item by name
@router.get("/items/{name}", response_model=co2_itemread) # GET /items/{name} fetches one item
def getitem(name: str, db: Session = Depends(get_db)):
    item = crud.get_itemby_name(db, name) # Calls the CRUD function to get the item by name
    if not item:
        raise HTTPException(status_code=404, detail="Item not found") # Returns 404 if item doesn't exist
    return item  # Returns the found item

# Route to create a new item in the database
@router.post("/items", response_model=co2_itemread) # POST /items/ with repsonse using Pydantic schema
def createitem(item: co2_createitem, db: Session = Depends(get_db)): # Injects Db Session dependency
    exisiting = crud.get_itemby_name(db, item.name) # Checks if item already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="Item already exists") # Prevents Duplicates
    try:
        return crud.create_item(db, item) # Calls crud function to add item and return created item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors

# Route to modify an exisiting item using the name
@router.put("/items/{name}", response_model=co2_itemread) # PUT /items/{name} updates an existing item
def updateitem(name: str, item: co2_createitem, db: Session = Depends(get_db)):
    updated_item = crud.update_item(db, name, item) # Calls crud update function that grabs a new item and tries to updated it 
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found to update") # Raises error if item isnt found
    return updated_item

# Route to delete an item identified by Name
@router.delete("/items/{name}", response_model=co2_itemread) # DELETE /items/{name} removes an item
def deleteitem(name: str, db: Session = Depends(get_db)): 
    deleted_item = crud.delete_item(db, name)  # Calls CRUD delete function that finds and deletes item
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Item not found for deletion") # Raises error if item isnt found
    return deleted_item # Returns the deleted item

# Route to get all pending users from the database
@router.get("/pen_users", response_model=list[pen_user]) # GET /pen_users/ returns a list of pending users
def show_pen_users(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return crud.get_all_pen_users(db) # Calls Crud function to retrieve all pending users and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single pending user by email
@router.get("/pen_user/{email}", response_model=pen_user) # GET /pen_user/{email} fetches one user
def get_pen(email: str, db: Session = Depends(get_db)):
    user = crud.get_pen_user_by_email(db, email) # Calls the CRUD function to get the user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found") # Returns 404 if user doesn't exist
    return user # Returns the found user

# Route to create a new user in the database
@router.post("/pen_user", response_model=pen_user) # POST /pen_user/ with repsonse using Pydantic schema
def register_user(new_user: pen_user, db: Session = Depends(get_db)): # Injects Db Session dependency
    
    exisiting = crud.get_pen_user_by_email(db, new_user.email) # Checks if user already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="User email already exists") # One email should be used by one user
    
    verified= crud.get_ver_user_by_email(db, new_user.email) # Checks if verified
    if verified:
        raise HTTPException(status_code=400, detail="User Account exists")
    
    try:
        return crud.register_user(db, new_user) # Calls crud function to register new user and add them to pending database
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors

# Route to delete a pending user identified by email
@router.delete("/pen_user/{email}", response_model=pen_user) # DELETE /pen_user/{email} removes a pending user 
def delete_pen_user(email: str, db: Session = Depends(get_db)): 
    deleted_user = crud.delete_pen_user(db, email)  # Calls CRUD delete function that finds and deletes user using email
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found for deletion") # Raises error if pending_user isnt found
    return deleted_user # Returns the deleted user

# Route to delete all pending users 
@router.delete("/pen_users", response_model=List[pen_user]) # DELETE /pen_user/{email} removes all pending users 
def delete_pen_users(db: Session = Depends(get_db)): 
    deleted_users = crud.delete_pen_users(db)  # Calls CRUD delete function deletes all pending users
    if not deleted_users:
        raise HTTPException(status_code=404, detail="User's arent found for deletion") # Raises error if pending users aren't found
    return deleted_users # Returns the deleted user

# Route to verify a pending user
@router.post("/ver_user/{email}", response_model=ver_user) # POST /ver_user/{email} verifies a pending user using the email
def verify_pending_user(email: str,  db: Session = Depends(get_db)):
    verification = crud.verify_user(db, email) # Calls CRUD verify function that verifies user and adds to verified users taböe

    if not verification:
        raise HTTPException(status_code=404, detail="Pending user not found") # Raises error if user isnt found
    
    verified_user = verification

    return verified_user  # Returns the verified user without password

# Route to change password
@router.put("/ver_user/{email}/change_pwd", response_model=ver_user) # PUT /ver_user/{email}/change_pwd changes the password
def change_password(email: str, new_password: str = Body(..., embed=True), db: Session = Depends(get_db)):
    updated_user = crud.change_password(db, email, new_password) # Calls crud change password function
    if not updated_user:
        raise HTTPException(status_code=400, detail="User not found or password invalid") # Raises error if user isnt found
    return updated_user  # Returns the updated user

# Route to get all verified users from the database
@router.get("/ver_users", response_model=list[ver_user]) # GET /ver_users/ returns a list of verified users
def show_ver_users(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return crud.get_all_ver_users(db) # Calls Crud function to retrieve all verified users and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP with status code 500

# Route to get single verified user by email
@router.get("/ver_user/{email}", response_model=ver_user) # GET /ver_user/{email} fetches one verified user
def get_ver(email: str, db: Session = Depends(get_db)):
    user = crud.get_ver_user_by_email(db, email) # Calls the CRUD function to get the user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found") # Returns 404 if user doesn't exist
    return user # Returns the found user

# Route to delete a verified user using an email
@router.delete("/ver_user/{email}", response_model=ver_user) # DELETE /ver_user/{email} removes a verified user 
def delete_ver_user(email: str, db: Session = Depends(get_db)): 
    deleted_user = crud.delete_ver_user(db, email)  # Calls CRUD delete function that finds and deletes user using email
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found for deletion") # Raises error if verified_user isnt found
    return deleted_user # Returns the deleted user

# Route to delete all verified users 
@router.delete("/ver_users", response_model= List[ver_user]) # DELETE /ver_users removes all verified users
def delete_ver_users(db: Session = Depends(get_db)): 
    deleted_users = crud.delete_ver_users(db)  # Calls CRUD delete function that deletes all users
    if not deleted_users:
        raise HTTPException(status_code=404, detail="Users not found for deletion") # Raises error if verififed users arent found
    return deleted_users # Returns deleted users
