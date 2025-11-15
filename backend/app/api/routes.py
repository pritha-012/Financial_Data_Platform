"""
API Routes for Financial Data Platform
Implements all REST endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np

from app.database import get_db
from app.models import Company, StockData
from app.models import (
    CompanyResponse, StockDataResponse, SummaryResponse,
    CompareResponse, TopMoversResponse, MoverResponse
)
from app.data_collector import data_collector


try:
    from app.data_service import data_service
    USE_DATA_SERVICE = True
except ImportError:
    USE_DATA_SERVICE = False
    logging.warning("data_service not available, using database only")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/companies", response_model=List[CompanyResponse])
async def get_companies(
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all available companies
    
    Query Parameters:
    - sector: Filter by sector (optional)
    """
    try:
        query = db.query(Company)
        
        if sector:
            query = query.filter(Company.sector == sector)
        
        companies = query.all()
        
        
        if not companies:
            default_companies = []
            for symbol in data_collector.INDIAN_STOCKS[:10]:
                company_info = data_collector.get_company_info(symbol)
                default_companies.append(CompanyResponse(**company_info))
            return default_companies
        
        return companies
    
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching companies")


@router.get("/data/{symbol}", response_model=List[StockDataResponse])
async def get_stock_data(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get historical stock data for a symbol
    
    Path Parameters:
    - symbol: Stock symbol (e.g., RELIANCE, TCS)
    
    Query Parameters:
    - days: Number of days of historical data (1-365, default: 30)
    """
    try:
       
        if USE_DATA_SERVICE:
            df, source = data_service.get_stock_data(symbol, days)
            
            if df is not None and not df.empty:
               
                response_data = []
                for _, row in df.iterrows():
                    response_data.append(StockDataResponse(
                        date=str(row['date']),
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=int(row['volume']),
                        daily_return=float(row.get('daily_return', 0)),
                        ma7=float(row.get('ma7', 0)),
                        ma30=float(row.get('ma30', 0))
                    ))
                
                logger.info(f"Served {len(response_data)} records from {source}")
                return response_data
        
       
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= cutoff_date
        ).order_by(StockData.date.desc()).all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        
        response_data = []
        for record in stock_data:
            response_data.append(StockDataResponse(
                date=str(record.date), 
                open=float(record.open),
                high=float(record.high),
                low=float(record.low),
                close=float(record.close),
                volume=int(record.volume),
                daily_return=float(record.daily_return) if record.daily_return else 0.0,
                ma7=float(record.ma7) if record.ma7 else 0.0,
                ma30=float(record.ma30) if record.ma30 else 0.0
            ))
        
        logger.info(f"Served {len(response_data)} records from database")
        return response_data[:days]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/summary/{symbol}", response_model=SummaryResponse)
async def get_stock_summary(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive summary statistics for a stock
    
    Path Parameters:
    - symbol: Stock symbol (e.g., RELIANCE, TCS)
    
    Returns:
    - 52-week high/low
    - Average close price
    - Current price
    - Total volume
    - Volatility
    - Daily return
    - Trend (bullish/bearish/neutral)
    """
    try:
      
        one_year_ago = datetime.now().date() - timedelta(days=365)
        
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= one_year_ago
        ).order_by(StockData.date).all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
       
        closes = [d.close for d in stock_data]
        highs = [d.high for d in stock_data]
        lows = [d.low for d in stock_data]
        returns = [d.daily_return for d in stock_data if d.daily_return]
        
       
        if len(closes) > 20:
            recent_avg = sum(closes[-20:]) / 20
            older_avg = sum(closes[:20]) / 20
            if recent_avg > older_avg * 1.05:
                trend = "bullish"
            elif recent_avg < older_avg * 0.95:
                trend = "bearish"
            else:
                trend = "neutral"
        else:
            trend = "neutral"
        
        summary = SummaryResponse(
            symbol=symbol,
            current_price=float(closes[-1]),
            week52_high=float(max(highs)),
            week52_low=float(min(lows)),
            avg_close=float(sum(closes) / len(closes)),
            total_volume=int(sum([d.volume for d in stock_data])),
            volatility=float(np.std(returns)) if returns else 0.0,
            daily_return=float(returns[-1]) if returns else 0.0,
            trend=trend
        )
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")


@router.get("/compare", response_model=CompareResponse)
async def compare_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    days: int = Query(default=90, ge=30, le=365),
    db: Session = Depends(get_db)
):
    """
    Compare performance of two stocks
    
    Query Parameters:
    - symbol1: First stock symbol
    - symbol2: Second stock symbol
    - days: Number of days for comparison (30-365, default: 90)
    
    Returns:
    - Correlation between stocks
    - Individual returns and volatility
    - Better performer
    """
    try:
       
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
       
        data1 = db.query(StockData).filter(
            StockData.symbol == symbol1,
            StockData.date >= cutoff_date
        ).order_by(StockData.date).all()
        
        
        data2 = db.query(StockData).filter(
            StockData.symbol == symbol2,
            StockData.date >= cutoff_date
        ).order_by(StockData.date).all()
        
        if not data1 or not data2:
            raise HTTPException(status_code=404, detail="Data not found for one or both symbols")
        
        
        symbol1_return = ((data1[-1].close - data1[0].close) / data1[0].close * 100)
        symbol2_return = ((data2[-1].close - data2[0].close) / data2[0].close * 100)
        
        
        returns1 = [d.daily_return for d in data1 if d.daily_return]
        returns2 = [d.daily_return for d in data2 if d.daily_return]
        
        symbol1_volatility = float(np.std(returns1)) if returns1 else 0.0
        symbol2_volatility = float(np.std(returns2)) if returns2 else 0.0
        
        
        if len(returns1) == len(returns2) and len(returns1) > 0:
            correlation = float(np.corrcoef(returns1, returns2)[0, 1])
        else:
            correlation = 0.0
        
        
        better_performer = symbol1 if symbol1_return > symbol2_return else symbol2
        
        comparison = CompareResponse(
            symbol1=symbol1,
            symbol2=symbol2,
            correlation=round(correlation, 4),
            symbol1_return=round(symbol1_return, 2),
            symbol2_return=round(symbol2_return, 2),
            symbol1_volatility=round(symbol1_volatility, 2),
            symbol2_volatility=round(symbol2_volatility, 2),
            better_performer=better_performer
        )
        
        return comparison
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing stocks: {str(e)}")


@router.get("/movers", response_model=TopMoversResponse)
async def get_top_movers(
    limit: int = Query(default=5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get top gainers and losers for the day
    
    Query Parameters:
    - limit: Number of top gainers/losers to return (1-10, default: 5)
    """
    try:
        movers_data = []
        
       
        companies = db.query(Company).all()
        
        for company in companies[:15]:  
            try:
               
                recent_data = db.query(StockData).filter(
                    StockData.symbol == company.symbol
                ).order_by(StockData.date.desc()).limit(2).all()
                
                if len(recent_data) >= 2:
                    latest = recent_data[0]
                    previous = recent_data[1]
                    
                    change_percent = ((latest.close - previous.close) / previous.close * 100)
                    
                    movers_data.append(MoverResponse(
                        symbol=company.symbol,
                        name=company.name,
                        current_price=float(latest.close),
                        change_percent=round(change_percent, 2),
                        volume=int(latest.volume)
                    ))
            except Exception as e:
                logger.warning(f"Error processing {company.symbol}: {str(e)}")
                continue
        
       
        movers_data.sort(key=lambda x: x.change_percent, reverse=True)
        
       
        gainers = movers_data[:limit]
        losers = movers_data[-limit:][::-1]
        
        return TopMoversResponse(gainers=gainers, losers=losers)
    
    except Exception as e:
        logger.error(f"Error fetching top movers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching top movers")


@router.get("/technicals/{symbol}")
async def get_technical_indicators(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get technical indicators for a stock
    
    Path Parameters:
    - symbol: Stock symbol
    
    Returns:
    - RSI
    - MACD
    - Support/Resistance
    - Price Prediction
    """
    try:
       
        six_months_ago = datetime.now().date() - timedelta(days=180)
        
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= six_months_ago
        ).order_by(StockData.date).all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        prices = [d.close for d in stock_data]
        highs = [d.high for d in stock_data]
        lows = [d.low for d in stock_data]
        returns = [d.daily_return for d in stock_data if d.daily_return]
        
        
        if len(returns) > 14:
            gains = [r for r in returns[-14:] if r > 0]
            losses = [abs(r) for r in returns[-14:] if r < 0]
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50.0
        
        
        macd_value = 0.0
        if len(prices) > 26:
            ema12 = sum(prices[-12:]) / 12
            ema26 = sum(prices[-26:]) / 26
            macd_value = ema12 - ema26
        
        
        support = float(min(lows[-20:]) if len(lows) >= 20 else min(lows))
        resistance = float(max(highs[-20:]) if len(highs) >= 20 else max(highs))
        
       
        if len(prices) > 10:
            recent_trend = (prices[-1] - prices[-10]) / 10
            prediction = prices[-1] + recent_trend
        else:
            prediction = prices[-1]
        
        return {
            "symbol": symbol,
            "rsi": round(rsi, 2),
            "macd": {
                "macd_line": round(macd_value, 2),
                "signal_line": 0.0,
                "histogram": 0.0
            },
            "support_resistance": {
                "support": round(support, 2),
                "resistance": round(resistance, 2)
            },
            "predicted_next_price": round(prediction, 2),
            "current_price": round(prices[-1], 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating technicals for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating technicals: {str(e)}")