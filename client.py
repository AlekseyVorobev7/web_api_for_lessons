import requests

URL = "http://127.0.0.1:8000"


def get_all():  # выдает все
    try:
        res = requests.get(f"{URL}/grades")
        res.raise_for_status()  # Проверка на ошибки HTTP
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении оценок: {e}")


def get_by_id(grade_id):  # выдает айди
    try:
        res = requests.get(f"{URL}/grades/{grade_id}")
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении оценки {grade_id}: {e}")


def add_grade(name, subject, grade, date, teacher):  # шаблон для 30 строки и обьявление каждого обьекта
    data = {
        "name": name,
        "subject": subject,
        "grade": grade,
        "date": date,
        "teacher": teacher
    }
    try:
        res = requests.post(f"{URL}/grades", json=data)
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при добавлении оценки: {e}")


def delete_grade(grade_id):
    try:
        res = requests.delete(f"{URL}/grades/{grade_id}")
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении оценки {grade_id}: {e}")


# НОВЫЕ ФУНКЦИИ ДЛЯ КЛАССОВ
def get_all_classes():  # выдает все классы
    try:
        res = requests.get(f"{URL}/classes")
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении классов: {e}")


def get_class_by_id(class_id):  # выдает класс по айди
    try:
        res = requests.get(f"{URL}/classes/{class_id}")
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении класса {class_id}: {e}")


def add_class(code, students, year, super_teacher):  # добавляет класс
    data = {
        "code": code,
        "students": students,
        "year": year,
        "super_teacher": super_teacher
    }
    try:
        res = requests.post(f"{URL}/classes", json=data)
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при добавлении класса: {e}")


def delete_class(class_id):  # удаляет класс
    try:
        res = requests.delete(f"{URL}/classes/{class_id}")
        res.raise_for_status()
        print(res.json())
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении класса {class_id}: {e}")


if __name__ == "__main__":
    # Тестирование функций для классов
    add_class("П411", ["Горин Дамир", "Иванов Иван"], 2, "Алексей Воробьев")
    get_all_classes()