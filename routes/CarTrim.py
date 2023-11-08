from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency
from starlette import status
import models
import schemas

router = APIRouter(
    tags=["CarTrim"],
    prefix='/car_trim'
)


@router.get("/list")
async def get_car_trims(db: db_dependency):
    car_trim_list = db.query(models.CarTrim).all()
    return car_trim_list


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_trim(car_trim: schemas.CarTrimBase, db: db_dependency):
    check_trim = db.query(models.CarTrim).filter(
        models.CarTrim.trim_name == car_trim.trim_name).first()
    if check_trim:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trim already exists")

    car_trim = models.CarTrim(**car_trim.dict())
    db.add(car_trim)
    db.commit()
    db.refresh(car_trim)
    return {"message": "Car trim created successfully", "data": car_trim}


@router.get("/get/{id}")
async def get_car_trim(id: int, db: db_dependency):
    car_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    return car_trim


@router.put("/update/{id}")
async def update_car_trim(id: int, car_trim: schemas.CarTrimUpdate, db: db_dependency):
    check_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    if check_trim is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trim does not exist")
    updated_values = {
        "trim_name": car_trim.trim_name,
        "car_model_id": car_trim.car_model_id,
        "engine": car_trim.engine,
        "curb_weight": car_trim.curb_weight,
        "updated_at": datetime.now(),
    }
    car_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).update(updated_values)
    db.commit()
    return {"message": "Car trim updated successfully", "data": car_trim}


@router.delete("/delete/{id}")
async def delete_car_trim(id: int, db: db_dependency):
    check_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).first()
    if check_trim is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trim does not exist")
    car_trim = db.query(models.CarTrim).filter(models.CarTrim.id == id).delete()
    db.commit()
    return {"message": "Car trim deleted successfully"}
