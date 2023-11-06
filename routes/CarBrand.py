from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency
from starlette import status
import models
import schemas

router = APIRouter(
    tags=["CarBrand"],
    prefix='/car_brand'
)


@router.get("/list")
async def get_car_brands(db: db_dependency):
    car_brand_list = db.query(models.CarBrand).all()
    return car_brand_list


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_brand(car_brand: schemas.CarBrandBase, db: db_dependency):
    check_brand = db.query(models.CarBrand).filter(models.CarBrand.name == car_brand.name).first()
    if check_brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand already exists")

    car_brand = models.CarBrand(**car_brand.dict())
    db.add(car_brand)
    db.commit()
    db.refresh(car_brand)
    return {"message": "Car brand created successfully", "data": car_brand}


@router.get("/get/{id}")
async def get_car_brand(id: int, db: db_dependency):
    car_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).first()
    return car_brand


@router.put("/update/{id}")
async def update_car_brand(id: int, car_brand: schemas.CarBrandBase, db: db_dependency):
    check_brand = db.query(models.CarBrand).filter(models.CarBrand.id == car_brand.id).first()
    if check_brand is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand does not exist")

    car_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).update(car_brand.dict())
    db.commit()
    return {"message":"Car brand updated successfully", "data": car_brand}


@router.delete("/delete/{id}")
async def delete_car_brand(id: int, db: db_dependency):
    car_brand = db.query(models.CarBrand).filter(models.CarBrand.id == id).delete()
    db.commit()
    return {"message":"Car brand deleted successfully"}
