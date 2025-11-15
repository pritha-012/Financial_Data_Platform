"""
Quick setup with Alpha Vantage - fetches 3 stocks only
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')

from app.database import SessionLocal, init_db
from app.models import Company, StockData
from app.alphavantage_collector import AlphaVantageCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
if not api_key or api_key == 'YOUR_API_KEY_HERE':
    print("❌ Error: Please set ALPHA_VANTAGE_API_KEY in backend/.env file")
    print("\nGet free key: https://www.alphavantage.co/support/#api-key")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:4]}...{api_key[-4:]}")


collector = AlphaVantageCollector(api_key=api_key)
init_db()
db = SessionLocal()

# Fetch 3 US stocks (work better with Alpha Vantage)
test_stocks = ['AAPL', 'MSFT', 'GOOGL']

print("\n🚀 Fetching 3 stocks from Alpha Vantage (for testing)...\n")

for symbol in test_stocks:
    try:
        print(f"📊 Fetching {symbol}...")
        df, company_info, stats = collector.process_stock(symbol, 'compact')
        
        if df is not None and not df.empty:
          
            existing = db.query(Company).filter(Company.symbol == symbol).first()
            if not existing:
                company = Company(
                    symbol=symbol,
                    name=company_info['name'],
                    sector=company_info['sector'],
                    industry=company_info['industry'],
                    market_cap=company_info['market_cap']
                )
                db.add(company)
                db.commit()
            
            
            added = 0
            for _, row in df.iterrows():
                existing = db.query(StockData).filter(
                    StockData.symbol == symbol,
                    StockData.date == row['date']
                ).first()
                
                if not existing:
                    stock_data = StockData(
                        symbol=symbol,
                        date=row['date'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=int(row['volume']),
                        daily_return=float(row.get('daily_return', 0)),
                        ma7=float(row.get('ma7', 0)),
                        ma30=float(row.get('ma30', 0)),
                        volatility=float(row.get('volatility', 0))
                    )
                    db.add(stock_data)
                    added += 1
            
            db.commit()
            print(f"   ✅ Added {added} records for {symbol}\n")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")

db.close()
print("✅ Alpha Vantage test complete!")
print("💡 Now you have both real (Alpha Vantage) and mock data!")