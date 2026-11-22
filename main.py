from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from os import getenv
from typing import Annotated
from fastapi.staticfiles import StaticFiles

from database import Base, engine, get_db
import models
from security import hash_password, verify_password

app = FastAPI()

load_dotenv()
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    SessionMiddleware,
    secret_key=getenv("SECRET_KEY"),
    max_age=24*60*60,
    same_site="lax",
    https_only=False
)


class LoginForm(BaseModel):
    email: str
    password: str


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str



def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return db.get(models.User, user_id)


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"user": user}
    )


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"errors": [], "name": "", "email": ""}
    )


@app.post("/register")
def post_register(
    request: Request,
    form_data: Annotated[RegisterForm, Form()],
    db: Session = Depends(get_db)
):
    name = form_data.name.strip()
    email = form_data.email.strip().lower()
    password = form_data.password

    errors = []

    if not name:
        errors.append("Full name is required.")
    if not email:
        errors.append("Email address is required.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")

    if email and db.query(models.User).filter(models.User.email == email).first():
        errors.append("An account with this email already exists.")

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"errors": errors, "name": name, "email": email},
            status_code=400
        )

    new_user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="student"
    )
    db.add(new_user)
    db.commit()

    return RedirectResponse("/login", status_code=303)


@app.get("/login")
def login_page(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )



@app.post("/login")
def post_login(
    request: Request,
    form_data: Annotated[LoginForm, Form()],
    db: Session = Depends(get_db)
):
    email = form_data.email.strip().lower()
    password = form_data.password

    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Email or password is incorrect."},
            status_code=401
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse("/dashboard", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if user is None:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user}
    )


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.get("/admin")
def admin_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if user is None:
        return RedirectResponse("/login", status_code=303)

    if user.role != "admin":
        return templates.TemplateResponse(
            request=request,
            name="forbidden.html",
            context={"user": user},
            status_code=403
        )

    users = db.query(models.User).order_by(models.User.id).all()
    total = len(users)
    admins = sum(1 for u in users if u.role == "admin")

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "users": users,
            "total": total,
            "admins": admins,
            "students": total - admins,
        }
    )


