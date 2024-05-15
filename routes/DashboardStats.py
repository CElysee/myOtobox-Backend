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

router = APIRouter(tags=["DashboardStats"], prefix="/dashboard-stats")


@router.get("/get-vehicle-count")
def get_vehicle_count(db: db_dependency):
    # Daily booked test drive cars count
    weekly_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(
            models.BookATestDrive.created_at
            >= datetime.now().date() - timedelta(days=7)
        )
        .count()
    )

    # Daily tax calculation count
    weekly_tax_calculation = (
        db.query(models.TaxCalculator)
        .filter(
            models.TaxCalculator.created_at >= datetime.now().date() - timedelta(days=7)
        )
        .count()
    )

    # Weekly new user count
    weekly_new_user = (
        db.query(models.User)
        .filter(
            models.User.created_at >= datetime.now().date() - timedelta(days=7),
            models.User.role == "user",
        )
        .count()
    )

    # Weekly new car for sale count
    weekly_new_car_for_sale = (
        db.query(models.CarForSale)
        .filter(
            models.CarForSale.created_at >= datetime.now().date() - timedelta(days=7)
        )
        .count()
    )

    # All cars for sale count
    all_cars_for_sale = db.query(models.CarForSale).count()

    # All pending booked test drive
    pending_booked_test_drive = (
        db.query(models.BookATestDrive)
        .filter(models.BookATestDrive.booking_status == "Pending")
        .order_by(models.BookATestDrive.id.desc())
        .all()
    )

    booked_test_drive = []
    for test_drive in pending_booked_test_drive:
        booked_car = test_drive.car_for_sale
        booked_user = test_drive.user
        booked_test_drive.append(test_drive)

    # All Import on orders
    import_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.order_status == "Pending")
        .order_by(models.ImportOnOrder.id.desc())
        .all()
    )
    
    orders = []
    for order in import_orders:
        order_car_brand = order.car_brand
        order_car_model = order.car_model
        order_car_trim = order.car_trim
        order_user = order.user
        orders.append(order)
        
    return {
        "weekly_booked_test_drive": weekly_booked_test_drive,
        "weekly_tax_calculation": weekly_tax_calculation,
        "weekly_new_user": weekly_new_user,
        "weekly_new_car_for_sale": weekly_new_car_for_sale,
        "all_cars_for_sale": all_cars_for_sale,
        "pending_booked_test_drive": booked_test_drive,
        "pending_import_orders": orders,
    }
