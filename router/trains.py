from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Train


router = APIRouter(
    prefix='/train',
    tags=['Train']
)

session = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


trains_data = [
    {
        "train_number": "T1",
        "train_name": "Express Train 1",
        "train_type": "Express",
        "starting_station": "Trivandrum",
        "departure_station": "Delhi"
    },
    {
        "train_number": "T2",
        "train_name": "Local Train 1",
        "train_type": "Local",
        "starting_station": "Thirunelveli",
        "departure_station": "Trivandrum"
    },
    {
        "train_number": "T3",
        "train_name": "Express Train 2",
        "train_type": "Express",
        "starting_station": "Nagercoil",
        "departure_station": "Bangalore"
    },
    {
        "train_number": "T4",
        "train_name": "Express Train 3",
        "train_type": "Express",
        "starting_station": "Nagercoil",
        "departure_station": "Mumbai"
    },
    {
        "train_number": "T5",
        "train_name": "Local Train 2",
        "train_type": "Local",
        "starting_station": "Nagercoil",
        "departure_station": "Madurai"
    }

]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_train_details(db: db_dependency):
    return db.query(Train).all()
