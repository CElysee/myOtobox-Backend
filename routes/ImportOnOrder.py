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


router = APIRouter(tags=["ImportOnOrder"], prefix="/import-on-order")


@router.get("/list")
async def get_all_import_on_order(db: db_dependency):
    # All Import on orders
    import_orders = (
        db.query(models.ImportOnOrder).order_by(models.ImportOnOrder.id.desc()).all()
    )
    orders = []
    for order in import_orders:
        order_car_brand = order.car_brand
        order_car_model = order.car_model
        order_car_trim = order.car_trim
        order_user = order.user
        orders.append(order)
    # Import order counts

    count_pending_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.order_status == "Pending")
        .count()
    )
    count_approved_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.order_status == "Approved")
        .count()
    )
    count_rejected_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.order_status == "Canceled")
        .count()
    )
    count_completed_orders = (
        db.query(models.ImportOnOrder)
        .filter(models.ImportOnOrder.order_status == "Completed")
        .count()
    )

    return {
        "orders": orders,
        "count_orders": {
            "count_pending_orders": count_pending_orders,
            "count_approved_orders": count_approved_orders,
            "count_canceled_orders": count_rejected_orders,
            "count_completed_orders": count_completed_orders,
        },
    }


@router.post("/create")
async def create_import_on_order(
    user_request: schemas.ImportOnOrderCreate, db: db_dependency
):
    new_order = models.ImportOnOrder(
        user_id=user_request.user_id,
        price_range=user_request.price_range,
        fuel_type=user_request.fuel_type,
        transmission_type=user_request.transmission_type,
        car_brand_id=user_request.car_brand_id,
        car_model_id=user_request.car_model_id,
        car_trim_id=user_request.car_trim_id,
        manufacture_year_from=user_request.manufacture_year_from,
        manufacture_year_to=user_request.manufacture_year_to,
        kilometers_from=user_request.kilometers_from,
        kilometers_to=user_request.kilometers_to,
        names=user_request.names,
        phone_number=user_request.phone_number,
        email=user_request.email,
        exterior_color=user_request.exterior_color,
        order_note=user_request.order_note,
        car_color=user_request.car_color,
        order_status="Pending",
        created_at=datetime.now(),
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "Successfully sent order"}

@router.put("/update/{id}")
async def update_import_on_order(
    id: int, user_request: schemas.ImportOnOrderUpdateStatus, db: db_dependency
):
    order = db.query(models.ImportOnOrder).filter(models.ImportOnOrder.id == id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.order_status = user_request.order_status
    db.commit()
    return {"message": "Order updated successfully"}