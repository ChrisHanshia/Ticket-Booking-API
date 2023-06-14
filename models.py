from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, foreignKey


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
    
    class Train(Base):
    __tablename__ = 'trains'

    id = Column(Integer, primary_key=True)
    train_number = Column(String, ForeignKey(Ticket.train_number))
    train_name = Column(String)
    train_type = Column(String)
    starting_station = Column(String)
    departure_station = Column(String)






