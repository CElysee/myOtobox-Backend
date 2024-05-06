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


router = APIRouter(tags=["TaxCalculator"], prefix="/tax-calculator")

def calculate_taxes(user_request):
    # Calculate import_duty_tax based on vehicle category
    current_value_in_rwf = float(user_request.current_value)
    weight_value = float(user_request.weight)

    if (
        user_request.vehicle_category == "Motor vehicles with  engine capacity less or equal to 1500 cc"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (current_value_in_rwf + import_duty_tax + (weight_value * 10)) * 0.05
        
    elif (
        user_request.vehicle_category == "Motor vehicles with engine capacity of 1500 cc to 2500cc"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (current_value_in_rwf + import_duty_tax + (weight_value * 10)) * 0.1
        
    elif (user_request.vehicle_category == "Motor vehicles with engine capacity above 2500cc"):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (current_value_in_rwf + import_duty_tax + (weight_value * 10)) * 0.15
        
    elif (user_request.vehicle_category == "Tractors" or user_request.vehicle_category == "Truck with carrying capacity exceeding 20 Tones"):
        import_duty_tax = 0
        excise_duty_tax = 0 
    elif (user_request.vehicle_category == "Minbuses (Seating capacity not exceeding 25 places)"):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = 0
        
    elif (user_request.vehicle_category == "Buses (Seating capacity exceeding 25 places)"):
        import_duty_tax = current_value_in_rwf * 0.1
        excise_duty_tax = 0  
        
    elif (user_request.vehicle_category == "Pick up"):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = 0
    elif (user_request.vehicle_category == "Truck with carrying capacity not exceeding 20 Tones"):  
        import_duty_tax = current_value_in_rwf * 0.1
        excise_duty_tax = 0

    # Calculate withholding_tax based on quitus fiscal status       
    
    if user_request.quitus_fiscal == "Yes":
        withholding_tax = 0 
    else:
        withholding_tax = current_value_in_rwf * 0.05
        
    # Calculate plate_fee based on engine_cc    
    if (user_request.engine_cc <= 1000):
        plate_fee = "75000"    
    elif (user_request.engine_cc >= 1001 and user_request.engine_cc <= 1500):
        plate_fee = "160000"      
    elif (user_request.engine_cc >= 1501 and user_request.engine_cc <= 3000):
        plate_fee = "250000"      
    elif (user_request.engine_cc >= 3001 and user_request.engine_cc <= 4500):   
        plate_fee = "420000" 
    else:
        plate_fee = "560000" 

    # Calculate vat_tax, idl_tax, aul_tax (assuming these are constants)
    vat_tax = round((float(user_request.current_value) + import_duty_tax + excise_duty_tax + (float(user_request.weight) * 10)) * 0.18)
    idl_tax = round(float(user_request.current_value) * 0.015)
    aul_tax = round(float(user_request.current_value) * 0.002)

    return import_duty_tax, excise_duty_tax, plate_fee, vat_tax, idl_tax, aul_tax, withholding_tax

@router.get("/list")
def get_all_tax_calculator(db: db_dependency):
    list = (
        db.query(models.TaxCalculator)
        .order_by(models.TaxCalculator.created_at.desc())
        .all()
    )
    return list


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_tax_calculator(user_request: schemas.TaxCalculatorCreate, db: db_dependency):
    # Convert string inputs to appropriate data types
    current_value_in_rwf = float(user_request.current_value)
    weight_value = float(user_request.weight)
    engine_cc = int(user_request.engine_cc)
    
    # Calculate taxes and fees
    import_duty_tax, excise_duty_tax, plate_fee, vat_tax, idl_tax, aul_tax , withholding_tax = calculate_taxes(user_request)
    
    # Calculate total tax
    total_tax = round(
        import_duty_tax
        + excise_duty_tax
        + vat_tax
        + idl_tax
        + withholding_tax
        + aul_tax
        + float(plate_fee)
    )
    
    # Create new TaxCalculator instance
    new_tax_calculator = models.TaxCalculator(
        user_id=user_request.user_id,
        car_brand_id=user_request.car_brand_id,
        car_model_id=user_request.car_model_id,
        car_trim_id=user_request.car_trim_id,
        weight=weight_value,
        engine_cc=engine_cc,
        year_of_manufacture=user_request.year_of_manufacture,
        price_when_new=user_request.price_when_new,
        amortisation_period=user_request.amortisation_period,
        current_residual_value=user_request.current_residual_value,
        freight_cost=user_request.freight_cost,
        insurance=user_request.insurance,
        cif_kigali=user_request.cif_kigali,
        current_value=current_value_in_rwf,
        quitus_fiscal=user_request.quitus_fiscal,
        vehicle_category=user_request.vehicle_category,
        import_duty_tax=import_duty_tax,
        excise_duty_tax=excise_duty_tax,
        vat_tax=vat_tax,
        idl_tax=idl_tax,
        withholding_tax=withholding_tax,
        plate_fee=plate_fee,
        aul_tax=aul_tax,
        total_tax=total_tax,
        created_at=datetime.now(),
    )
    
    # Add new_tax_calculator to the database session
    db.add(new_tax_calculator)
    
    # Commit the session to persist changes
    db.commit()
    
    # Refresh the object to reflect changes made during commit
    db.refresh(new_tax_calculator)
    
    return {"message": "Tax calculator created successfully", "data_id": new_tax_calculator.id}


@router.get("/get/{id}")
def get_tax_calculator_by_id(id: int, db: db_dependency):
    tax_calculator = db.query(models.TaxCalculator).filter(models.TaxCalculator.id == id).first()
    if tax_calculator is None:
        raise HTTPException(status_code=404, detail="Tax calculator not found")
    if tax_calculator.car_brand_id:
        car_brand = tax_calculator.car_brand
    if tax_calculator.car_model_id:    
        car_model = tax_calculator.car_model
    if tax_calculator.car_trim_id:
        car_trim = tax_calculator.car_trim
    if tax_calculator is None:
        raise HTTPException(status_code=404, detail="Tax calculator not found")
    return tax_calculator