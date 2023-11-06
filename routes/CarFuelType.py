from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency
from starlette import status
import models
import schemas

router = APIRouter(
    tags=["CarFuelType"],
    prefix='/car_fuel_type'
)


@router.get("/list")
async def get_car_fuel_type(db: db_dependency):
    car_fuel_type_list = db.query(models.CarFuelType).all()
    return car_fuel_type_list


@router.post('/create')
async def create_car_fuel_type(car_fuel_type: schemas.CarFuelTypeBase, db: db_dependency):

    for fuel_type in car_fuel_type.fuel_type:
        check_car_fuel_type = db.query(models.CarFuelType).filter(
            models.CarFuelType.fuel_type == fuel_type).first()
        if check_car_fuel_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel type already exists")

        car_fuel_type = models.CarFuelType(
            fuel_type=fuel_type,
            created_at=datetime.now()
        )
        db.add(car_fuel_type)
        db.commit()

    db.refresh(car_fuel_type)
    return {"message": "Fuel type created successfully", "data": car_fuel_type.fuel_type}


@router.get("/get/{id}")
async def get_car_fuel_type(id: int, db: db_dependency):
    car_fuel_type = db.query(models.CarFuelType).filter(models.CarFuelType.id == id).first()
    if car_fuel_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel type does not exist")
    return car_fuel_type


@router.put("/update/{id}")
async def update_car_fuel_type(id: int, car_fuel_type: schemas.CarFuelTypeUpdate, db: db_dependency):
    check_car_fuel_type = db.query(models.CarFuelType).filter(models.CarFuelType.id == id).first()
    if check_car_fuel_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel type does not exist")
    updated_values = {
        "fuel_type": car_fuel_type.fuel_type,
        "updated_at": datetime.now()
    }
    car_fuel_type = db.query(models.CarFuelType).filter(models.CarFuelType.id == id).update(updated_values)
    db.commit()
    return {"message": "Fuel type updated successfully"}


@router.delete("/delete/{id}")
async def delete_car_fuel_type(id: int, db: db_dependency):
    check_car_fuel_type = db.query(models.CarFuelType).filter(models.CarFuelType.id == id).first()
    if check_car_fuel_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel type does not exist")
    car_fuel_type = db.query(models.CarFuelType).filter(models.CarFuelType.id == id).delete()
    db.commit()
    return {"message": "Fuel type deleted successfully"}
