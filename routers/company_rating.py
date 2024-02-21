from typing import List, Union, Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from fmp import get_company_rating
from models import CompanyRating, Instruments

router = APIRouter(
    prefix="/company_rating",
    tags=["Company rating"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CompanyRatingResponse(BaseModel):
    id: int
    symbol: str
    rating_score: float
    rating_rating: str
    rating_recommendation: str



@router.get("", response_model=List[CompanyRatingResponse])
async def get_all_ratings(db: db_dependency):
    symbols = [instrument.foreign_symbol for instrument in db.query(Instruments).all()]
    response = []

    for symbol in symbols:
        rating_data = get_company_rating(symbol)

        if isinstance(rating_data, dict):
            rating_score = rating_data.get("ratingScore", 0)
            rating_rating = rating_data.get("rating", "")
            rating_recommendation = rating_data.get("ratingRecommendation", "")
        elif isinstance(rating_data, list) and rating_data:
            # Adjust accordingly based on the actual structure of the list response
            rating_score = rating_data[0].get("ratingScore", 0)
            rating_rating = rating_data[0].get("rating", "")
            rating_recommendation = rating_data[0].get("ratingRecommendation", "")
        else:
            rating_score = 0
            rating_rating = ""
            rating_recommendation = ""

        company_rating = db.query(CompanyRating).filter(CompanyRating.symbol == symbol).first()

        if not company_rating:
            company_rating = CompanyRating(
                symbol=symbol,
                rating_score=rating_score,
                rating_rating=rating_rating,
                rating_recommendation=rating_recommendation
            )
            db.add(company_rating)
            print(f"Se creó el rating para el símbolo {symbol}")
        else:
            company_rating.rating_score = rating_score
            company_rating.rating_rating = rating_rating
            company_rating.rating_recommendation = rating_recommendation
            print(f"Company rating actualizado para el símbolo {symbol}")

        db.commit()

        response.append(
            CompanyRatingResponse(
                id=company_rating.id,
                symbol=company_rating.symbol,
                rating_score=company_rating.rating_score,
                rating_rating=company_rating.rating_rating,
                rating_recommendation=company_rating.rating_recommendation
            )
        )

    return response


@router.get("/{symbol}", response_model=Union[CompanyRatingResponse])
async def get_by_symbol(symbol: str, db: db_dependency):
    if not db.query(Instruments).filter(Instruments.foreign_symbol == symbol).first():
        raise HTTPException(status_code=404, detail=f"El instrument {symbol} no está en la base de datos.")

    rating_data_list = get_company_rating(symbol)

    if not rating_data_list:
        raise HTTPException(status_code=500, detail=f"No se pudo obtener el company rating para {symbol}.")

    rating_data = rating_data_list[0]

    company_rating = db.query(CompanyRating).filter(CompanyRating.symbol == symbol).first()

    if not company_rating:
        company_rating = CompanyRating(
            symbol=symbol,
            rating_score=rating_data.get("ratingScore", 0),
            rating_rating=rating_data.get("rating", ""),
            rating_recommendation=rating_data.get("ratingRecommendation", "")
        )
        db.add(company_rating)
        db.commit()
        print(f"Company rating agregado para el símbolo {symbol}")
    else:
        company_rating.rating_score = rating_data.get("ratingScore", 0)
        company_rating.rating_rating = rating_data.get("rating", "")
        company_rating.rating_recommendation = rating_data.get("ratingRecommendation", "")
        db.commit()
        print(f"Company rating actualizado para el símbolo {symbol}")

    return CompanyRatingResponse(
        id=company_rating.id,
        symbol=company_rating.symbol,
        rating_score=company_rating.rating_score,
        rating_rating=company_rating.rating_rating,
        rating_recommendation=company_rating.rating_recommendation
    )
