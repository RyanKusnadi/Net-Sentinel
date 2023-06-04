from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from pymongo import MongoClient
import uvicorn

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = MongoClient("mongodb+srv://ryankusnadi:Temporary999@senprologinapi.1eqaarl.mongodb.net/?retryWrites=true&w=majority")
db = client["auth"]
users = db.users 


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/register")
def register(username: str, password: str):
    hashed_password = get_password_hash(password)
    user = {"username": username, "password": hashed_password}
    users.insert_one(user)
    return JSONResponse({"message": "User registered successfully."})


@app.post("/login")
def login(username: str, password: str):
    user = users.find_one({"username": username})
    if user is None or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Set session cookie
    response = JSONResponse({"message": "Login successful."})
    response.set_cookie(key="session", value=username)
    return response


@app.get("/logout")
def logout():
    # Clear session cookie
    response = JSONResponse({"message": "Logged out successfully."})
    response.delete_cookie(key="session")
    return response


@app.get("/protected")
def protected_route(session: str = Depends(security)):
    if session:
        return JSONResponse({"message": "Access granted."})

    raise HTTPException(status_code=401, detail="You need to log in to access this route.")

"""
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""