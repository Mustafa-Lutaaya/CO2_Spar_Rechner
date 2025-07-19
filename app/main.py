from fastapi import FastAPI, Request # Imports FastAPI class to create the main app instance
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.responses import RedirectResponse, HTMLResponse  # For returning HTML content in the welcome route
from routes.ui_routes import router as ui_router  # Imports UI router instance from the ui_routes module and rename it as ui_router
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support
from pathlib import Path # Provides object-oriented file system paths
from fastapi.middleware.cors import CORSMiddleware # Imports CORS to enable communication beteween frontend and backend
from crud.sync_operations import sync_cloud_to_local, sync_local_to_cloud
from database.data import Co2
import os

app = FastAPI(
    title="CO2 Spar Rechner",
    description="Welcome to the CO2 Savings Calculator Demo Page.", # Initializes the FastAPI application
    version="1.0.0"
) 

app.mount("/static", StaticFiles(directory="static"), name="static") # Mounts the 'static' Files directory making it accessible via '/static' URL 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

app.include_router(ui_router, prefix="/UI", tags=["UI"])# Adds the User Interaction router to the main app, prefixing all its routes with "/UI" meaning every path inside the UI_router will be available under "/UI". The tags parameter groups the routes under an UI tag in Swagger UI


ENV = os.getenv("ENV", "dev")
if ENV not in ["dev", "prod"]:
    raise ValueError("Invalid ENV setting. Must be 'dev' or 'prod'.")

@app.on_event("startup")
def sync_on_startup():
    try:
        cloud = Co2()
        local = Co2()

        if cloud.is_online:
            sync_cloud_to_local(cloud.client, local.client)
            sync_local_to_cloud(local.client, cloud.client)
            print("MongoDB sync complete")
        else:
            print("Cloud not reachable. Skipping sync.")
    except Exception as e:
        print(f"Sync error: {e}")

@app.get("/", response_class=RedirectResponse)
def root_redirect():
    if ENV == "prod":
        return RedirectResponse(url="https://co2-spar-rechner.onrender.com")
    else:
        return RedirectResponse(url="http://localhost:5000/UI")

# Domains allowed to make requests to the backend
origins = [
    "http://localhost:5050",   # Local dev server
    "http://127.0.0.1:5050",
    "https://co2-rechner.onrender.com"
]

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Allows requests from these origins
    allow_credentials=True,     # Allows cookies and authentication headers
    allow_methods=["*"],        # Allows all HTTP methods 
    allow_headers=["*"],        # Allows all headers
)