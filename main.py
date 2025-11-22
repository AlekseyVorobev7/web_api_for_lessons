from typing import Dict, Any
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import hashlib
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")

JSON_FILE = "grades.json"
CLASSES_FILE = "classes.json"
USERS_FILE = "users.json"


def load_data():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(grades):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        return json.dump(grades, f, indent=2)


def load_classes():
    try:
        with open(CLASSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_classes(classes):
    with open(CLASSES_FILE, "w", encoding="utf-8") as f:
        return json.dump(classes, f, indent=2)


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        return json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_hex(32)


# Хранилище активных сессий (token -> username)
active_sessions = {}


def check_auth(token: str = None):
    if not token:
        return None
    return active_sessions.get(token)


def generate_id():
    grades = load_data()
    if not grades:
        return 0
    return max(grade["id"] for grade in grades) + 1


def generate_class_id():
    classes = load_classes()
    if not classes:
        return 0
    return max(cls["id"] for cls in classes) + 1


# Страницы аутентификации
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/api/register")
async def register(data: Dict[str, Any]):
    users = load_users()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return {"success": False, "error": "Заполните все поля"}

    # Проверка существующего пользователя
    for user in users:
        if user["username"] == username:
            return {"success": False, "error": "Пользователь уже существует"}

    # Создание нового пользователя
    new_user = {
        "username": username,
        "password": hash_password(password)
    }
    users.append(new_user)
    save_users(users)

    return {"success": True}


@app.post("/api/login")
async def login(data: Dict[str, Any], response: Response):
    users = load_users()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return {"success": False, "error": "Заполните все поля"}

    # Поиск пользователя
    hashed_password = hash_password(password)
    for user in users:
        if user["username"] == username and user["password"] == hashed_password:
            # Создание сессии
            token = generate_token()
            active_sessions[token] = username

            response.set_cookie(key="session_token", value=token, httponly=True)
            return {"success": True}

    return {"success": False, "error": "Неверное имя пользователя или пароль"}


@app.post("/api/logout")
async def logout(response: Response, session_token: str = Cookie(None)):
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response.delete_cookie("session_token")
    return {"success": True}


# API endpoints для оценок (с проверкой авторизации)
@app.get("/api/grades")
def get_grades(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    return load_data()


@app.post("/api/grades")
def add_grade(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    grades = load_data()
    new_grade = {
        "id": generate_id(),
        "name": data["name"],
        "subject": data["subject"],
        "grade": data["grade"],
        "date": data["date"],
        "teacher": data["teacher"]
    }
    grades.append(new_grade)
    save_data(grades)
    return {"Success": True, "grade": new_grade}


@app.delete("/api/grades/{grade_id}")
def delete_grade(grade_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    grades = load_data()
    for i, grade in enumerate(grades):
        if grade["id"] == grade_id:
            deleted_grade = grades.pop(i)
            save_data(grades)
            return deleted_grade
    return {"ERROR": "Нет такой оценки"}


@app.get("/api/grades/{grade_id}")
def get_grade_by_id(grade_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    grades = load_data()
    for grade in grades:
        if grade["id"] == grade_id:
            return grade
    return {"ERROR": "Нет такой оценки"}


# API endpoints для классов (с проверкой авторизации)
@app.get("/api/classes")
def all_classes(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    return load_classes()


@app.get("/api/classes/{class_id}")
def get_class_by_id(class_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    classes = load_classes()
    for cls in classes:
        if cls["id"] == class_id:
            return cls
    return {"ERROR": "Нет такого класса"}


@app.post("/api/classes")
def add_class(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    classes = load_classes()
    new_class = {
        "id": generate_class_id(),
        "code": data["code"],
        "students": data["students"],
        "year": data["year"],
        "super_teacher": data["super_teacher"]
    }
    classes.append(new_class)
    save_classes(classes)
    return {"Success": True, "class": new_class}


@app.delete("/api/classes/{class_id}")
def delete_class_by_id(class_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    classes = load_classes()
    for i, cls in enumerate(classes):
        if cls["id"] == class_id:
            deleted_class = classes.pop(i)
            save_classes(classes)
            return deleted_class
    return {"ERROR": "Нет такого класса"}


# Проверка авторизации для API
@app.get("/api/check-auth")
async def check_auth_endpoint(session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if username:
        return {"authenticated": True, "username": username}
    return {"authenticated": False}


# Веб-страницы (с проверкой авторизации)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})


@app.get("/grades", response_class=HTMLResponse)
async def grades_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("grades.html", {"request": request, "username": username})


@app.get("/classes", response_class=HTMLResponse)
async def classes_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("classes.html", {"request": request, "username": username})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
