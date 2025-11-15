"""
Data models and Pydantic schemas for API validation
"""

from sqlalchemy import Column, Integer, String, Float, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

Base = declarative_base()

# SQLAlchemy ORM Models
class Company(Base):
    """Company/Stock information table"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    
    def __repr__(self):
        return f"<Company {self.symbol}>"


class StockData(Base):
    """Historical stock price data table"""
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    daily_return = Column(Float)
    ma7 = Column(Float)  # 7-day moving average
    ma30 = Column(Float)  # 30-day moving average
    volatility = Column(Float)  # Daily volatility
    
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
    )
    
    def __repr__(self):
        return f"<StockData {self.symbol} {self.date}>"


# Pydantic Response Models
class CompanyResponse(BaseModel):
    """Company information response schema"""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    
    class Config:
        from_attributes = True


class StockDataResponse(BaseModel):
    """Single stock data point response schema"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: Optional[float] = None
    ma7: Optional[float] = None
    ma30: Optional[float] = None
    
    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    """Stock summary statistics response schema"""
    symbol: str
    current_price: float
    week52_high: float
    week52_low: float
    avg_close: float
    total_volume: int
    volatility: float
    daily_return: float
    trend: str  # "bullish", "bearish", "neutral"


class CompareResponse(BaseModel):
    """Stock comparison response schema"""
    symbol1: str
    symbol2: str
    correlation: float
    symbol1_return: float
    symbol2_return: float
    symbol1_volatility: float
    symbol2_volatility: float
    better_performer: str


class MoverResponse(BaseModel):
    """Top mover (gainer/loser) response schema"""
    symbol: str
    name: str
    current_price: float
    change_percent: float
    volume: int


class TopMoversResponse(BaseModel):
    """Top gainers and losers response schema"""
    gainers: List[MoverResponse]
    losers: List[MoverResponse]