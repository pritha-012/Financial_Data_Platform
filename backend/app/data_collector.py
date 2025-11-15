"""
Data collection and cleaning module
Fetches stock data from yfinance and processes it
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """Handles data collection and cleaning operations"""
    
    
    INDIAN_STOCKS = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LT.NS",
        "KOTAKBANK.NS", "WIPRO.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS"
    ]
    
    def __init__(self):
        self.data_cache = {}
    
    def fetch_stock_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from yfinance
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with stock data or None if failed
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare stock data
        
        Steps:
        1. Handle missing values
        2. Remove duplicates
        3. Convert date format
        4. Handle incorrect data types
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
       
        df = df.copy()
        
      
        df.reset_index(inplace=True)
        
      
        df.columns = df.columns.str.lower()
        
      
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        
      
        df.dropna(inplace=True)
        
        # Remove duplicates based on date
        df.drop_duplicates(subset=['date'], keep='last', inplace=True)
        
        # Convert date to proper format
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Sort by date
        df.sort_values('date', inplace=True)
        
        # Reset index
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate custom metrics and technical indicators
        
        Metrics calculated:
        1. Daily Return = (Close - Open) / Open * 100
        2. 7-day Moving Average
        3. 30-day Moving Average
        4. Daily Volatility (std of returns)
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 1. Daily Return
        df['daily_return'] = ((df['close'] - df['open']) / df['open'] * 100).round(4)
        
        # 2. 7-day Moving Average
        df['ma7'] = df['close'].rolling(window=7, min_periods=1).mean().round(2)
        
        # 3. 30-day Moving Average
        df['ma30'] = df['close'].rolling(window=30, min_periods=1).mean().round(2)
        
        # 4. Daily Volatility (using rolling standard deviation)
        df['volatility'] = df['daily_return'].rolling(window=20, min_periods=1).std().round(4)
        
        # 5. Custom: Momentum Score (price relative to 30-day MA)
        df['momentum_score'] = ((df['close'] - df['ma30']) / df['ma30'] * 100).round(2)
        
        # 6. Custom: Volume Trend (relative to 20-day average)
        avg_volume = df['volume'].rolling(window=20, min_periods=1).mean()
        df['volume_trend'] = ((df['volume'] - avg_volume) / avg_volume * 100).round(2)
        
        return df
    
    def get_52_week_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate 52-week high, low, and other statistics"""
        if df.empty:
            return {}
        
        # Get last 52 weeks of data
        one_year_ago = datetime.now().date() - timedelta(days=365)
        df_year = df[pd.to_datetime(df['date']) >= pd.to_datetime(one_year_ago)]
        
        if df_year.empty:
            df_year = df
        
        stats = {
            'week52_high': float(df_year['high'].max()),
            'week52_low': float(df_year['low'].min()),
            'avg_close': float(df_year['close'].mean()),
            'current_price': float(df.iloc[-1]['close']),
            'total_volume': int(df_year['volume'].sum()),
            'avg_daily_return': float(df_year['daily_return'].mean()),
            'volatility': float(df_year['daily_return'].std())
        }
        
        return stats
    
    def calculate_correlation(
        self, 
        df1: pd.DataFrame, 
        df2: pd.DataFrame
    ) -> float:
        """
        Calculate correlation between two stocks' daily returns
        """
        if df1.empty or df2.empty:
            return 0.0
        
        # Merge dataframes on date
        merged = pd.merge(
            df1[['date', 'daily_return']],
            df2[['date', 'daily_return']],
            on='date',
            suffixes=('_1', '_2')
        )
        
        if merged.empty:
            return 0.0
        
        correlation = merged['daily_return_1'].corr(merged['daily_return_2'])
        return round(correlation, 4)
    
    def get_company_info(self, symbol: str) -> Dict:
        """Fetch company information from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return {
                'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0
            }
    
    def process_stock(self, symbol: str, period: str = "1y") -> tuple:
        """
        Complete pipeline: fetch, clean, calculate metrics
        
        Returns:
            Tuple of (cleaned_df, company_info, stats)
        """
        # Add .NS suffix if not present (for NSE stocks)
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        # Fetch raw data
        raw_df = self.fetch_stock_data(symbol, period)
        if raw_df is None or raw_df.empty:
            return None, None, None
        
        # Clean data
        clean_df = self.clean_data(raw_df)
        if clean_df.empty:
            return None, None, None
        
        # Calculate metrics
        processed_df = self.calculate_metrics(clean_df)
        
        # Get company info
        company_info = self.get_company_info(symbol)
        
        # Calculate statistics
        stats = self.get_52_week_stats(processed_df)
        
        return processed_df, company_info, stats


# Create singleton instance
data_collector = DataCollector()