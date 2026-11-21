from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session, create_db

from models import User, Train as TrainModel
from schemas import TrainCreate, TrainResponse
from sqlalchemy.exc import IntegrityError
from models import User, Train as TrainModel, Booking
from schemas import BookingCreate, BookingResponse
from datetime import date
from schemas import Register, Login, Token, UserResponse ,Train
from auth import (
    hash_password,
    verify_password,
    create_token,
    get_current_user
)

app = FastAPI()



trains = [
    {
        "train_no": 12301,
        "train_name": "Rajdhani Express",
        "source": "New Delhi",
        "destination": "Howrah",
        "departure": "16:50",
        "arrival": "10:05"
    },
    {
        "train_no": 12002,
        "train_name": "Shatabdi Express",
        "source": "New Delhi",
        "destination": "Bhopal",
        "departure": "06:00",
        "arrival": "14:30"
    },
    {
        "train_no": 12951,
        "train_name": "Mumbai Rajdhani",
        "source": "New Delhi",
        "destination": "Mumbai Central",
        "departure": "16:55",
        "arrival": "08:35"
    }
]


@app.get("/trains")
def get_all_trains():
    return trains

@app.get("/trains/{train_no}", response_model=Train)
def get_train(train_no: int):

    for train in trains:
        if train.train_no == train_no:
            return train

    raise HTTPException(
        status_code=404,
        detail="Train not found"
    )
    


@app.on_event("startup")
def startup():
    create_db()


# REGISTER API
@app.post("/register", response_model=UserResponse)
def register(
    data: Register,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = User(
        username=data.username,
        password_hash=hash_password(data.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


# LOGIN API
@app.post("/login", response_model=Token)
def login(
    data: Login,
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    if not user or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# PROTECTED API
@app.get("/profile", response_model=UserResponse)
def profile(current_user: User = Depends(get_current_user)):
    return current_user

# ADD TRAIN TO DATABASE
@app.post("/trains", response_model=TrainResponse)
def add_train(
    data: TrainCreate,
    session: Session = Depends(get_session)
):

    new_train = TrainModel(
        train_no=data.train_no,
        train_name=data.train_name,
        source=data.source,
        destination=data.destination,
        departure=data.departure,
        arrival=data.arrival
    )

    session.add(new_train)

    try:
        session.commit()
        session.refresh(new_train)

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Train number already exists"
        )

    return new_train

from sqlalchemy.exc import IntegrityError

@app.post("/bookings")
def book_train(
    data: BookingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    try:
        train = session.exec(
            select(TrainModel).where(
                TrainModel.train_no == data.train_no
            )
        ).first()

        if not train:
            raise HTTPException(
                status_code=404,
                detail="Train not found"
            )

        if data.journey_date < date.today():
            raise HTTPException(
                status_code=400,
                detail="Invalid journey date"
            )

        booking = Booking(
            user_id=current_user.id,
            train_id=train.id,
            journey_date=data.journey_date,
            seat_number=data.seat_number,
            status="Confirmed"
        )

        session.add(booking)
        session.commit()
        session.refresh(booking)

        return {
            "message": "Ticket booked successfully",
            "booking_id": booking.id,
            "train_no": train.train_no,
            "seat_number": booking.seat_number,
            "journey_date": booking.journey_date,
            "status": booking.status
        }

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="This seat is already booked. Please select another seat."
        )

    except Exception:
        session.rollback()
        raise

@app.get("/my-bookings", response_model=list[BookingResponse])
def get_my_bookings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    bookings = session.exec(
        select(Booking).where(
            Booking.user_id == current_user.id
        )
    ).all()

    result = []

    for booking in bookings:

        train = session.get(TrainModel, booking.train_id)

        if train:
            result.append({
                "booking_id": booking.id,
                "train_no": train.train_no,
                "train_name": train.train_name,
                "source": train.source,
                "destination": train.destination,
                "journey_date": booking.journey_date,
                "passenger_count": booking.passenger_count,
                "status": booking.status
            })

    return result

@app.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    booking = session.get(Booking, booking_id)

    if not booking or booking.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Booking already cancelled"
        )

    booking.status = "Cancelled"

    session.add(booking)
    session.commit()

    return {
        "message": "Booking cancelled successfully",
        "booking_id": booking_id
    }