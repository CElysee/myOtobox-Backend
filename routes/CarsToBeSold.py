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
import requests


router = APIRouter(tags=["CarsToBeSold"], prefix="/cars-to-be-sold")


def send_sms(phone_number, message):
    url = "https://api.mista.io/sms"
    api_key = os.getenv("API_KEY")  # API key
    sender_id = os.getenv("SENDER_ID")  # Sender ID

    payload = {
        "action": "send-sms",
        "to": phone_number,
        "from": sender_id,
        "sms": message,
        "unicode": "0",
    }
    headers = {"x-api-key": api_key}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Error sending SMS: {e}")
        return None


def format_number(number):
    number_to_format = int(number)
    # Format the selling price with commas
    formatted_number = "{:,}".format(number_to_format)
    return formatted_number

@router.get("/list")
async def get_all_cars_to_be_sold(db: db_dependency):
    # All Cars to be sold
    cars_to_be_sold = (
        db.query(models.CarsToBeSold).order_by(models.CarsToBeSold.id.desc()).all()
    )
    cars = []
    for car in cars_to_be_sold:
        car_car_brand = car.car_brand
        car_car_model = car.car_model
        car_car_trim = car.car_trim
        cars.append(car)
    # Cars to be sold counts

    count_pending_cars = (
        db.query(models.CarsToBeSold)
        .filter(models.CarsToBeSold.listing_car_status == "Pending")
        .count()
    )
    count_approved_cars = (
        db.query(models.CarsToBeSold)
        .filter(models.CarsToBeSold.listing_car_status == "Approved")
        .count()
    )
    count_rejected_cars = (
        db.query(models.CarsToBeSold)
        .filter(models.CarsToBeSold.listing_car_status == "Canceled")
        .count()
    )
    count_completed_cars = (
        db.query(models.CarsToBeSold)
        .filter(models.CarsToBeSold.listing_car_status == "Completed")
        .count()
    )

    return {
        "cars": cars,
        "count_cars": {
            "count_pending_cars": count_pending_cars,
            "count_approved_cars": count_approved_cars,
            "count_canceled_cars": count_rejected_cars,
            "count_completed_cars": count_completed_cars,
        },
    }


@router.post("/create")
async def create_car_to_be_sold(
    request_data: schemas.CarToBeSoldCreate, db: db_dependency
):
    new_car = models.CarsToBeSold(
        car_info_name=request_data.car_info_name,
        manufacture_year=request_data.manufacture_year,
        car_brand_id=request_data.car_brand_id,
        car_model_id=request_data.car_model_id,
        car_trim_id=request_data.car_trim_id,
        selling_price=request_data.selling_price,
        kilometers=request_data.kilometers,
        transmission_type=request_data.transmission_type,
        fuel_type=request_data.fuel_type,
        exterior_color=request_data.exterior_color,
        interior_color=request_data.interior_color,
        seller_name=request_data.seller_name,
        seller_phone_number=request_data.seller_phone_number,
        seller_note=request_data.seller_note,
        listing_car_status="Pending",
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    seller_amount = format_number(request_data.selling_price)
    kilometers = format_number(request_data.kilometers)
    if request_data.transmission_type == "Automatic Transmission":
        transmission_type = "AT"
    else:
        transmission_type = "MT"    
    message = (
        f"You have a new request car details:\n"
        f"{request_data.car_info_name} {request_data.manufacture_year} selling for {seller_amount} RWF with {kilometers} km, "
        f"{transmission_type}. Seller info: {request_data.seller_name}, {request_data.seller_phone_number}."
    )
    sms_result = send_sms(250782384772, message)
    return sms_result

    return {"message": "Car to be sold created successfully.", "data": new_car}
