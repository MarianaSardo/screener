from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from fmp import get_stock_prices
from models import Instruments, StockPrice

router = APIRouter(
    prefix="/stock_prices",
    tags=["Stock Prices"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class StockPriceResponse(BaseModel):
    id: int
    symbol: str
    name: str
    price: float
    changes_percentage: float
    change: float
    day_low: float
    day_high: float
    year_high: float
    year_low: float
    market_cap: float
    price_avg50: float
    price_avg200: float
    exchange: str
    volume: int
    avg_volume: int
    open: float
    previous_close: float
    eps: float
    pe: float
    earnings_announcement: Optional[datetime]
    shares_outstanding: int
    timestamp: Optional[datetime]

    @validator("earnings_announcement", pre=True, always=True)
    def parse_earnings_announcement(cls, value):
        if value is None:
            return None
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            raise ValueError("Invalid type for earnings_announcement")

    @validator("timestamp", pre=True, always=True)
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        return datetime.utcfromtimestamp(value)


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("", response_model=List[StockPriceResponse], status_code=status.HTTP_200_OK)
async def get_all_prices(db: db_dependency) -> List[StockPriceResponse]:
    stock_prices = db.query(StockPrice).all()
    return [StockPriceResponse(**stock_price.__dict__) for stock_price in stock_prices]


@router.get("/{symbol}", response_model=StockPriceResponse, status_code=status.HTTP_200_OK)
async def get_by_symbol(db: db_dependency, symbol: str) -> StockPriceResponse:
    stock_price = db.query(StockPrice).filter(StockPrice.symbol == symbol).first()
    if stock_price is not None:
        return StockPriceResponse(**stock_price.__dict__)
    raise HTTPException(status_code=404,
                        detail=f'Precio no encontrado. El simbolo {symbol} no se encuentra en la base de datos.')


@router.put("", response_model=str)
async def update_all_prices(db: db_dependency):
    symbols = [instrument.foreign_symbol for instrument in db.query(Instruments).all()]
    response = []

    for symbol in symbols:
        stock_data = get_stock_prices(symbol)
        stock_price = db.query(StockPrice).filter(StockPrice.symbol == symbol).first()

        if not stock_price:
            stock_price = StockPrice(
                symbol=stock_data["symbol"],
                price=stock_data["price"],
                name=stock_data["name"],
                changes_percentage=stock_data["changesPercentage"],
                change=stock_data["change"],
                day_low=stock_data["dayLow"],
                day_high=stock_data["dayHigh"],
                year_high=stock_data["yearHigh"],
                year_low=stock_data["yearLow"],
                market_cap=stock_data["marketCap"],
                price_avg50=stock_data["priceAvg50"],
                price_avg200=stock_data["priceAvg200"],
                exchange=stock_data["exchange"],
                volume=stock_data["volume"],
                avg_volume=stock_data["avgVolume"],
                open=stock_data["open"],
                previous_close=stock_data["previousClose"],
                eps=stock_data["eps"],
                pe=stock_data["pe"],
                earnings_announcement=stock_data["earningsAnnouncement"],
                shares_outstanding=stock_data["sharesOutstanding"],
                timestamp=stock_data["timestamp"]
            )
            db.add(stock_price)

        else:
            stock_price.price = stock_data["price"]
            stock_price.changes_percentage = stock_data["changesPercentage"]
            stock_price.name = stock_data["name"]
            stock_price.change = stock_data["change"]
            stock_price.day_low = stock_data["dayLow"]
            stock_price.day_high = stock_data["dayHigh"]
            stock_price.year_high = stock_data["yearHigh"]
            stock_price.year_low = stock_data["yearLow"]
            stock_price.market_cap = stock_data["marketCap"]
            stock_price.price_avg50 = stock_data["priceAvg50"]
            stock_price.price_avg200 = stock_data["priceAvg200"]
            stock_price.exchange = stock_data["exchange"]
            stock_price.volume = stock_data["volume"]
            stock_price.avg_volume = stock_data["avgVolume"]
            stock_price.open = stock_data["open"]
            stock_price.previous_close = stock_data["previousClose"]
            stock_price.eps = stock_data["eps"]
            stock_price.pe = stock_data["pe"]
            stock_price.earnings_announcement = stock_data["earningsAnnouncement"]
            stock_price.shares_outstanding = stock_data["sharesOutstanding"]
            stock_price.timestamp = stock_data["timestamp"]

        db.commit()

        response.append(
            StockPriceResponse(
                id=stock_price.id,
                symbol=stock_price.symbol,
                name=stock_price.name,
                price=stock_price.price,
                changes_percentage=stock_price.changes_percentage,
                change=stock_price.change,
                day_low=stock_price.day_low,
                day_high=stock_price.day_high,
                year_high=stock_price.year_high,
                year_low=stock_price.year_low,
                market_cap=stock_price.market_cap,
                price_avg50=stock_price.price_avg50,
                price_avg200=stock_price.price_avg200,
                exchange=stock_price.exchange,
                volume=stock_price.volume,
                avg_volume=stock_price.avg_volume,
                open=stock_price.open,
                previous_close=stock_price.previous_close,
                eps=stock_price.eps,
                pe=stock_price.pe,
                earnings_announcement=stock_price.earnings_announcement,
                shares_outstanding=stock_price.shares_outstanding,
                timestamp=stock_price.timestamp,
            )
        )

    return f"Registros actualizados con exito"


@router.put("/{symbol}")
async def update_price_by_symbol(symbol: str, db: db_dependency):
    stock_data = get_stock_prices(symbol)
    stock_price = db.query(StockPrice).filter(StockPrice.symbol == symbol).first()

    if not stock_price:
        stock_price = StockPrice(
            symbol=stock_data["symbol"],
            price=stock_data["price"],
            name=stock_data["name"],
            changes_percentage=stock_data["changesPercentage"],
            change=stock_data["change"],
            day_low=stock_data["dayLow"],
            day_high=stock_data["dayHigh"],
            year_high=stock_data["yearHigh"],
            year_low=stock_data["yearLow"],
            market_cap=stock_data["marketCap"],
            price_avg50=stock_data["priceAvg50"],
            price_avg200=stock_data["priceAvg200"],
            exchange=stock_data["exchange"],
            volume=stock_data["volume"],
            avg_volume=stock_data["avgVolume"],
            open=stock_data["open"],
            previous_close=stock_data["previousClose"],
            eps=stock_data["eps"],
            pe=stock_data["pe"],
            earnings_announcement=stock_data["earningsAnnouncement"],
            shares_outstanding=stock_data["sharesOutstanding"],
            timestamp=stock_data["timestamp"]
        )
        db.add(stock_price)
        db.commit()

    else:
        stock_price.price = stock_data["price"]
        stock_price.changes_percentage = stock_data["changesPercentage"]
        stock_price.name = stock_data["name"]
        stock_price.change = stock_data["change"]
        stock_price.day_low = stock_data["dayLow"]
        stock_price.day_high = stock_data["dayHigh"]
        stock_price.year_high = stock_data["yearHigh"]
        stock_price.year_low = stock_data["yearLow"]
        stock_price.market_cap = stock_data["marketCap"]
        stock_price.price_avg50 = stock_data["priceAvg50"]
        stock_price.price_avg200 = stock_data["priceAvg200"]
        stock_price.exchange = stock_data["exchange"]
        stock_price.volume = stock_data["volume"]
        stock_price.avg_volume = stock_data["avgVolume"]
        stock_price.open = stock_data["open"]
        stock_price.previous_close = stock_data["previousClose"]
        stock_price.eps = stock_data["eps"]
        stock_price.pe = stock_data["pe"]
        stock_price.earnings_announcement = stock_data["earningsAnnouncement"]
        stock_price.shares_outstanding = stock_data["sharesOutstanding"]
        stock_price.timestamp = stock_data["timestamp"]

        db.commit()

    return f"Datos actualizados para el símbolo {symbol}"
