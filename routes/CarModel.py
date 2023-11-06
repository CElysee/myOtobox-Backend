from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency
from starlette import status
import models
import schemas

router = APIRouter(
    tags=["CarModels"],
    prefix='/car_model'
)


@router.get("/list")
async def get_car_models(db: db_dependency):
    car_model_list = db.query(models.CarModel).all()
    return car_model_list


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_model(car_model: schemas.CarModelBase, db: db_dependency):
    check_model = db.query(models.CarModel).filter(
        models.CarModel.brand_model_name == car_model.brand_model_name).first()
    if check_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model already exists")

    car_model = models.CarModel(**car_model.dict())
    db.add(car_model)
    db.commit()
    db.refresh(car_model)
    return {"message":"Car model created successfully", "data": car_model}


@router.get("/get/{id}")
async def get_car_model(id: int, db: db_dependency):
    car_model = db.query(models.CarModel).filter(models.CarModel.id == id).first()
    return car_model


@router.put("/update/{id}")
async def update_car_model(id: int, car_model: schemas.CarModelBase, db: db_dependency):
    check_model = db.query(models.CarModel).filter(models.CarModel.id == car_model.id).first()
    if check_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model does not exist")

    car_model = db.query(models.CarModel).filter(models.CarModel.id == id).update(car_model.dict())
    db.commit()
    return {"message": "Car model updated successfully", "data": car_model}


@router.delete("/delete/{id}")
async def delete_car_model(id: int, db: db_dependency):
    car_model = db.query(models.CarModel).filter(models.CarModel.id == id).delete()
    db.commit()
    return {"message": "Car model deleted successfully"}

