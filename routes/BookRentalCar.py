import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File, Query
from sqlalchemy.orm import Session, load_only, contains_eager

from database import db_dependency, SessionLocal
from starlette import status
from models import BookedRentalCar, CarsForRent
import schemas
from sqlalchemy import asc
import hashlib
import random
from datetime import datetime, date



router = APIRouter(tags=["BookRentalCar"], prefix="/book-rental-car")

@router.get("/list")
def get_all_book_rental_car(db: db_dependency):
    list = (
        db.query(BookedRentalCar)
        .order_by(BookedRentalCar.created_at.desc())
        .all()
    )
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
async def create_book_rental_car(user_request: schemas.BookRentalCarCreate, db: db_dependency):
    start_date = datetime.strptime(user_request.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(user_request.end_date, "%Y-%m-%d").date()
    days_between = (end_date - start_date).days
    car_info = db.query(CarsForRent).filter(CarsForRent.stock_number == user_request.car_id).first()
    rental_amount = int(car_info.car_price_per_day) * days_between
    
    new_book_rental_car = BookedRentalCar(
        user_id=user_request.user_id,
        car_id=car_info.id,
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
    return {"message": "Booked rental car successfully created", "result": new_book_rental_car}

@router.put("/update/{id}")
async def update_book_rental_car(id: int, user_request: schemas.BookRentalCarUpdate, db: db_dependency):
    book_rental_car = db.query(BookedRentalCar).filter(BookedRentalCar.id == id).first()
    if book_rental_car is None:
        raise HTTPException(status_code=404, detail="Booked rental car not found")
    
    book_rental_car.booking_status = user_request.booking_status
    db.commit()
    return {"message": "Booked rental car updated successfully", "data": book_rental_car}

