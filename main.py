from fastapi import FastAPI,Request,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from os import getenv
from typing import Annotated

app = FastAPI()

load_dotenv()

templates = Jinja2Templates(directory="templates")


app.add_middleware(
    SessionMiddleware,
    secret_key=getenv("SECRET_KEY"),
    max_age=24*60*60,
    same_site="lax",
    https_only=False
)


class LoginForm(BaseModel):
    username:str
    password:str


@app.get("/")
def home(request:Request):
    return RedirectResponse("/login",status_code=303)


@app.get("/login")
def login_page(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.post("/login")
def login_post(request:Request,form_data:Annotated[LoginForm,Form()]):




