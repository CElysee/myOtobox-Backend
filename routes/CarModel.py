from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from database import db_dependency
from starlette import status
import models
import schemas
from UploadFile import FileHandler
from database import db_dependency, get_db
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
import csv
from io import StringIO  # new import

router = APIRouter(tags=["CarModels"], prefix="/car_model")

UPLOAD_FOLDER = "BrandModel"


@router.get("/list")
async def get_car_models(db: db_dependency):
    car_model_list = db.query(models.CarModel).order_by(models.CarModel.id.desc()).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    car_model = []
    for model in car_model_list:
        car_model.append(
            {
                "id": model.id,
                "brand_model_name": model.brand_model_name,
                "brand_id": model.brand_id,
                "brand_name": db.query(models.CarBrand)
                .filter(models.CarBrand.id == model.brand_id)
                .first()
                .name,
                "production_years": model.production_years,
                "brand_model_image": f"/BrandModel/{model.brand_model_image}",
                "created_at": model.created_at,
            }
        )
    counts = {
        "car_brand": car_brand_count,
        "car_model": car_model_count,
        "car_trim": car_trim_count,
    }
    return {"car_model": car_model, "counts": counts}


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_model(
    brand_model_name: str = Form(...),
    brand_id: str = Form(...),
    production_years: str = Form(...),
    brand_model_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    check_model = (
        db.query(models.CarModel)
        .filter(models.CarModel.brand_model_name == brand_model_name)
        .first()
    )
    if check_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Model already exists"
        )

    # Upload logo to the server
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(brand_model_image)

    car_model = models.CarModel(
        brand_model_name=brand_model_name,
        brand_id=brand_id,
        production_years=production_years,
        brand_model_image=saved_filename,
        created_at=datetime.now(),
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)
    return {"message": "Car model created successfully", "data": car_model}


@router.post("/create_excel")
async def upload_using_excel(
    db: Session = Depends(get_db), file: UploadFile = File(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    df = pd.read_csv(file.file)
    for i, row in df.iterrows():
        name = row["BrandName"]
        chech_brand = (
            db.query(models.CarBrand)
            .filter(models.CarBrand.name.ilike(f"%{name}%"))
            .first()
        )
        
        if not chech_brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Brand {name} not found"
            )
        
        check_model = (
            db.query(models.CarModel)
            .filter(models.CarModel.brand_model_name == row["ModelName"])
            .first()
        )
        if check_model:
            continue  # Skip if model already exists
        else:
            car_model = models.CarModel(
                brand_model_name=row["ModelName"],
                brand_id=chech_brand.id,
                production_years=row["ProductionYears"],
                brand_model_image=row["ModelImage"],
                created_at=datetime.now(),
            )
            db.add(car_model)
            db.commit()

    return {"message": "Successfully uploaded Car Models"}


@router.get("/get/{id}")
async def get_car_model(id: int, db: db_dependency):
    car_model = db.query(models.CarModel).filter(models.CarModel.id == id).first()
    return car_model


@router.put("/update/")
async def update_car_model(
    id: str = Form(...),
    brand_model_name: str = Form(...),
    brand_id: str = Form(...),
    production_years: str = Form(...),
    brand_model_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    check_model = db.query(models.CarModel).filter(models.CarModel.id == id).first()
    if check_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Model does not exist"
        )

    if brand_id:
        check_model.brand_id = brand_id
    if brand_model_name:
        check_model.brand_model_name = brand_model_name
    if production_years:
        check_model.production_years = production_years
    if brand_model_image:
        file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
        saved_filename = file_handler.save_uploaded_file(brand_model_image)
        check_model.brand_model_image = saved_filename
    db.commit()

    return {"message": "Car model updated successfully"}


@router.delete("/delete/{id}")
async def delete_car_model(id: int, db: db_dependency):
    check_model = db.query(models.CarModel).filter(models.CarModel.id == id).first()
    if check_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Car Model does not exist"
        )
    car_model = db.query(models.CarModel).filter(models.CarModel.id == id).delete()
    db.commit()
    return {"message": "Car model deleted successfully"}
