from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from database import db_dependency
from starlette import status
from UploadFile import FileHandler
import models
from sqlalchemy.orm import Session
from schemas import CarBrandBase, CarBrandUpdate
from typing import Optional, List
from database import db_dependency, get_db
from sqlalchemy import asc

router = APIRouter(tags=["CarBrand"], prefix="/car_brand")

UPLOAD_FOLDER = "BrandLogo"


@router.get("/list")
async def get_car_brands(db: db_dependency):
    # car_brand_list = db.query(models.CarBrand).order_by(models.CarBrand.id.desc()).all()
    car_brand_list = db.query(models.CarBrand).order_by(asc(models.CarBrand.name)).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    counts = {"car_brand": car_brand_count, "car_model": car_model_count, "car_trim": car_trim_count}
    return {"car_brand": car_brand_list, "counts": counts}
    # return car_brand_list


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_brand(
    brand_name: str = Form(...),
    brand_logo: UploadFile = File(...),
    country_id: str = Form(...),
    db: Session = Depends(get_db),
):
    # data_options = car_brand.dict()
    check_brand = (
        db.query(models.CarBrand).filter(models.CarBrand.name == brand_name).first()
    )
    if check_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Brand already exists"
        )
    # Upload logo to the server
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(brand_logo)
    car_brand = models.CarBrand(
        name=brand_name,
        country_name=country_id,
        brand_logo=saved_filename,
        created_at=datetime.now(),
    )
    db.add(car_brand)
    db.commit()
    db.refresh(car_brand)
    return {"message": "Car brand created successfully"}


@router.get("/get/{id}")
async def get_car_brand(id: int, db: db_dependency):
    car_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).first()
    return car_brand


@router.put("/update_car_brand")
async def update_car_brand(
    id: str = Form(...),
    brand_name: Optional[str] = Form(None),  # Use None as default value for optional parameters
    brand_logo: Optional[UploadFile] = File(None),
    country_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    check_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).first()
    if check_brand is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Brand does not exist"
        )

    # Define the update values in a dictionary
    if brand_name:
        check_brand.name = brand_name
    if brand_logo:
        file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
        saved_filename = file_handler.save_uploaded_file(brand_logo)
        check_brand.brand_logo = saved_filename
    if country_id:
        check_brand.country_name = country_id
    check_brand.updated_at = datetime.now()
    db.commit()
    return {"message": "Car brand updated successfully"}


@router.delete("/delete/{id}")
async def delete_car_brand(id: int, db: db_dependency):
    check_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).first()
    if check_brand is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Brand does not exist"
        )

    car_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).delete()
    db.commit()
    return {"message": "Car brand deleted successfully"}
