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
    tags=['registration']
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

class TicketUpdate(BaseModel):
    date: date
    time: str

    class Config:
        orm_mode = True


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
    return {"message": "ticket booked Successfully"}

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
    return {'message': 'ticket cancelled Successfully'}

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
