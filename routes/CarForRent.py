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


router = APIRouter(tags=["CarForRent"], prefix="/car_for_rent")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_FOLDER = "CarRentImages"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def save_uploaded_file(file: UploadFile):
    file_extension = file.filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, random_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return random_filename


def generate_short_stock_number():
    short_stock_number = str(uuid.uuid4())[:8]  # Generate an eight-character UUID
    return short_stock_number


@router.get("/list")
async def get_car_for_rent(
    make: str = None,
    model_id: str = None,
    min_input_price: float = Query(None),
    max_input_price: float = Query(None),
    db: Session = Depends(get_db),
):

    query = db.query(models.CarsForRent).order_by(models.CarsForRent.id.desc())

    if make:
        make_id = db.query(models.CarBrand).filter(models.CarBrand.name == make).first()
        if make_id:
            query = query.filter(models.CarsForRent.car_brand_id == make_id.id)

    if model_id:
        query = query.filter(models.CarsForRent.car_model_id == model_id)

    if min_input_price is not None and max_input_price is not None:
        query = query.filter(
            models.CarsForRent.car_price_per_day.between(
                min_input_price, max_input_price
            )
        )

    car_for_sale_list = query.all()
    count_cars_for_rent = query.filter(
        models.CarsForRent.car_status == "Available"
    ).count()

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
            db.query(models.CarRentImages)
            .filter(models.CarRentImages.car_for_rent_id == car.id)
            .options(load_only(models.CarRentImages.image_name))
            .all()
        )
        # Fetch and attach the features to the car object
        features_list = (
            db.query(models.CarStandardFeatures)
            .join(
                models.CarRentStandardFeatures,
                models.CarStandardFeatures.id
                == models.CarRentStandardFeatures.car_standard_features_id,
            )
            .filter(models.CarRentStandardFeatures.car_for_rent_id == car.id)
            .options(load_only(models.CarStandardFeatures.feature_name))
            .all()
        )
        # car.features = [features.feature_name in features_list for features in features_list]
        car.features = [feature for feature in features_list]
        car.features_ids = [feature.id for feature in features_list]
        # Add car_cover_image field to each car object
        car_cover_image = "/CarRentImages/" + car.cover_image
        car.cover_image = car_cover_image

        cars_for_sale.append(car)

    return {"cars_for_rent": cars_for_sale, "count_cars_for_rent": count_cars_for_rent}


@router.get("/makeModels")
async def get_car_make_models(
    make: str = None,
    model_id: str = None,
    min_input_price: float = Query(None),
    max_input_price: float = Query(None),
    start_year: int = Query(None),
    end_year: int = Query(None),
    start_kilometers: int = Query(None),
    end_kilometers: int = Query(None),
    car_transmission: str = Query(None),
    fuel_type: str = Query(None),
    shape: str = Query(None),
    db: Session = Depends(get_db),
):

    query = db.query(models.CarsForRent).order_by(models.CarsForRent.id.desc())

    if make:
        make_id = db.query(models.CarBrand).filter(models.CarBrand.name == make).first()
        if make_id:
            query = query.filter(models.CarsForRent.car_brand_id == make_id.id)

    if model_id:
        model = (
            db.query(models.CarModel)
            .filter(models.CarModel.brand_model_name == model_id)
            .first()
        )
        query = query.filter(models.CarsForRent.car_model_id == model.id)

    if min_input_price is not None and max_input_price is not None:
        query = query.filter(
            models.CarsForRent.car_price_per_day.between(
                min_input_price, max_input_price
            )
        )

    if start_year is not None and end_year is not None:
        startYear = int(start_year)  # Convert to integer if not already
        endYear = int(end_year)  # Convert to integer if not already
        query = query.filter(models.CarsForRent.car_year.between(startYear, endYear))

    if start_kilometers is not None and end_kilometers is not None:
        startKilometers = int(start_kilometers)
        endKilometers = int(end_kilometers)
        query = query.filter(
            models.CarsForRent.car_mileage.between(startKilometers, endKilometers)
        )
    if car_transmission:
        query = query.filter(models.CarsForRent.car_transmission == car_transmission)
    if fuel_type:
        query = query.filter(models.CarsForRent.car_fuel_type == fuel_type)

    if shape:
        query = query.filter(models.CarsForRent.car_body_type == shape)

    car_for_rent_list = query.all()

    count_cars_for_rent = query.filter(
        models.CarsForRent.car_status == "Available"
    ).count()

    cars_for_rent = []

    for car in car_for_rent_list:
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
            db.query(models.CarRentImages)
            .filter(models.CarRentImages.car_for_rent_id == car.id)
            .options(load_only(models.CarRentImages.image_name))
            .all()
        )
        # Fetch and attach the features to the car object
        features_list = (
            db.query(models.CarStandardFeatures)
            .join(
                models.CarRentStandardFeatures,
                models.CarStandardFeatures.id
                == models.CarRentStandardFeatures.car_standard_features_id,
            )
            .filter(models.CarRentStandardFeatures.car_for_rent_id == car.id)
            .options(load_only(models.CarStandardFeatures.feature_name))
            .all()
        )
        # car.features = [features.feature_name in features_list for features in features_list]
        car.features = [feature for feature in features_list]
        car.features_ids = [feature.id for feature in features_list]
        # Add car_cover_image field to each car object
        car_cover_image = "/CarRentImages/" + car.cover_image
        car.cover_image = car_cover_image

        cars_for_rent.append(car)

    return {"cars_for_rent": cars_for_rent, "count_cars_for_sale": count_cars_for_rent}


@router.get("/car_brands/")
async def get_car_brands(db: db_dependency):
    car_brand_list = db.query(models.CarBrand).order_by(asc(models.CarBrand.name)).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    car_standard_features_count = db.query(models.CarStandardFeatures).count()
    car_standard_features = db.query(models.CarStandardFeatures).all()
    car_for_rent = (
        db.query(models.CarsForRent)
        .filter(models.CarsForRent.car_status == "Available")
        .count()
    )
    cars_rented = (
        db.query(models.CarsForRent)
        .filter(models.CarsForRent.car_status == "Rented")
        .count()
    )

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
            "car_for_rent": car_for_rent,
            "cars_rented": cars_rented,
        },
        "car_standard_features": car_standard_features,
    }


@router.get("/list/{user_id}")
async def get_car_for_rent(user_id: int, db: db_dependency):
    car_for_rent_list = (
        db.query(models.CarsForRent).filter(models.CarsForRent.user_id == user_id).all()
    )
    return car_for_rent_list


@router.get("/makeModels")
async def get_car_make_models(
    make: str = None,
    model_id: str = None,
    min_input_price: float = Query(None),
    max_input_price: float = Query(None),
    start_year: int = Query(None),
    end_year: int = Query(None),
    start_kilometers: int = Query(None),
    end_kilometers: int = Query(None),
    car_transmission: str = Query(None),
    fuel_type: str = Query(None),
    shape: str = Query(None),
    db: Session = Depends(get_db),
):

    query = db.query(models.CarForSale).order_by(models.CarForSale.id.desc())

    if make:
        make_id = db.query(models.CarBrand).filter(models.CarBrand.name == make).first()
        if make_id:
            query = query.filter(models.CarForSale.car_brand_id == make_id.id)

    if model_id:
        model = (
            db.query(models.CarModel)
            .filter(models.CarModel.brand_model_name == model_id)
            .first()
        )
        query = query.filter(models.CarForSale.car_model_id == model.id)

    if min_input_price is not None and max_input_price is not None:
        query = query.filter(
            models.CarForSale.car_price.between(min_input_price, max_input_price)
        )

    if start_year is not None and end_year is not None:
        startYear = int(start_year)  # Convert to integer if not already
        endYear = int(end_year)  # Convert to integer if not already
        query = query.filter(models.CarForSale.car_year.between(startYear, endYear))

    if start_kilometers is not None and end_kilometers is not None:
        startKilometers = int(start_kilometers)
        endKilometers = int(end_kilometers)
        query = query.filter(
            models.CarForSale.car_mileage.between(startKilometers, endKilometers)
        )
    if car_transmission:
        query = query.filter(models.CarForSale.car_transmission == car_transmission)
    if fuel_type:
        query = query.filter(models.CarForSale.car_fuel_type == fuel_type)

    if shape:
        query = query.filter(models.CarForSale.car_body_type == shape)

    car_for_sale_list = query.all()

    count_cars_for_sale = query.filter(
        models.CarForSale.car_status == "Available"
    ).count()

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
        car.features = [feature for feature in features_list]
        car.features_ids = [feature.id for feature in features_list]
        # Add car_cover_image field to each car object
        car_cover_image = "/CarSellImages/" + car.cover_image
        car.cover_image = car_cover_image

        cars_for_sale.append(car)

    return {"cars_for_sale": cars_for_sale, "count_cars_for_sale": count_cars_for_sale}


@router.post("/create")
async def create_car_for_rent(
    user_id: str = Form(...),
    car_name_info: str = Form(...),
    car_brand_id: str = Form(...),
    car_model_id: str = Form(...),
    car_trim_id: str = Form(...),
    car_year: str = Form(...),
    car_mileage: str = Form(...),
    car_price_per_day: str = Form(...),
    car_price_per_week: str = Form(...),
    car_price_per_month: str = Form(...),
    car_price_per_day_up_country: str = Form(...),
    car_price_per_week_up_country: str = Form(...),
    car_price_per_month_up_country: str = Form(...),
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
    inspection_note: str = Form(...),
    car_condition: str = Form(...),
    car_renter_name: str = Form(...),
    renter_phone_number: str = Form(...),
    renter_email: str = Form(...),
    car_images: List[UploadFile] = File(...),  # Corrected type declaration
    cover_image: UploadFile = File(...),
    car_standard_features: List[str] = Form(...),  # Assuming these are integer IDs
    db: Session = Depends(get_db),
):

    car_standard_features_ids = [
        int(item) for item in car_standard_features[0].split(",")
    ]
    cover_image_path = save_uploaded_file(cover_image)
    short_stock_number = generate_short_stock_number()
    # Last added car for sale
    last_car = (
        db.query(models.CarsForRent).order_by(models.CarsForRent.id.desc()).first()
    )
    # Combine the last car ID with the short stock number
    if last_car is None:
        new_stock_number = f"{short_stock_number}1-R"
    else:
        new_stock_number = f"{short_stock_number}{last_car.id+1}-R"

    add_car_for_rent = models.CarsForRent(
        stock_number=new_stock_number,  # This should be generated dynamically
        user_id=user_id,
        car_name_info=car_name_info,
        car_brand_id=car_brand_id,
        car_model_id=car_model_id,
        car_trim_id=car_trim_id,
        car_year=car_year,
        car_mileage=car_mileage,
        car_price_per_day=car_price_per_day,
        car_price_per_week=car_price_per_week,
        car_price_per_month=car_price_per_month,
        car_price_per_day_up_country=car_price_per_day_up_country,
        car_price_per_week_up_country=car_price_per_week_up_country,
        car_price_per_month_up_country=car_price_per_month_up_country,
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
        inspection_note=inspection_note,
        renter_phone_number=renter_phone_number,
        renter_email=renter_email,
        cover_image=cover_image_path,
        car_condition=car_condition,
        car_renter_name=car_renter_name,
        created_at=datetime.now(),
    )
    db.add(add_car_for_rent)
    db.commit()

    for image in car_images:
        picture_path = save_uploaded_file(image)
        car_sell_images = models.CarRentImages(
            car_for_rent_id=add_car_for_rent.id,
            image_name=picture_path,
            created_at=datetime.now(),
        )
        db.add(car_sell_images)
        db.commit()

    for standard_feature in car_standard_features_ids:
        car_rent_standard_features = models.CarRentStandardFeatures(
            car_for_rent_id=add_car_for_rent.id,
            car_standard_features_id=standard_feature,
            created_at=datetime.now(),
        )
        db.add(car_rent_standard_features)
        db.commit()

    return {"message": "Car for rent successfully uplaoded"}


@router.put("/update")
async def update_car_for_rent(
    user_id: str = Form(None),
    car_id: str = Form(None),
    car_name_info: str = Form(None),
    car_brand_id: str = Form(None),
    car_model_id: str = Form(None),
    car_trim_id: str = Form(None),
    car_year: str = Form(None),
    car_mileage: str = Form(None),
    car_price_per_day: str = Form(None),
    car_price_per_week: str = Form(None),
    car_price_per_month: str = Form(None),
    car_price_per_day_up_country: str = Form(None),
    car_price_per_week_up_country: str = Form(None),
    car_price_per_month_up_country: str = Form(None),
    car_fuel_type: Optional[str] = Form(None),
    car_location: str = Form(None),
    car_exterior_color: str = Form(None),
    car_interior_color: str = Form(None),
    car_body_type: str = Form(None),
    car_transmission: str = Form(None),
    car_engine_capacity: str = Form(None),
    car_fuel_consumption: str = Form(None),
    car_drive_train: str = Form(None),
    car_vin_number: str = Form(None),
    car_registration_number: str = Form(None),
    car_insurance: str = Form(None),
    car_control_technique: str = Form(None),
    car_condition: str = Form(None),
    inspection_note: str = Form(None),
    renter_phone_number: str = Form(None),
    renter_email: str = Form(None),
    car_renter_name: str = Form(None),
    car_images: List[UploadFile] = File(None),  # Corrected type declaration
    # car_images: List[UploadFile] = File(...),  # Corrected type declaration
    cover_image: Optional[UploadFile] = File(None),
    car_standard_features: List[str] = Form(None),  # Assuming these are integer IDs
    db: Session = Depends(get_db),
):
    check_car_exist = (
        db.query(models.CarsForRent).filter(models.CarsForRent.id == car_id).first()
    )

    if not check_car_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car for rent not found"
        )
    if car_name_info:
        check_car_exist.car_name_info = car_name_info
    if car_brand_id:
        check_car_exist.car_brand_id = car_brand_id
    if car_model_id:
        check_car_exist.car_model_id = car_model_id
    if car_trim_id:
        check_car_exist.car_trim_id = car_trim_id
    if car_year:
        check_car_exist.car_year = car_year
    if car_mileage:
        check_car_exist.car_mileage = car_mileage
    if car_price_per_day:
        check_car_exist.car_price_per_day = car_price_per_day
    if car_price_per_week:
        check_car_exist.car_price_per_week = car_price_per_week
    if car_price_per_month:
        check_car_exist.car_price_per_month = car_price_per_month
    if car_price_per_day_up_country:
        check_car_exist.car_price_per_day_up_country = car_price_per_day_up_country
    if car_price_per_week_up_country:
        check_car_exist.car_price_per_week_up_country = car_price_per_week_up_country
    if car_price_per_month_up_country:
        check_car_exist.car_price_per_month_up_country = car_price_per_month_up_country
    if car_fuel_type:
        check_car_exist.car_fuel_type = car_fuel_type
    if car_location:
        check_car_exist.car_location = car_location
    if car_condition:
        check_car_exist.car_condition = car_condition
    if car_fuel_type:
        check_car_exist.car_fuel_type = car_fuel_type
    if car_exterior_color:
        check_car_exist.car_exterior_color = car_exterior_color
    if car_interior_color:
        check_car_exist.car_interior_color = car_interior_color
    if car_body_type:
        check_car_exist.car_body_type = car_body_type
    if car_transmission:
        check_car_exist.car_transmission = car_transmission
    if car_engine_capacity:
        check_car_exist.car_engine_capacity = car_engine_capacity
    if car_fuel_consumption:
        check_car_exist.car_fuel_consumption = car_fuel_consumption
    if car_drive_train:
        check_car_exist.car_drive_train = car_drive_train
    if car_vin_number:
        check_car_exist.car_vin_number = car_vin_number
    if car_registration_number:
        check_car_exist.car_registration_number = car_registration_number
    if car_insurance:
        check_car_exist.car_insurance = car_insurance
    if car_control_technique:
        check_car_exist.car_control_technique = car_control_technique
    if inspection_note:
        check_car_exist.inspection_note = inspection_note
    if car_renter_name:
        check_car_exist.car_renter_name = car_renter_name
    if renter_phone_number:
        check_car_exist.renter_phone_number = renter_phone_number
    if renter_email:
        check_car_exist.renter_email = renter_email
    if cover_image:
        cover_image_path = save_uploaded_file(cover_image)
        check_car_exist.cover_image = cover_image_path
    check_car_exist.updated_at = datetime.now()
    db.commit()

    if car_images:
        for image in car_images:
            picture_path = save_uploaded_file(image)
            car_sell_images = models.CarSellImages(
                car_for_rent_id=car_id,
                image_name=picture_path,
                created_at=datetime.now(),
            )
            db.add(car_sell_images)
            db.commit()

    for standard_feature in car_standard_features:

        check_if_feature_exist = (
            db.query(models.CarRentStandardFeatures)
            .filter(
                models.CarRentStandardFeatures.car_for_rent_id == car_id,
                models.CarRentStandardFeatures.car_standard_features_id
                == standard_feature,
            )
            .first()
        )

        if check_if_feature_exist is None:
            car_sell_standard_features = models.CarRentStandardFeatures(
                car_for_rent_id=car_id,
                car_standard_features_id=standard_feature,
                created_at=datetime.now(),
            )
            db.add(car_sell_standard_features)
            db.commit()

    return {"message": "Car for rent updated successfully"}


@router.delete("/delete/{id}")
async def delete_car_for_rent(id: int, db: db_dependency):
    check_car_exist = (
        db.query(models.CarsForRent).filter(models.CarsForRent.id == id).first()
    )
    if check_car_exist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car for rent not found"
        )

    delete_images = (
        db.query(models.CarSellImages)
        .filter(models.CarSellImages.car_for_sale_id == id)
        .delete()
    )
    delete_standard_features = (
        db.query(models.CarSellStandardFeatures)
        .filter(models.CarSellStandardFeatures.car_for_sale_id == id)
        .delete()
    )
    car_for_sale = (
        db.query(models.CarsForRent).filter(models.CarsForRent.id == id).delete()
    )
    db.commit()
    return {"message": "Car for rent deleted successfully"}


@router.get("/car_details")
async def get_car_details(id: str, db: db_dependency):
    car_detail = (
        db.query(models.CarsForRent)
        .filter(models.CarsForRent.stock_number == id)
        .first()
    )
    if car_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car details can not be found"
        )

    car_details = []
    car_detail.brand = (
        db.query(models.CarBrand)
        .filter(models.CarBrand.id == car_detail.car_brand_id)
        .options(load_only(models.CarBrand.name))
        .first()
    )
    car_detail.model = (
        db.query(models.CarModel)
        .filter(models.CarModel.id == car_detail.car_model_id)
        .options(load_only(models.CarModel.brand_model_name))
        .first()
    )
    car_detail.car_images = (
        db.query(models.CarRentImages)
        .filter(models.CarRentImages.car_for_rent_id == car_detail.id)
        .options(load_only(models.CarRentImages.image_name))
        .all()
    )
    # Fetch and attach the features to the car object
    features_list = (
        db.query(models.CarStandardFeatures)
        .join(
            models.CarRentStandardFeatures,
            models.CarStandardFeatures.id
            == models.CarRentStandardFeatures.car_standard_features_id,
        )
        .filter(models.CarRentStandardFeatures.car_for_rent_id == car_detail.id)
        .options(load_only(models.CarStandardFeatures.feature_name))
        .all()
    )
    # car.features = [features.feature_name in features_list for features in features_list]
    car_detail.features = [feature for feature in features_list]
    car_detail.features_ids = [feature.id for feature in features_list]
    # Add car_cover_image field to each car object
    car_cover_image = "/CarRentImages/" + car_detail.cover_image
    car_detail.cover_image = car_cover_image

    car_details.append(car_detail)

    return car_details


@router.get("/search")
async def search_car_for_rent(keyword: str, db: db_dependency):
    keywords = (
        db.query(models.CarsForRent)
        .filter(models.CarsForRent.car_name_info.ilike(f"%{keyword}%"))
        .all()
    )
    brand_keywords = (
        db.query(models.CarBrand)
        .filter(models.CarBrand.name.ilike(f"%{keyword}%"))
        .all()
    )
    # return brand_keywords

    # Return only car_name_info from the list and limit to 10
    return [keyword.car_name_info for keyword in keywords][:10]


@router.get("/search/{keyword}")
async def search_car_for_sale(keyword: str, db: db_dependency):
    keywords = (
        db.query(models.CarsForRent)
        .filter(models.CarsForRent.car_name_info == keyword)
        .first()
    )
    car_brand = keywords.car_brand
    car_model = keywords.car_model

    # Return only car_brand_name and car_model_name from the list
    return {"car_brand": car_brand.name, "car_model": car_model.brand_model_name}

    return keywords
