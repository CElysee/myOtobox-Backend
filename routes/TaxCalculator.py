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
from sqlalchemy import asc, or_, and_, desc
import hashlib
import random
from openai import OpenAI


router = APIRouter(tags=["TaxCalculator"], prefix="/tax-calculator")


def calculate_taxes(user_request):
    # Calculate import_duty_tax based on vehicle category
    current_value_in_rwf = float(user_request.current_value)
    weight_value = float(user_request.weight)

    if (
        user_request.vehicle_category
        == "Motor vehicles with  engine capacity less or equal to 1500 cc"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (
            current_value_in_rwf + import_duty_tax + (weight_value * 10)
        ) * 0.05

    elif (
        user_request.vehicle_category
        == "Motor vehicles with engine capacity of 1500 cc to 2500cc"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (
            current_value_in_rwf + import_duty_tax + (weight_value * 10)
        ) * 0.1

    elif (
        user_request.vehicle_category
        == "Motor vehicles with engine capacity above 2500cc"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = (
            current_value_in_rwf + import_duty_tax + (weight_value * 10)
        ) * 0.15

    elif (
        user_request.vehicle_category == "Tractors"
        or user_request.vehicle_category
        == "Truck with carrying capacity exceeding 20 Tones"
    ):
        import_duty_tax = 0
        excise_duty_tax = 0
    elif (
        user_request.vehicle_category
        == "Minbuses (Seating capacity not exceeding 25 places)"
    ):
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = 0

    elif (
        user_request.vehicle_category == "Buses (Seating capacity exceeding 25 places)"
    ):
        import_duty_tax = current_value_in_rwf * 0.1
        excise_duty_tax = 0

    elif user_request.vehicle_category == "Pick up":
        import_duty_tax = current_value_in_rwf * 0.25
        excise_duty_tax = 0
    elif (
        user_request.vehicle_category
        == "Truck with carrying capacity not exceeding 20 Tones"
    ):
        import_duty_tax = current_value_in_rwf * 0.1
        excise_duty_tax = 0

    # Calculate withholding_tax based on quitus fiscal status

    if user_request.quitus_fiscal == "Yes":
        withholding_tax = 0
    else:
        withholding_tax = current_value_in_rwf * 0.05

    # Calculate plate_fee based on engine_cc
    if user_request.engine_cc <= 1000:
        plate_fee = "75000"
    elif user_request.engine_cc >= 1001 and user_request.engine_cc <= 1500:
        plate_fee = "160000"
    elif user_request.engine_cc >= 1501 and user_request.engine_cc <= 3000:
        plate_fee = "250000"
    elif user_request.engine_cc >= 3001 and user_request.engine_cc <= 4500:
        plate_fee = "420000"
    else:
        plate_fee = "560000"

    # Calculate vat_tax, idl_tax, aul_tax (assuming these are constants)
    vat_tax = round(
        (
            float(user_request.current_value)
            + import_duty_tax
            + excise_duty_tax
            + (float(user_request.weight) * 10)
        )
        * 0.18
    )
    idl_tax = round(float(user_request.current_value) * 0.015)
    aul_tax = round(float(user_request.current_value) * 0.002)

    return (
        import_duty_tax,
        excise_duty_tax,
        plate_fee,
        vat_tax,
        idl_tax,
        aul_tax,
        withholding_tax,
    )


@router.get("/list")
def get_all_tax_calculator(db: db_dependency):
    list = (
        db.query(models.TaxCalculator)
        .order_by(models.TaxCalculator.created_at.desc())
        .all()
    )
    tax_calculator_list = []
    for tax_calculator in list:
        if tax_calculator.car_brand_id:
            car_brand = tax_calculator.car_brand
        if tax_calculator.car_model_id:
            car_model = tax_calculator.car_model
        if tax_calculator.car_trim_id:
            car_trim = tax_calculator.car_trim
        tax_calculator_list.append(tax_calculator)
        if tax_calculator.user_id:
            user = tax_calculator.user

    # Counts
    count_tax_calculations = db.query(models.TaxCalculator).count()
    count_brands = db.query(models.CarBrand).count()
    count_models = db.query(models.CarModel).count()
    count_trims = db.query(models.CarTrim).count()

    return {
        "tax_calculations": tax_calculator_list,
        "counts": {
            "count_tax_calculations": count_tax_calculations,
            "count_brands": count_brands,
            "count_models": count_models,
            "count_trims": count_trims,
        },
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_tax_calculator(
    user_request: schemas.TaxCalculatorCreate, db: db_dependency
):
    # Convert string inputs to appropriate data types
    current_value_in_rwf = float(user_request.current_value)
    weight_value = float(user_request.weight)
    engine_cc = int(user_request.engine_cc)

    # Calculate taxes and fees
    (
        import_duty_tax,
        excise_duty_tax,
        plate_fee,
        vat_tax,
        idl_tax,
        aul_tax,
        withholding_tax,
    ) = calculate_taxes(user_request)

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
        price_source=user_request.price_source,
        created_at=datetime.now(),
    )

    # Add new_tax_calculator to the database session
    db.add(new_tax_calculator)

    # Commit the session to persist changes
    db.commit()

    # Refresh the object to reflect changes made during commit
    db.refresh(new_tax_calculator)

    return {
        "message": "Tax calculator created successfully",
        "data_id": new_tax_calculator.id,
    }


@router.get("/get/{id}")
def get_tax_calculator_by_id(id: int, db: db_dependency):
    tax_calculator = (
        db.query(models.TaxCalculator).filter(models.TaxCalculator.id == id).first()
    )
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


@router.post("/find-msrp")
async def find_msrp(db: db_dependency, msrp_request: schemas.FindMsrp):
    # return msrp_request
    def generate_search_patterns(search_term: str) -> list:
        if not search_term:
            return []
        patterns = [
            search_term,
            search_term.replace(" ", "-"),
            search_term.replace("-", " "),
        ]
        return patterns

    car_brand = (
        db.query(models.CarBrand)
        .filter(models.CarBrand.id == msrp_request.car_brand)
        .first()
    )
    car_brand_model = (
        db.query(models.CarModel)
        .filter(models.CarModel.id == msrp_request.car_mark)
        .first()
    )
    engineDisplacement = msrp_request.car_engine[:3]
    car_brand_patterns = generate_search_patterns(car_brand.name)
    car_mark_patterns = generate_search_patterns(car_brand_model.brand_model_name)
    car_engine_patterns = generate_search_patterns(engineDisplacement)
    car_drive_patterns = generate_search_patterns(msrp_request.car_drive)
    car_year_patterns = generate_search_patterns(msrp_request.car_year)
    body_style_patterns = generate_search_patterns(msrp_request.body_style)

    query = db.query(models.RRACarMsrp)

    if car_brand_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.car_brand.like(f"%{pattern}%")
                    for pattern in car_brand_patterns
                ]
            )
        )
    if car_mark_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.car_mark.like(f"%{pattern}%")
                    for pattern in car_mark_patterns
                ]
            )
        )
    if car_engine_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.car_engine.like(f"%{pattern}%")
                    for pattern in car_engine_patterns
                ]
            )
        )
    if car_drive_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.car_drive.like(f"%{pattern}%")
                    for pattern in car_drive_patterns
                ]
            )
        )
    if car_year_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.car_year.like(f"%{pattern}%")
                    for pattern in car_year_patterns
                ]
            )
        )
    if body_style_patterns:
        query = query.filter(
            or_(
                *[
                    models.RRACarMsrp.body_style.like(f"%{pattern}%")
                    for pattern in body_style_patterns
                ]
            )
        )

    msrp_records = query.all()

    # Additional filtering to match exact fields
    filtered_records = [
        record
        for record in msrp_records
        if (
            not msrp_request.car_drive
            or msrp_request.car_drive.lower() in record.car_drive.lower()
        )
        and (
            not msrp_request.body_style
            or msrp_request.body_style.lower() in record.body_style.lower()
        )
    ]

    return filtered_records


@router.post("/find-msrp-open-ai")
async def find_msrp_open_ai(db: db_dependency, msrp_request: schemas.FindMsrp):
    car_brand = (
        db.query(models.CarBrand)
        .filter(models.CarBrand.id == msrp_request.car_brand)
        .first()
    )
    car_brand_model = (
        db.query(models.CarModel)
        .filter(models.CarModel.id == msrp_request.car_mark)
        .first()
    )
    query = f"Find the MSRP for a {msrp_request.car_year} {car_brand.name} {car_brand_model.brand_model_name} with a {msrp_request.car_engine} engine, {msrp_request.car_drive} drive, and {msrp_request.body_style} body style."
    client = OpenAI()


    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
            },
            {
                "role": "user",
                "content": "Compose a poem that explains the concept of recursion in programming.",
            },
        ],
    )

    response = completion.choices[0].message
    return response
