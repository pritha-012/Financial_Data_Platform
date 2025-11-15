"""
Alpha Vantage Data Collector
Fetches stock data from Alpha Vantage API
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import time
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


class AlphaVantageCollector:
    """Handles data collection from Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    
    API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_API_KEY_HERE')
    
   
    STOCK_SYMBOLS = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'WMT': 'Walmart Inc.'
    }
    
    # Indian stock symbols (BSE symbols - may have limited data)
    INDIAN_STOCKS = {
        'RELIANCE.BSE': 'RELIANCE',
        'TCS.BSE': 'TCS',
        'HDFCBANK.BSE': 'HDFCBANK',
        'INFY.BSE': 'INFY',
        'HINDUNILVR.BSE': 'HINDUNILVR',
        'ICICIBANK.BSE': 'ICICIBANK',
        'BHARTIARTL.BSE': 'BHARTIARTL',
        'ITC.BSE': 'ITC',
        'SBIN.BSE': 'SBIN',
        'LT.BSE': 'LT'
    }
    
    def __init__(self, api_key: str = None):
        """Initialize with API key"""
        self.api_key = api_key or self.API_KEY
        
        # Check if API key is properly configured
        if self.api_key == "YOUR_API_KEY_HERE" or not self.api_key:
            logger.warning("⚠️  Alpha Vantage API key not configured!")
            logger.warning("Set ALPHA_VANTAGE_API_KEY in backend/.env file")
            logger.warning("Get free key: https://www.alphavantage.co/support/#api-key")
    
    def fetch_daily_data(self, symbol: str, outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """
        Fetch daily time series data
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'RELIANCE.BSE')
            outputsize: 'compact' (100 days) or 'full' (20+ years)
        
        Returns:
            DataFrame with stock data or None if failed
        """
        try:
            logger.info(f"📊 Fetching data for {symbol} from Alpha Vantage...")
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                logger.error(f"❌ API Error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"⚠️  API Limit: {data['Note']}")
                return None
            
            if 'Time Series (Daily)' not in data:
                logger.error(f"❌ No data found for {symbol}")
                logger.debug(f"Response keys: {data.keys()}")
                return None
            
            # Parse data
            time_series = data['Time Series (Daily)']
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'date'}, inplace=True)
            df['date'] = df['date'].dt.date
            
            logger.info(f"✅ Fetched {len(df)} records for {symbol}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error fetching {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {str(e)}")
            return None
    
    def get_company_info(self, symbol: str) -> Dict:
        """
        Get company overview/information
        """
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            data = response.json()
            
            if not data or 'Symbol' not in data:
                # Return basic info if API call fails
                clean_symbol = symbol.replace('.BSE', '').replace('.NSE', '')
                name = self.STOCK_SYMBOLS.get(clean_symbol, f"{clean_symbol} Corporation")
                return {
                    'symbol': clean_symbol,
                    'name': name,
                    'sector': 'Unknown',
                    'industry': 'Unknown',
                    'market_cap': 0
                }
            
            return {
                'symbol': data.get('Symbol', symbol),
                'name': data.get('Name', symbol),
                'sector': data.get('Sector', 'Unknown'),
                'industry': data.get('Industry', 'Unknown'),
                'market_cap': float(data.get('MarketCapitalization', 0))
            }
            
        except Exception as e:
            logger.error(f"Error fetching company info: {str(e)}")
            clean_symbol = symbol.replace('.BSE', '').replace('.NSE', '')
            name = self.STOCK_SYMBOLS.get(clean_symbol, f"{clean_symbol} Corporation")
            return {
                'symbol': clean_symbol,
                'name': name,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0
            }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        df = df.copy()
        
        # Handle missing values
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        df.dropna(inplace=True)
        
        # Remove duplicates
        df.drop_duplicates(subset=['date'], keep='last', inplace=True)
        df.sort_values('date', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators and metrics"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Daily Return
        df['daily_return'] = ((df['close'] - df['open']) / df['open'] * 100).round(4)
        
        # Moving Averages
        df['ma7'] = df['close'].rolling(window=7, min_periods=1).mean().round(2)
        df['ma30'] = df['close'].rolling(window=30, min_periods=1).mean().round(2)
        
        # Volatility
        df['volatility'] = df['daily_return'].rolling(window=20, min_periods=1).std().round(4)
        
        # Momentum Score
        df['momentum_score'] = ((df['close'] - df['ma30']) / df['ma30'] * 100).round(2)
        
        # Volume Trend
        avg_volume = df['volume'].rolling(window=20, min_periods=1).mean()
        df['volume_trend'] = ((df['volume'] - avg_volume) / avg_volume * 100).round(2)
        
        return df
    
    def process_stock(self, symbol: str, outputsize: str = 'compact') -> tuple:
        """
        Complete pipeline: fetch, clean, calculate metrics
        
        Args:
            symbol: Stock symbol
            outputsize: 'compact' or 'full'
        
        Returns:
            Tuple of (dataframe, company_info, stats)
        """
        # Fetch data
        df = self.fetch_daily_data(symbol, outputsize)
        if df is None or df.empty:
            return None, None, None
        
        # Clean data
        df = self.clean_data(df)
        if df.empty:
            return None, None, None
        
        # Calculate metrics
        df = self.calculate_metrics(df)
        
        # Get company info
        company_info = self.get_company_info(symbol)
        
        # Calculate statistics
        stats = {
            'week52_high': float(df['high'].max()),
            'week52_low': float(df['low'].min()),
            'avg_close': float(df['close'].mean()),
            'current_price': float(df.iloc[-1]['close']),
            'total_volume': int(df['volume'].sum()),
            'avg_daily_return': float(df['daily_return'].mean()),
            'volatility': float(df['daily_return'].std())
        }
        
        
        time.sleep(12)  
        
        return df, company_info, stats



alphavantage_collector = AlphaVantageCollector()