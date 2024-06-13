import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File, Query
from sqlalchemy.orm import Session, load_only, contains_eager

from database import db_dependency, SessionLocal
from starlette import status
from models import BookedRentalCar, CarsForRent, User
import schemas
from sqlalchemy import asc
import hashlib
import random
from datetime import datetime, date
from sendSMS import sendSMS


router = APIRouter(tags=["BookRentalCar"], prefix="/book-rental-car")

def generate_short_stock_number():
    short_stock_number = str(uuid.uuid4())[:5]  # Generate an eight-character UUID
    return short_stock_number    

@router.get("/list")
def get_all_book_rental_car(db: db_dependency):
    list = db.query(BookedRentalCar).order_by(BookedRentalCar.created_at.desc()).all()
    booked_rental_cars = []
    for test_drive in list:
        booked_car = test_drive.car_for_sale
        booked_user = test_drive.user
        booked_rental_cars.append(test_drive)

    count_pending_booked_rental_cars = (
        db.query(BookedRentalCar)
        .filter(BookedRentalCar.booking_status == "Pending")
        .count()
    )
    count_approved_booked_rental_cars = (
        db.query(BookedRentalCar)
        .filter(BookedRentalCar.booking_status == "Approved")
        .count()
    )
    count_canceled_booked_rental_cars = (
        db.query(BookedRentalCar)
        .filter(BookedRentalCar.booking_status == "Canceled")
        .count()
    )
    count_completed_booked_rental_cars = (
        db.query(BookedRentalCar)
        .filter(BookedRentalCar.booking_status == "Completed")
        .count()
    )
    return {
        "booked_test_drive": booked_rental_cars,
        "count_bookings": {
            "count_completed_booked_rental_cars": count_pending_booked_rental_cars,
            "count_approved_booked_rental_cars": count_approved_booked_rental_cars,
            "count_canceled_booked_rental_cars": count_canceled_booked_rental_cars,
            "count_completed_booked_rental_cars": count_completed_booked_rental_cars,
        },
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_book_rental_car(
    user_request: schemas.BookRentalCarCreate, db: db_dependency
):
    start_date = datetime.strptime(user_request.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(user_request.end_date, "%Y-%m-%d").date()
    days_between = (end_date - start_date).days
    car_info = (
        db.query(CarsForRent)
        .filter(CarsForRent.stock_number == user_request.car_id)
        .first()
    )
    user_info = db.query(User).filter(User.id == user_request.user_id).first()
    
    short_stock_number = generate_short_stock_number()
    # Last added car for sale
    last_car = db.query(BookedRentalCar).order_by(BookedRentalCar.id.desc()).first()
    # Combine the last car ID with the short stock number
    if last_car is None:
        new_stock_number = f"{short_stock_number}1-RE"
    else:
        new_stock_number = f"{short_stock_number}{last_car.id+1}-RE"
        
    rental_amount = int(car_info.car_price_per_day) * days_between
    phone_number = "25"+user_request.phone_number
    new_book_rental_car = BookedRentalCar(
        user_id=user_request.user_id,
        car_id=car_info.id,
        booking_id=new_stock_number,
        phone_number=user_request.phone_number,
        car_delivery_choice=user_request.car_delivery_choice,
        booking_status="Booked",
        start_date=user_request.start_date,
        start_time=user_request.start_time,
        end_date=user_request.end_date,
        end_time=user_request.end_time,
        rental_days=days_between,
        rental_amount=rental_amount,
        created_at=datetime.now(),
    )
    db.add(new_book_rental_car)
    db.commit()
    db.refresh(new_book_rental_car)
    
    car_name = car_info.car_year + " " + car_info.car_name_info
    message_user = f"Hello {user_info.firstName}, your rental car booking has been confirmed. Your booking ID is {new_book_rental_car.booking_id}. You have booked {car_name} for {days_between} days from {start_date} to {end_date}. Your total rental amount is {rental_amount} Rwf."
    send_sms_to_user = sendSMS(
        phone_number,
        message_user
    )
    message_owner = f"Hello {car_info.car_renter_name}, your {car_name} with plate number {car_info.car_registration_number} has been booked for {days_between} days from {start_date} to {end_date}. The total rental amount is {rental_amount} Rwf."
    
    owner_phone_number = "25"+car_info.renter_phone_number
    send_sms_to_owner = sendSMS(
        owner_phone_number,
        message_owner
    )
    return {
        "message": "Booked rental car successfully created",
        "result": new_book_rental_car,
    }


@router.put("/update/{id}")
async def update_book_rental_car(
    id: int, user_request: schemas.BookRentalCarUpdate, db: db_dependency
):
    book_rental_car = db.query(BookedRentalCar).filter(BookedRentalCar.id == id).first()
    if book_rental_car is None:
        raise HTTPException(status_code=404, detail="Booked rental car not found")

    book_rental_car.booking_status = user_request.booking_status
    db.commit()
    return {
        "message": "Booked rental car updated successfully",
        "data": book_rental_car,
    }


@router.get("/send-sms/")
async def send_sms(phone_number: str, message: str):
    sendSMS(phone_number, message)
