from fastapi import FastAPI, HTTPException, Response, Depends, File, UploadFile
from authx import AuthX, AuthXConfig
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

class UserLoginSchema(BaseModel):
    username: str
    password: str


@app.post("/login", tags=["Auth"])
def login(credentials: UserLoginSchema, res: Response):
    if credentials.username == "test" and credentials.password == "test":
        token = security.create_access_token(uid="12345test")
        res.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Wrong credentials")


@app.get("/protected-route", dependencies=[Depends(security.access_token_required)], tags=["Protected routes"])
def getmyinfo():
    return {"data": "my info"}


@app.post("/single_file", tags=["Files"])
async def upload_file(uploaded_file: UploadFile):
    file = uploaded_file.file
    filename = uploaded_file.filename
    with open(filename, "wb") as f:
        f.write(file.read())


@app.post("/multiple_files", tags=["Files"], summary="Upload multiple files")
async def upload_file(uploaded_files: list[UploadFile]):
    for uploaded_file in uploaded_files:
        file = uploaded_file.file
        filename = uploaded_file.filename
        with open(filename, "wb") as f:
            f.write(file.read())