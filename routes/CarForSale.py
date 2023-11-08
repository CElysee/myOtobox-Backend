import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from database import db_dependency, SessionLocal
from starlette import status
import models
import schemas

router = APIRouter(
    tags=["CarForSale"],
    prefix='/car_for_sale'
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_FOLDER = "CarSellImages"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def save_uploaded_file(file: UploadFile):
    file_extension = file.filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, random_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return random_filename


@router.get("/list")
async def get_car_for_sale(db: db_dependency):
    car_for_sale_list = db.query(models.CarForSale).all()
    return car_for_sale_list


@router.get("/list/{user_id}")
async def get_car_for_sale(user_id: int, db: db_dependency):
    car_for_sale_list = db.query(models.CarForSale).filter(models.CarForSale.user_id == user_id).all()
    return car_for_sale_list


@router.post('/create')
async def create_car_for_sale(db: Session = Depends(get_db), car_for_sale: schemas.CarForSaleBase = Depends(),
                              car_images: list[UploadFile] = File(...)):
    car_standard_features_ids = [int(item) for item in car_for_sale.car_standard_features[0].split(',')]
    add_car_for_sale = models.CarForSale(
        user_id=car_for_sale.user_id,
        car_brand_id=car_for_sale.car_brand_id,
        car_model_id=car_for_sale.car_model_id,
        car_trim_id=car_for_sale.car_trim_id,
        car_year=car_for_sale.car_year,
        car_mileage=car_for_sale.car_mileage,
        car_price=car_for_sale.car_price,
        car_currency=car_for_sale.car_currency,
        car_location=car_for_sale.car_location,
        car_fuel_type_id=car_for_sale.car_fuel_type_id,
        car_exterior_color=car_for_sale.car_exterior_color,
        car_interior_color=car_for_sale.car_interior_color,
        car_transmission=car_for_sale.car_transmission,
        car_engine_capacity=car_for_sale.car_engine_capacity,
        car_drive_train=car_for_sale.car_drive_train,
        car_fuel_consumption=car_for_sale.car_fuel_consumption,
        car_vin_number=car_for_sale.car_vin_number,
        car_registration_number=car_for_sale.car_registration_number,
        car_insurance=car_for_sale.car_insurance,
        car_control_technique=car_for_sale.car_control_technique,
        car_user_type=car_for_sale.car_user_type,
        car_accident_history=car_for_sale.car_accident_history,
        seller_note=car_for_sale.seller_note,
        car_status="sale",
        created_at=datetime.now()
    )
    db.add(add_car_for_sale)
    db.commit()

    for image in car_images:
        picture_path = save_uploaded_file(image)
        car_sell_images = models.CarSellImages(car_for_sale_id=add_car_for_sale.id, image_name=picture_path)
        db.add(car_sell_images)
        db.commit()

    for standard_feature in car_standard_features_ids:
        car_sell_standard_features = models.CarSellStandardFeatures(car_for_sale_id=add_car_for_sale.id,
                                                                    car_standard_features_id=standard_feature)
        db.add(car_sell_standard_features)
        db.commit()

    return {"message": "Car for sale created successfully", "data": car_for_sale}
