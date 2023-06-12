from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date


class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    passenger_name = Column(String)
    train_number = Column(String)
    seat_number = Column(String, unique=True)
    date = Column(Date)
    time = Column(String)
    boarding_station = Column(String)
    departure_station = Column(String)






