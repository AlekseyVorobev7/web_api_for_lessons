from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

JSON_FILE = "grades.json"
CLASSES_FILE = "classes.json"

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

# API endpoints для оценок
@app.get("/api/grades")
def get_grades():
    return load_data()

@app.post("/api/grades")
def add_grade(data: Dict[str, Any]):
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
def delete_grade(grade_id: int):
    grades = load_data()
    for i, grade in enumerate(grades):
        if grade["id"] == grade_id:
            deleted_grade = grades.pop(i)
            save_data(grades)
            return deleted_grade
    return {"ERROR": "Нет такой оценки"}

@app.get("/api/grades/{grade_id}")
def get_grade_by_id(grade_id: int):
    grades = load_data()
    for grade in grades:
        if grade["id"] == grade_id:
            return grade
    return {"ERROR": "Нет такой оценки"}

# API endpoints для классов
@app.get("/api/classes")
def all_classes():
    return load_classes()

@app.get("/api/classes/{class_id}")
def get_class_by_id(class_id: int):
    classes = load_classes()
    for cls in classes:
        if cls["id"] == class_id:
            return cls
    return {"ERROR": "Нет такого класса"}

@app.post("/api/classes")
def add_class(data: Dict[str, Any]):
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
def delete_class_by_id(class_id: int):
    classes = load_classes()
    for i, cls in enumerate(classes):
        if cls["id"] == class_id:
            deleted_class = classes.pop(i)
            save_classes(classes)
            return deleted_class
    return {"ERROR": "Нет такого класса"}

# Веб-страницы
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/grades", response_class=HTMLResponse)
async def grades_page(request: Request):
    return templates.TemplateResponse("grades.html", {"request": request})

@app.get("/classes", response_class=HTMLResponse)
async def classes_page(request: Request):
    return templates.TemplateResponse("classes.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")