import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from sqlalchemy.orm import Session, load_only, contains_eager

from database import db_dependency, SessionLocal
from starlette import status
import models
import schemas
from sqlalchemy import asc

router = APIRouter(tags=["CarForSale"], prefix="/car_for_sale")


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
async def get_car_for_sale(db: Session = Depends(get_db)):
    car_for_sale_list = db.query(models.CarForSale).all()
    cars_for_sale = []

    for car in car_for_sale_list:
        car.brand = (
            db.query(models.CarBrand)
            .filter(models.CarBrand.id == car.car_brand_id)
            .options(load_only(models.CarBrand.name))
            .first()
        )
        car.model = (
            db.query(models.CarModel)
            .filter(models.CarModel.id == car.car_model_id)
            .options(load_only(models.CarModel.brand_model_name))
            .first()
        )
        car.car_images = (
            db.query(models.CarSellImages)
            .filter(models.CarSellImages.car_for_sale_id == car.id)
            .options(load_only(models.CarSellImages.image_name))
            .all()
        )
        # Fetch and attach the features to the car object
        features_list = (
            db.query(models.CarStandardFeatures)
            .join(
                models.CarSellStandardFeatures,
                models.CarStandardFeatures.id
                == models.CarSellStandardFeatures.car_standard_features_id,
            )
            .filter(models.CarSellStandardFeatures.car_for_sale_id == car.id)
            .options(load_only(models.CarStandardFeatures.feature_name))
            .all()
        )
        # car.features = [features.feature_name in features_list for features in features_list]
        car.features = [feature.feature_name for feature in features_list]
        # Add car_cover_image field to each car object
        car_cover_image = "/CarSellImages/" + car.cover_image
        car.cover_image = car_cover_image
        
        cars_for_sale.append(car)

    return cars_for_sale


@router.get("/car_brands/")
async def get_car_brands(db: db_dependency):
    car_brand_list = db.query(models.CarBrand).order_by(asc(models.CarBrand.name)).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    car_standard_features_count = db.query(models.CarStandardFeatures).count()
    car_standard_features = db.query(models.CarStandardFeatures).all()

    car_brand = []

    for brand in car_brand_list:

        car_model_list = (
            db.query(models.CarModel).filter(models.CarModel.brand_id == brand.id).all()
        )
        car_model = []

        for model in car_model_list:

            car_trim_list = (
                db.query(models.CarTrim)
                .filter(models.CarTrim.car_model_id == model.id)
                .all()
            )
            car_trim = []
            for trim in car_trim_list:
                car_trim.append(
                    {
                        "id": trim.id,
                        "trim_name": trim.trim_name,
                    }
                )
            car_model.append(
                {
                    "id": model.id,
                    "brand_model_name": model.brand_model_name,
                    "production_years": model.production_years,
                    "brand_model_image": model.brand_model_image,
                    "created_at": model.created_at,
                    "trims": car_trim,
                }
            )
        car_brand.append(
            {
                "id": brand.id,
                "name": brand.name,
                "country_name": brand.country_name,
                "brand_logo": brand.brand_logo,
                "created_at": brand.created_at,
                "models": car_model,
            }
        )
    return {
        "car_brand": car_brand,
        "counts": {
            "brand_count": car_brand_count,
            "model_count": car_model_count,
            "trim_count": car_trim_count,
            "standard_features_count": car_standard_features_count,
        },
        "car_standard_features": car_standard_features,
    }


#     for brand in car_brands:
#         car_brand.append({
#             "brands": brand,
#         })
#         # car_brand.append(
#         #     {
#         #         "brands": brand,
#         #         "models": db.query(models.CarModel)
#         #         .filter(models.CarModel.brand_id == brand.id)
#         #         .all(),
#         #         "trims": db.query(models.CarTrim)
#         #         .filter(models.CarTrim.car_brand_id == brand.id)
#         #         .all(),
#         #     }
#         # )
#     return {
#         "car_brand": car_brand,
#         "counts": {
#             "brand_count": car_brand_count,
#             "model_count": car_model_count,
#             "trim_count": car_trim_count,
#             "standard_features_count": car_standard_features,
#         },
#     }


@router.get("/list/{user_id}")
async def get_car_for_sale(user_id: int, db: db_dependency):
    car_for_sale_list = (
        db.query(models.CarForSale).filter(models.CarForSale.user_id == user_id).all()
    )
    return car_for_sale_list


@router.post("/create")
async def create_car_for_sale(
    user_id: str = Form(...),
    car_name_info: str = Form(...),
    car_brand_id: str = Form(...),
    car_model_id: str = Form(...),
    car_trim_id: str = Form(...),
    car_year: str = Form(...),
    car_mileage: str = Form(...),
    car_price: str = Form(...),
    car_fuel_type: Optional[str] = Form(...),
    car_location: str = Form(...),
    car_exterior_color: str = Form(...),
    car_interior_color: str = Form(...),
    car_body_type: str = Form(...),
    car_transmission: str = Form(...),
    car_engine_capacity: str = Form(...),
    car_fuel_consumption: str = Form(...),
    car_drive_train: str = Form(...),
    car_vin_number: str = Form(...),
    car_registration_number: str = Form(...),
    car_insurance: str = Form(...),
    car_control_technique: str = Form(...),
    seller_note: str = Form(...),
    seller_phone_number: str = Form(...),
    seller_email: str = Form(...),
    car_images: List[UploadFile] = File(...),  # Corrected type declaration
    cover_image: UploadFile = File(...),
    car_standard_features: List[str] = Form(...),  # Assuming these are integer IDs
    db: Session = Depends(get_db),
):

    car_standard_features_ids = [
        int(item) for item in car_standard_features[0].split(",")
    ]
    cover_image_path = save_uploaded_file(cover_image)
    add_car_for_sale = models.CarForSale(
        user_id=user_id,
        car_name_info=car_name_info,
        car_brand_id=car_brand_id,
        car_model_id=car_model_id,
        car_trim_id=car_trim_id,
        car_year=car_year,
        car_mileage=car_mileage,
        car_price=car_price,
        car_location=car_location,
        car_fuel_type=car_fuel_type,
        car_exterior_color=car_exterior_color,
        car_interior_color=car_interior_color,
        car_body_type=car_body_type,
        car_transmission=car_transmission,
        car_engine_capacity=car_engine_capacity,
        car_fuel_consumption=car_fuel_consumption,
        car_drive_train=car_drive_train,
        car_vin_number=car_vin_number,
        car_registration_number=car_registration_number,
        car_insurance=car_insurance,
        car_control_technique=car_control_technique,
        car_status="Available",
        seller_note=seller_note,
        seller_phone_number=seller_phone_number,
        seller_email=seller_email,
        cover_image=cover_image_path,
        created_at=datetime.now(),
    )
    db.add(add_car_for_sale)
    db.commit()

    for image in car_images:
        picture_path = save_uploaded_file(image)
        car_sell_images = models.CarSellImages(
            car_for_sale_id=add_car_for_sale.id,
            image_name=picture_path,
            created_at=datetime.now(),
        )
        db.add(car_sell_images)
        db.commit()

    for standard_feature in car_standard_features_ids:
        car_sell_standard_features = models.CarSellStandardFeatures(
            car_for_sale_id=add_car_for_sale.id,
            car_standard_features_id=standard_feature,
            created_at=datetime.now(),
        )
        db.add(car_sell_standard_features)
        db.commit()

    return {"message": "Car for sale created successfully"}
