from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, UniqueConstraint
from database import Base


class Instruments(Base):
    __tablename__ = 'instruments'

    id = Column(Integer, primary_key=True, index=True)
    cedear_symbol = Column(String)
    foreign_market = Column(String)
    foreign_symbol = Column(String)
    cedear_ratio = Column(Float)
    foreign_ratio = Column(Float)


class StockPrice(Base):
    __tablename__ = 'stock_prices'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    price = Column(Float)
    changes_percentage = Column(Float)
    change = Column(Float)
    day_low = Column(Float)
    day_high = Column(Float)
    year_low = Column(Float)
    year_high = Column(Float)
    market_cap = Column(Float)
    price_avg50 = Column(Float)
    price_avg200 = Column(Float)
    exchange = Column(String)
    volume = Column(Integer)
    avg_volume = Column(Integer)
    open = Column(Float)
    previous_close = Column(Float)
    eps = Column(Float)
    pe = Column(Float)
    earnings_announcement = Column(DateTime)
    shares_outstanding = Column(Float)
    timestamp = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint('symbol', 'timestamp'),
    )


class CompanyRating(Base):
    __tablename__ = 'company_rating'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, unique=True)
    rating_score = Column(Float)
    rating_rating = Column(String)
    rating_recommendation = Column(String)
