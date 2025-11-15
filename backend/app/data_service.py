"""
Smart Data Service - Uses Alpha Vantage with database fallback
"""

import os
from typing import Optional, Tuple
import pandas as pd
import logging

from app.alphavantage_collector import alphavantage_collector
from app.data_collector import data_collector
from app.database import SessionLocal
from app.models import StockData
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataService:
    """Intelligent data fetching with multiple sources"""
    
    def __init__(self):
        self.use_alpha_vantage = os.getenv('ALPHA_VANTAGE_API_KEY') not in [None, '', 'YOUR_API_KEY_HERE']
        logger.info(f"Alpha Vantage enabled: {self.use_alpha_vantage}")
    
    def get_stock_data(self, symbol: str, days: int = 30) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Get stock data from best available source
        
        Returns:
            Tuple of (dataframe, source_name)
            source_name: 'alpha_vantage', 'database', 'yfinance', or None
        """
        
        if self.use_alpha_vantage:
            logger.info(f"Attempting Alpha Vantage for {symbol}")
            try:
                df, _, _ = alphavantage_collector.process_stock(symbol, 'compact')
                if df is not None and not df.empty:
                    logger.info(f"✅ Got data from Alpha Vantage for {symbol}")
                    return df.tail(days), 'alpha_vantage'
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for {symbol}: {str(e)}")
        
       
        logger.info(f"Attempting database for {symbol}")
        try:
            db = SessionLocal()
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            data = db.query(StockData).filter(
                StockData.symbol == symbol,
                StockData.date >= cutoff_date
            ).order_by(StockData.date).all()
            
            db.close()
            
            if data:
                
                df = pd.DataFrame([{
                    'date': d.date,
                    'open': d.open,
                    'high': d.high,
                    'low': d.low,
                    'close': d.close,
                    'volume': d.volume,
                    'daily_return': d.daily_return,
                    'ma7': d.ma7,
                    'ma30': d.ma30
                } for d in data])
                
                logger.info(f"✅ Got data from database for {symbol}")
                return df, 'database'
        except Exception as e:
            logger.warning(f"Database failed for {symbol}: {str(e)}")
        
        
        logger.info(f"Attempting yfinance for {symbol}")
        try:
            full_symbol = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            df, _, _ = data_collector.process_stock(full_symbol, f"{days}d")
            if df is not None and not df.empty:
                logger.info(f"✅ Got data from yfinance for {symbol}")
                return df, 'yfinance'
        except Exception as e:
            logger.warning(f"yfinance failed for {symbol}: {str(e)}")
        
        logger.error(f"❌ All data sources failed for {symbol}")
        return None, None



data_service = DataService()