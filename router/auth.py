from datetime import timedelta, datetime, date
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Ticket
from starlette import status
from sqlalchemy import and_


router = APIRouter(
    prefix='/booking',
    tags=['Ticket Booking']
)

session = SessionLocal()

class TicketRequest(BaseModel):
    passenger_name: str
    train_number: str
    seat_number: str
    date: date
    time: str
    boarding_station: str
    departure_station: str

    @validator('date')
    def validate_date(cls, value):
        if value < date.today():
            raise ValueError("Date must be in the future")
        return value

    @validator('time')
    def validate_time(cls, value):
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Expected format: HH:MM")
        return value

    @validator('seat_number')
    def validate_seat_number(cls, value):
        row_column = value.split()
        if len(row_column) != 2:
            raise ValueError("Invalid seat number. Seat number must have two parts separated by a space.")
        row = row_column[0]
        column = row_column[1]
        valid_rows = 'ABCDEFGHIJKLMNOPQRS'
        valid_columns = [str(i) for i in range(1, 26)]
        if row not in valid_rows or column not in valid_columns:
            raise ValueError(
                "Invalid seat number. Seat number must be in the format A 1-S 25 and within the range A 1-25 to S 1-25.")
        return value

class TicketUpdate(BaseModel):
    date: date
    time: str

    class Config:
        orm_mode = True

class SeatAvailabilityResponse(BaseModel):
    seat_number: str
    is_booked: bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def book_ticket(db: db_dependency, create_user_request: TicketRequest):
    existing_ticket = db.query(Ticket).filter(
        and_(
            Ticket.seat_number == create_user_request.seat_number,
            Ticket.train_number == create_user_request.train_number,
            Ticket.date == create_user_request.date
        )
    ).first()
    if existing_ticket:
        raise HTTPException(status_code=400, detail="The seat is already reserved.")

    create_user_model = Ticket(
        passenger_name=create_user_request.passenger_name,
        train_number=create_user_request.train_number,
        seat_number=create_user_request.seat_number,
        date=create_user_request.date,
        time=create_user_request.time,
        boarding_station=create_user_request.boarding_station,
        departure_station=create_user_request.departure_station
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"message": "Ticket booked Successfully"}

@router.get("/ticket", status_code=status.HTTP_200_OK)
async def get_ticket_details(db: db_dependency,
                             page: int = Query(1, gt=0)):
    per_page = 5
    offset = (page - 1) * per_page
    return db.query(Ticket).offset(offset).limit(per_page).all()

@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: db_dependency):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    db.delete(ticket)
    db.commit()
    return {'message': 'Ticket cancelled Successfully'}

@router.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, ticket_update: TicketUpdate,
                  db: db_dependency):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket not found')
    ticket.date = ticket_update.date
    ticket.time = ticket_update.time
    db.commit()
    return {'message': 'Ticket updated successfully'}

@router.get("/seats/availability")
async def check_seat_availability(seat_number: str, train_number: str, date: date, db: db_dependency):
    seat = db.query(Ticket).filter(
        Ticket.seat_number == seat_number,
        Ticket.train_number == train_number,
        Ticket.date == date
    ).first()
    if seat:
        if seat.is_booked:
            return {"message": "Seat not found."}
        else:
            return {"message": "Seat already booked."}
    else:
        return {"message": "Seat is available."}

