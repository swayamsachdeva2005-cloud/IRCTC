from sqlmodel import SQLModel, Field,UniqueConstraint

from datetime import date

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str


class Train(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_no: int = Field(unique=True, index=True)
    train_name: str
    source: str
    destination: str
    departure: str
    arrival: str


class Booking(SQLModel, table=True):

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "journey_date",
            "seat_number",
            name="unique_train_seat_date"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    train_id: int = Field(foreign_key="train.id")

    journey_date: date
    seat_number: int
    status: str = Field(default="Confirmed")