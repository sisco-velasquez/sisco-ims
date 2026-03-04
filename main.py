import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import auth, inventory, mpesa, sms

# 1. Initialize the app
app = FastAPI()

# 2. Simple CORS (So your HTML can talk to this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Create the database tables as soon as this file loads
init_db()

# 4. Include your routes
app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(mpesa.router)
app.include_router(sms.router)


if __name__ == "__main__":
    # If port 8000 is "already in use", change 8000 to 8001 here
    uvicorn.run("main:app", port=8001, reload=True)