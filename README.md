### CO₂ Spar Rechner
This is the backend for the **YoungCaritas Kleidertausch CO₂ Savings Calculator**, developed as a final semester project to improve the original system with:

-  A complete admin dashboard
-  User registration & approval
-  Persistent data saving via PostgreSQL
-  A flexible CO₂ item management system

---

### Features

- Admins can now:
  - Add, edit, or delete clothing items with CO₂ base values
  - Manage user registrations (approve/reject)
  - View & interact with data using a built-in UI or Swagger documentation
- Built with **FastAPI**, **PostgreSQL**, **Jinja2**, and **Docker**
- Swagger UI for API exploration: `/docs`
- Admin UI: `/UI/admin`

---
## 🔧 Environment Setup (Required First!)

Before running the app (via Makefile or Docker), you **must create a `.env` file** in the project root:

### 1. Create `.env` file:
# A: For Local Development (Makefile)
DATABASE_URL=postgresql://admin:password@localhost:5432/spar_db
JWT=your_jwt_secret
ADMIN_EMAIL=your_admin_email@example.com
SENDER_EMAIL=your_email@example.com
EMAIL_PASSWORD=your_email_password
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=spar_db

# B: For Docker Usage
DATABASE_URL=postgresql://admin:password@db:5432/spar_db


2. ## Generate a JWT Secret:
- cd config

- Run: python generate_jwt_secret.py

- Copy the output and paste it into the JWT field in your .env file.


### Local Development Setup - Makefile Method

# Download and install Make first

# 1. Clone the Repository
git clone https://github.com/Mustafa-Lutaaya/CO2_Spar_Rechner
cd CO2-Spar-Rechner

# 2. Setup Virtual Enviroment
make create
make act

# 3.  Install Dependencies
make install

# 4.  Start the Server
make start
Visit http://localhost:8000 to access the system.


### Testing 
Run tests with: make pytest

---
### Docker Setup
- You can also run the application using Docker.

# 2.  Start Services
docker-compose up --build

# 3. Access
-App: http://localhost:8000

-Swagger Docs: http://localhost:8000/docs

-Admin UI: http://localhost:8000/UI/admin

### Tech Stack
- Backend Framework: FastAPI 

- Database: PostgreSQL — Relational database for storing users, items, and CO₂ values

- Frontend (UI Layer): Jinja2 templating engine used to build admin/user-facing UI

- Authentication & Security: JWT (JSON Web Tokens)

- Secrets (Python): Used to generate secure JWT keys

- Environment & Dependency Management: Makefile — For simple local automation (virtualenv setup, running server, tests)

-Python virtualenv: Isolated environment for Python dependencies

- DevOps / Containerization: Docker Containerized environment for the app and database

- docker-compose: For managing multi-container setup (FastAPI + PostgreSQL)

- Testing: pytest — Unit and integration tests for API and database logic

- API Documentation: Swagger UI (via FastAPI) — Auto-generated API docs available at /docs

### Maintainers: 

Mustafa Lutaaya
