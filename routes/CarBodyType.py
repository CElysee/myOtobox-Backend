from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from database import db_dependency
from starlette import status
from UploadFile import FileHandler
import models
from sqlalchemy.orm import Session
from schemas import CarBodyTypeCreate, CarBrandUpdate
from typing import Optional, List
from database import db_dependency, get_db
from sqlalchemy import asc

router = APIRouter(tags=["CarBodyType"], prefix="/car_body_type")

UPLOAD_FOLDER = "BodyTypeImage"


@router.get("/list")
async def get_car_body_types(db: db_dependency):
    car_body_type_list = db.query(models.CarBodyType).order_by(asc(models.CarBodyType.body_type_name)).all()
    car_body_type_count = db.query(models.CarBodyType).count()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    counts = {"car_brand": car_brand_count, "car_model": car_model_count, "car_trim": car_trim_count, "car_body_type": car_body_type_count}
    return {"car_body": car_body_type_list, "counts": counts}


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car_body_type(
    body_type_name: str = Form(...),
    body_type_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    check_body = (
        db.query(models.CarBodyType).filter(models.CarBodyType.body_type_name == body_type_name).first()
    )
    if check_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Body type already exists"
        )
    # Upload logo to the server
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(body_type_image)
    car_body_type = models.CarBodyType(
        body_type_name=body_type_name,
        body_type_image=saved_filename,
        created_at=datetime.now(),
    )
    db.add(car_body_type)
    db.commit()
    db.refresh(car_body_type)
    return {"message": "Car body type created successfully"}


@router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_car_body_type(
    id: int,
    body_type_name: Optional[str] = Form(None),
    body_type_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    car_body_type = db.query(models.CarBodyType).filter(models.CarBodyType.id == id).first()
    if not car_body_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Body type not found"
        )
    if body_type_image:
    # Upload logo to the server
        file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
        saved_filename = file_handler.save_uploaded_file(body_type_image)
        car_body_type.body_type_image = saved_filename
        
    if body_type_name:
        car_body_type.body_type_name = body_type_name
        
    car_body_type.updated_at = datetime.now()
    
    db.commit()
    db.refresh(car_body_type)
    return {"message": "Car body type updated successfully"}

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_body_type(id: int, db: Session = Depends(get_db)):
    car_body_type = db.query(models.CarBodyType).filter(models.CarBodyType.id == id).first()
    if not car_body_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Body type not found"
        )
    db.delete(car_body_type)
    db.commit()
    return {"message": "Car body type deleted successfully"}