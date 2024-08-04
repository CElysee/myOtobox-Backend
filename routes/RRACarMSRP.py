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
import numpy as np
from io import BytesIO
import csv
from io import StringIO  # new import

router = APIRouter(tags=["RRACarMSRP"], prefix="/rra-car-msrp")


@router.get("/list")
async def get_car_trims(db: db_dependency):
    car_msrp = db.query(models.RRACarMsrp).all()
    return car_msrp

@router.post("/create_excel")
async def create_car_trim_from_excel(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    df = pd.read_csv(file.file)

    # Replace nan values with None
    df = df.where(pd.notnull(df), None)

    for i, row in df.iterrows():
        # return row
        # Convert row to dictionary to ensure all values are handled properly
        row_dict = row.to_dict()

        # Replace nan values with None in the row dictionary
        for key, value in row_dict.items():
            if isinstance(value, float) and np.isnan(value):
                row_dict[key] = None

        check_car_msrp = (
            db.query(models.RRACarMsrp)
            .filter(
                models.RRACarMsrp.car_brand == row_dict["BRAND"],
                models.RRACarMsrp.car_mark == row_dict["MARK"],
                models.RRACarMsrp.car_engine == row_dict["ENGINE"],
                models.RRACarMsrp.car_drive == row_dict["DRIVE"],
                models.RRACarMsrp.car_year == row_dict["YEAR"],
                models.RRACarMsrp.body_style == row_dict["BODY STYLE"],
            )
            .first()
        )

        if check_car_msrp:
            continue
        else:
            add_rra_car_msrp = models.RRACarMsrp(
                car_brand=row_dict["BRAND"],
                car_mark=row_dict["MARK"],
                car_engine=row_dict["ENGINE"],
                car_drive=row_dict["DRIVE"],
                car_year=row_dict["YEAR"],
                # car_new_price=row_dict["WHEN NEW PRICES($)"],
                # car_new_price=row_dict["WHEN NEW PRICES"],
                car_new_price=row_dict[" WHEN NEW PRICES "],
                body_style=row_dict["BODY STYLE"],
                created_at=datetime.now(),
            )
            db.add(add_rra_car_msrp)
            db.commit()

    return {"message": "Successfully uploaded RRA CAR MSRP data"}
