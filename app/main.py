# FastAPI Components to build the web app.
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

# Utilities
from datetime import datetime

# Initializes FastAPI Web Application
app = FastAPI() 