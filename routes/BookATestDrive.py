import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File, Query
from sqlalchemy.orm import Session, load_only, contains_eager

from database import db_dependency, SessionLocal
from starlette import status
import models
import schemas
from sqlalchemy import asc
import hashlib
import random


router = APIRouter(tags=["BookATestDrive"], prefix="/book-a-test-drive")


@router.get("/list")
def get_all_book_a_test_drive(db: db_dependency):
    list = (
        db.query(models.BookATestDrive)
        .order_by(models.BookATestDrive.created_at.desc())
        .all()
    )
    booked_test_drive = []
    for test_drive in list:
        booked_car = test_drive.car_for_sale
        booked_user = test_drive.user
        booked_test_drive.append(test_drive)
    count_pending_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Pending")
        .count()
    )
    count_approved_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Approved")
        .count()
    )
    count_canceled_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Canceled")
        .count()
    )
    count_completed_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Completed")
        .count()
    )
    return {
        "booked_test_drive": booked_test_drive,
        "count_bookings": {
            "count_pending_booked_test_drive": count_pending_booked_test_drive,
            "count_approved_booked_test_drive": count_approved_booked_test_drive,
            "count_canceled_booked_test_drive": count_canceled_booked_test_drive,
            "count_completed_booked_test_drive": count_completed_booked_test_drive,
        },
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_book_a_test_drive(
    user_request: schemas.BookATestDriveCreate, db: db_dependency
):
    car_id_check = (
        db.query(models.CarForSale)
        .filter(models.CarForSale.stock_number == user_request.car_id)
        .first()
    )

    if car_id_check is None:
        raise HTTPException(status_code=404, detail="Car not found")

    new_book_a_test_drive = models.BookATestDrive(
        phone_number=user_request.phone_number,
        car_id=car_id_check.id,
        user_id=user_request.user_id,
        date=user_request.date,
        time=user_request.time,
        location_choice=user_request.location_choice,
        booking_status="Pending",
        created_at=datetime.now(),
    )
    db.add(new_book_a_test_drive)
    db.commit()
    return {"message": "Book a test drive created successfully"}


@router.put("/update/{id}")
async def update_book_a_test_drive(
    id: int, user_request: schemas.BookATestDriveUpdateBookingStatus, db: db_dependency
):
    book_a_test_drive = db.query(models.BookATestDrive).filter_by(id=id).first()
    if book_a_test_drive is None:
        raise HTTPException(status_code=404, detail="Book a test drive not found")

    book_a_test_drive.booking_status = user_request.booking_status
    db.commit()
    return {"message": "Book a test drive updated successfully"}
