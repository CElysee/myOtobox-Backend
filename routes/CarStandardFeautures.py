from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency
from starlette import status
import models
import schemas

router = APIRouter(tags=["CarStandardFeatures"], prefix="/car_standard_features")


@router.get("/list")
async def get_car_standard_features(db: db_dependency):
    car_standard_features_list = db.query(models.CarStandardFeatures).order_by(models.CarStandardFeatures.id.desc()).all()
    car_brand_count = db.query(models.CarBrand).count()
    car_model_count = db.query(models.CarModel).count()
    car_trim_count = db.query(models.CarTrim).count()
    car_standard_features = db.query(models.CarStandardFeatures).count()
    return {
        "counts": {
            "brand_count": car_brand_count,
            "model_count": car_model_count,
            "trim_count": car_trim_count,
            "standard_features_count": car_standard_features,
        },
        "standard_features": car_standard_features_list,
    }


@router.get("/list/{id}")
async def get_car_standard_features(id: int, db: db_dependency):
    car_standard_features = (
        db.query(models.CarStandardFeatures)
        .filter(models.CarStandardFeatures.id == id)
        .first()
    )
    if not car_standard_features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car Standard Features with id {id} not found",
        )
    return car_standard_features


@router.post("/create")
async def create_car_standard_features(
    car_standard_features: schemas.CarStandardFeaturesBase, db: db_dependency
):
    
    for feature in car_standard_features.features:
        check_car_standard_features = (
            db.query(models.CarStandardFeatures)
            .filter(models.CarStandardFeatures.feature_name == feature.feature_name)
            .first()
        )

        if not check_car_standard_features:
            db_car_standard_features = models.CarStandardFeatures(
                feature_name=feature.feature_name,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(db_car_standard_features)
            db.commit()
            db.refresh(db_car_standard_features)

    return {
        "message": "Car Standard Features created successfully",
        # "data": car_standard_features.feature_name,
    }


@router.put("/update/{id}")
async def update_car_standard_features(
    id: int, car_standard_features: schemas.CarStandardFeaturesUpdate, db: db_dependency
):
    check_car_standard_features = (
        db.query(models.CarStandardFeatures)
        .filter(models.CarStandardFeatures.id == id)
        .first()
    )
    if not check_car_standard_features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car Standard Features with id {id} not found",
        )
    check_car_standard_features.feature_name = car_standard_features.feature_name
    check_car_standard_features.updated_at = datetime.now()
    db.commit()
    return {"message": "Car Standard Features updated successfully"}


@router.delete("/delete/{id}")
async def delete_car_standard_features(id: int, db: db_dependency):
    check_car_standard_features = (
        db.query(models.CarStandardFeatures)
        .filter(models.CarStandardFeatures.id == id)
        .first()
    )
    if check_car_standard_features is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car Standard Features does not exist",
        )

    car_standard_features = (
        db.query(models.CarStandardFeatures)
        .filter(models.CarStandardFeatures.id == id)
        .delete()
    )
    db.commit()
    return {"message": "Car Standard Features deleted successfully"}
