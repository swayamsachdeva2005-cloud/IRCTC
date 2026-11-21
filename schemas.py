from pydantic import BaseModel, Field
from datetime import date
class Register(BaseModel):
    username: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class Train(BaseModel):
    train_no: int
    train_name: str
    source: str
    destination: str
    
class TrainCreate(BaseModel):
    train_no: int
    train_name: str
    source: str
    destination: str
    departure: str
    arrival: str


class TrainResponse(BaseModel):
    id: int
    train_no: int
    train_name: str
    source: str
    destination: str
    departure: str
    arrival: str
    
class BookingCreate(BaseModel):
    train_no: int
    journey_date: date
    seat_number: int = Field(ge=1, le=100)

class BookingResponse(BaseModel):
    booking_id: int
    train_no: int
    train_name: str
    source: str
    destination: str
    journey_date: date
    passenger_count: int
    status: str
    
BookingCreate.model_rebuild()
BookingResponse.model_rebuild()