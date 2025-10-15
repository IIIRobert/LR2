from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import datetime
import uvicorn

app = FastAPI(title="Система бронирования номеров (Вариант 12)")

# ----- Модели -----
class Room(BaseModel):
    id: int
    number: str
    type: str
    price: float
    description: str = ""

class Booking(BaseModel):
    id: int
    room_id: int
    user_name: str
    start_date: datetime.date
    end_date: datetime.date


# ----- “База данных” -----
rooms = [
    Room(id=1, number="101", type="1", price=30.0, description="Одноместный"),
    Room(id=2, number="102", type="2", price=45.0, description="Двухместный"),
    Room(id=3, number="103", type="2", price=50.0, description="Двухместный с балконом"),
    Room(id=4, number="201", type="3", price=60.0, description="Трёхместный номер"),
    Room(id=5, number="202", type="1", price=35.0, description="Одноместный улучшенный"),
    Room(id=6, number="301", type="suite", price=120.0, description="Люкс с видом на море"),
    Room(id=7, number="302", type="suite", price=130.0, description="Люкс премиум"),
]

bookings: List[Booking] = []
next_booking_id = 1

# ----- Простая система ролей -----
def get_user_role(x_user_role: Optional[str] = Header(None)) -> str:
    if x_user_role not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="Укажите заголовок X-User-Role: admin или user")
    return x_user_role

# ----- CRUD для бронирований -----

# CREATE — создать бронь (user и admin)
@app.post("/bookings")
def create_booking(
    room_id: int,
    user_name: str,
    start_date: datetime.date,
    end_date: datetime.date,
    role: str = Depends(get_user_role)
):
    global next_booking_id
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Дата начала позже даты конца")

    # проверяем комнату
    room = next((r for r in rooms if r.id == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    # проверка пересечений
    for b in bookings:
        if b.room_id == room_id and not (b.end_date < start_date or b.start_date > end_date):
            raise HTTPException(status_code=400, detail="Комната уже забронирована на эти даты")

    booking = Booking(
        id=next_booking_id,
        room_id=room_id,
        user_name=user_name,
        start_date=start_date,
        end_date=end_date
    )
    bookings.append(booking)
    next_booking_id += 1
    return {"message": "Бронирование успешно создано", "booking": booking}


# READ — просмотр всех бронирований (только админ)
@app.get("/bookings")
def list_bookings(role: str = Depends(get_user_role)):
    if role == "admin":
        return bookings
    else:
        raise HTTPException(status_code=403, detail="Только администратор может просматривать все бронирования")


# UPDATE — изменить бронь (только админ)
@app.put("/bookings/{booking_id}")
def update_booking(
    booking_id: int,
    start_date: datetime.date,
    end_date: datetime.date,
    role: str = Depends(get_user_role)
):
    booking = next((b for b in bookings if b.id == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Дата начала позже даты конца")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Только админ может редактировать бронирования")

    booking.start_date = start_date
    booking.end_date = end_date
    return {"message": "Бронирование обновлено", "booking": booking}


# DELETE — удалить бронь (только админ)
@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, role: str = Depends(get_user_role)):
    booking = next((b for b in bookings if b.id == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Удалять может только администратор")

    bookings.remove(booking)
    return {"message": "Бронирование удалено"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
