import os
import uuid
from datetime import datetime, timedelta
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

router = APIRouter(tags=["UserDashboard"], prefix="/user-dashboard")


@router.get("/get-vehicle-count")
def get_vehicle_count(user_id: int, db: db_dependency):
    # Pending booked test drive
    pending_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Pending")
        .count()
    )
    # Approved booked test drive
    approved_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Approved")
        .count()
    )
    # Rejected booked test drive
    rejected_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Rejected")
        .count()
    )

    # Booked rentals
    booked_rentals = (
        db.query(models.BookedRentalCar).filter(
            models.BookedRentalCar.user_id == user_id
        )
    ).count()

    # All Import on orders
    import_orders = (
        db.query(models.ImportOnOrder)
        .filter(
            models.ImportOnOrder.order_status, models.ImportOnOrder.user_id == user_id
        )
        .count()
    )

    # Tax calculated
    tax_calculated = (
        db.query(models.TaxCalculator)
        .filter(models.TaxCalculator.user_id == user_id)
        .count()
    )

    return {
        "pending_booked_test_drive": pending_booked_test_drive,
        "approved_booked_test_drive": approved_booked_test_drive,
        "rejected_booked_test_drive": rejected_booked_test_drive,
        "booked_rentals": booked_rentals,
        "import_orders": import_orders,
        "tax_calculated": tax_calculated,
    }


@router.get("/get-user-profile")
def get_user_profile(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    country = (
        db.query(models.Country).filter(models.Country.id == user.country_id).first()
    )
    user_data = {
        "id": user.id,
        "first_name": user.firstName,
        "last_name": user.lastName,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "is_active": user.is_active,
        "country_id": user.country_id,
        "country": country,
    }

    return user_data


@router.get("/get-user-booked-test-drive")
def get_user_booked_test_drive(user_id: int, db: db_dependency):
    booked_test_drives = (
        db.query(models.BookATestDrive, models.CarForSale)
        .join(models.CarForSale, models.BookATestDrive.car_id == models.CarForSale.id)
        .filter(models.BookATestDrive.user_id == user_id)
        .all()
    )

    results = []
    for booked_test_drive, car in booked_test_drives:
        results.append(
            {
                "booked_test_drive": {
                    "id": booked_test_drive.id,
                    "scheduled_date": booked_test_drive.date,
                    "scheduled_time": booked_test_drive.time,
                    "booking_status": booked_test_drive.booking_status,
                    "created_at": booked_test_drive.created_at,
                    "phone_number": booked_test_drive.phone_number,
                    "location_choice": booked_test_drive.location_choice,
                    # Add other fields as necessary
                },
                "car": {
                    "id": car.id,
                    "name": car.car_name_info + " " + car.car_year,
                    # Add other fields as necessary
                },
            }
        )

    return results


@router.get("/get-user-booked-rentals")
def user_booked_rentals(user_id: int, db: db_dependency):
    booked_rentals = (
        db.query(models.BookedRentalCar, models.CarsForRent)
        .join(
            models.CarsForRent, models.BookedRentalCar.car_id == models.CarsForRent.id
        )
        .filter(models.BookedRentalCar.user_id == user_id)
        .all()
    )

    results = []
    for booked_rental, car in booked_rentals:
        results.append(
            {
                "booked_rental": {
                    "id": booked_rental.id,
                    "start_date": booked_rental.start_date,
                    "end_date": booked_rental.end_date,
                    "start_time": booked_rental.start_time,
                    "end_time": booked_rental.end_time,
                    "booking_status": booked_rental.booking_status,
                    "created_at": booked_rental.created_at,
                    "phone_number": booked_rental.phone_number,
                    "car_delivery_choice": booked_rental.car_delivery_choice,
                    "rental_days": booked_rental.rental_days,
                    "rental_amount": booked_rental.rental_amount,
                    # Add other fields as necessary
                },
                "car": {
                    "id": car.id,
                    "name": car.car_name_info + " " + car.car_year,
                    # Add other fields as necessary
                },
            }
        )

    return results


@router.get("/get-user-import-orders")
def get_user_import_orders(user_id: int, db: db_dependency):
    import_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.user_id == user_id)
        .all()
    )
    return import_orders

@router.get("/get-user-tax-calculations")
def get_user_tax_calculations(user_id: int, db: db_dependency):
    tax_calculations = (
        db.query(models.TaxCalculator)
        .filter(models.TaxCalculator.user_id == user_id)
        .all()
    )
    return tax_calculations