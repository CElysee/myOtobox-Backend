from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from database import db_dependency, get_db
from starlette import status
import models
import schemas
from UploadFile import FileHandler
from sqlalchemy import asc
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
import csv
from io import StringIO  # new import

router = APIRouter(tags=["CarTrim"], prefix="/car_trim")


@router.get("/list")
async def get_car_trims(db: db_dependency):
    car_trim_list = db.query(models.CarTrim).order_by(models.CarTrim.id.desc()).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    car_tim = []

    for trim in car_trim_list:
        car_tim.append(
            {
                "id": trim.id,
                "trim_code_name": trim.trim_code_name,
                "trim_name": trim.trim_name,
                "car_brand_id": trim.car_brand_id,
                "car_brand_name": db.query(models.CarBrand)
                .filter(models.CarBrand.id == trim.car_brand_id)
                .first()
                .name,
                "car_model_id": trim.car_model_id,
                "car_model_name": db.query(models.CarModel)
                .filter(models.CarModel.id == trim.car_model_id)
                .first()
                .brand_model_name,
                "engine_displacement": trim.engine_displacement,
                "engine": trim.engine,
                "curb_weight": trim.curb_weight,
                "trim_hp": trim.trim_hp,
                "created_at": trim.created_at,
            }
        )
    return {
        "car_trim": car_tim,
        "counts": {
            "car_brand": car_brand_count,
            "car_model": car_model_count,
            "car_trim": car_trim_count,
        },
    }


@router.get("/brand_models")
async def get_brand_models(db: db_dependency):
    # list brands with their models
    car_brand_list = db.query(models.CarBrand).order_by(asc(models.CarBrand.name)).all()
    car_brand = []
    for brand in car_brand_list:
        car_model_list = (
            db.query(models.CarModel).filter(models.CarModel.brand_id == brand.id).all()
        )
        car_model = []
        for model in car_model_list:
            car_model.append(
                {
                    "id": model.id,
                    "brand_model_name": model.brand_model_name,
                    "production_years": model.production_years,
                    "brand_model_image": model.brand_model_image,
                    "created_at": model.created_at,
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
    return car_brand


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_trim(car_trim: schemas.CarTrimBase, db: Session = Depends(get_db)):
    check_trim = (
        db.query(models.CarTrim)
        .filter(models.CarTrim.trim_name == car_trim.trim_name)
        .first()
    )
    if check_trim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Trim already exists"
        )

    # car_trim = models.CarTrim(**car_trim.dict())
    car_trim = models.CarTrim(
        car_brand_id=car_trim.car_brand_id,
        car_model_id=car_trim.car_model_id,
        trim_name=car_trim.trim_name,
        engine=car_trim.engine,
        curb_weight=car_trim.curb_weight,
        trim_hp=car_trim.trim_hp,
        trim_production_years=car_trim.trim_production_years,
        created_at=datetime.now(),
    )
    db.add(car_trim)
    db.commit()
    db.refresh(car_trim)
    return {"message": "Car trim created successfully", "data": car_trim}


@router.post("/create_excel")
async def create_car_trim_from_excel(
    db: Session = Depends(get_db),
    # car_brand_id: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    df = pd.read_csv(file.file)
    for i, row in df.iterrows():
        model_name = row["ModelName"]
        brand_name = row["BrandName"]
        check_brand_name = (
            db.query(models.CarBrand)
            .filter(models.CarBrand.name.ilike(f"%{brand_name}%"))
            .first()
        )
        if not check_brand_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {brand_name} not found",
            )
        chech_model_name = (
            db.query(models.CarModel)
            .filter(
                models.CarModel.brand_id == check_brand_name.id,
                models.CarModel.brand_model_name.ilike(f"%{model_name}%"),
            )
            .first()
        )
        if not chech_model_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_name} not found",
            )
        check_trim = (
            db.query(models.CarTrim)
            .filter(
                models.CarTrim.trim_name == row["TrimName"],
                models.CarTrim.trim_code_name == row["TrimCodeName"],
            )
            .first()
        )

        if check_trim:
            continue
        else:
            add_car_trim = models.CarTrim(
                car_brand_id=check_brand_name.id,
                car_model_id=chech_model_name.id,
                trim_name=row["TrimName"],
                trim_code_name=row["TrimCodeName"],
                engine=row["TrimEngineCC"],
                engine_displacement=row["TrimDisplacement"],
                curb_weight=row["TrimWeight"],
                trim_hp=row["TrimHP"],
                trim_production_years=row["TrimProductionYear"],
                created_at=datetime.now(),
            )
            db.add(add_car_trim)
            db.commit()

    return {"message": "Successfully uploaded Car Trim"}


@router.get("/get/{id}")
async def get_car_trim(id: int, db: db_dependency):
    car_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    return car_trim


@router.put("/update/{id}")
async def update_car_trim(id: int, car_trim: schemas.CarTrimUpdate, db: db_dependency):
    check_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    if check_trim is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Trim does not exist"
        )
    # Update only the fields with non-None values from car_trim
    if car_trim.trim_name:
        check_trim.trim_name = car_trim.trim_name

    if car_trim.car_model_id:
        check_trim.car_model_id = car_trim.car_model_id

    if car_trim.engine:
        check_trim.engine = car_trim.engine

    if car_trim.curb_weight:
        check_trim.curb_weight = car_trim.curb_weight
    if car_trim.trim_hp:
        check_trim.trim_hp = car_trim.trim_hp

    check_trim.updated_at = datetime.now()
    db.commit()
    return {"message": "Car trim updated successfully", "data": car_trim}


@router.delete("/delete/{id}")
async def delete_car_trim(id: int, db: db_dependency):
    check_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    if check_trim is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Trim does not exist"
        )
    car_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).delete()
    db.commit()
    return {"message": "Car trim deleted successfully"}
