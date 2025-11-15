"""
Generate realistic mock stock data for demo without internet
Run: python scripts/generate_mock_data.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.database import SessionLocal
from app.models import StockData
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_realistic_price_data(base_price, days=90):
    """Generate realistic stock price movements"""
    data = []
    current_price = base_price
    current_date = datetime.now().date() - timedelta(days=days)
    
    for i in range(days):
       
        daily_change = random.uniform(-0.03, 0.03)
        trend = random.uniform(-0.002, 0.005)
        
        
        open_price = current_price
        close_price = open_price * (1 + daily_change + trend)
        high_price = max(open_price, close_price) * random.uniform(1.005, 1.02)
        low_price = min(open_price, close_price) * random.uniform(0.98, 0.995)
        
        # Volume
        base_volume = random.randint(2000000, 8000000)
        volume = int(base_volume * (1 + abs(daily_change) * 10))
        
        # Metrics
        daily_return = ((close_price - open_price) / open_price) * 100
        ma7 = close_price * random.uniform(0.98, 1.02)
        ma30 = close_price * random.uniform(0.95, 1.05)
        volatility = abs(daily_return) * random.uniform(0.8, 1.5)
        
        data.append({
            'date': current_date,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'daily_return': round(daily_return, 4),
            'ma7': round(ma7, 2),
            'ma30': round(ma30, 2),
            'volatility': round(volatility, 4)
        })
        
        current_price = close_price
        current_date += timedelta(days=1)
    
    return data


def populate_mock_data():
    """Populate database with realistic mock data"""
    
    stocks = {
        'RELIANCE': 2850.0, 'TCS': 3600.0, 'HDFCBANK': 1650.0,
        'INFY': 1450.0, 'HINDUNILVR': 2380.0, 'ICICIBANK': 1050.0,
        'BHARTIARTL': 1580.0, 'ITC': 450.0, 'SBIN': 780.0,
        'LT': 3500.0, 'KOTAKBANK': 1780.0, 'WIPRO': 580.0,
        'AXISBANK': 1150.0, 'ASIANPAINT': 2900.0, 'MARUTI': 12500.0
    }
    
    db = SessionLocal()
    total_records = 0
    
    try:
        logger.info("🎲 Generating mock stock data...")
        logger.info("=" * 60)
        
        for symbol, base_price in stocks.items():
            logger.info(f"📊 Generating data for {symbol}...")
            
            price_data = generate_realistic_price_data(base_price, days=90)
            records_added = 0
            
            for data_point in price_data:
                existing = db.query(StockData).filter(
                    StockData.symbol == symbol,
                    StockData.date == data_point['date']
                ).first()
                
                if existing:
                    continue
                
                stock_data = StockData(
                    symbol=symbol,
                    date=data_point['date'],
                    open=data_point['open'],
                    high=data_point['high'],
                    low=data_point['low'],
                    close=data_point['close'],
                    volume=data_point['volume'],
                    daily_return=data_point['daily_return'],
                    ma7=data_point['ma7'],
                    ma30=data_point['ma30'],
                    volatility=data_point['volatility']
                )
                
                db.add(stock_data)
                records_added += 1
            
            db.commit()
            total_records += records_added
            logger.info(f"   ✅ Added {records_added} records for {symbol}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Mock Data Generation Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Total records added: {total_records}")
        logger.info(f"📈 Stock data points: {db.query(StockData).count()}")
        logger.info("\n💡 Start API server: cd backend && python run.py")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🎲 Mock Data Generator")
    print("=" * 60)
    print("Generating realistic stock data for demo")
    print("=" * 60 + "\n")
    populate_mock_data()