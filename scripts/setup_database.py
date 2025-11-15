"""
Database setup script
Initializes database with sample stock data
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.database import SessionLocal, init_db
from app.models import Company, StockData
from app.data_collector import data_collector
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_companies(db):
    """Add companies to database"""
    logger.info("📊 Adding companies to database...")
    
    companies_added = 0
    
    for symbol in data_collector.INDIAN_STOCKS:
        try:
         
            existing = db.query(Company).filter(Company.symbol == symbol.replace('.NS', '')).first()
            if existing:
                logger.info(f"   ⏭️  {symbol} already exists, skipping...")
                continue
            
          
            company_info = data_collector.get_company_info(symbol)
            
         
            company = Company(
                symbol=company_info['symbol'],
                name=company_info['name'],
                sector=company_info['sector'],
                industry=company_info['industry'],
                market_cap=company_info['market_cap']
            )
            
            db.add(company)
            companies_added += 1
            logger.info(f"   ✅ Added {company_info['symbol']} - {company_info['name']}")
            
        except Exception as e:
            logger.error(f"   ❌ Error adding {symbol}: {str(e)}")
            continue
    
    db.commit()
    logger.info(f"✅ Added {companies_added} companies!\n")


def populate_stock_data(db, symbol, days=90):
    """Add historical stock data for a symbol"""
    try:
        logger.info(f"📈 Fetching {days} days of data for {symbol}...")
        
  
        df, company_info, stats = data_collector.process_stock(symbol, f"{days}d")
        
        if df is None or df.empty:
            logger.warning(f"   ⚠️  No data available for {symbol}")
            return 0
        
        records_added = 0
        symbol_clean = symbol.replace('.NS', '').replace('.BO', '')
        
        for _, row in df.iterrows():
      
            existing = db.query(StockData).filter(
                StockData.symbol == symbol_clean,
                StockData.date == row['date']
            ).first()
            
            if existing:
                continue
            
          
            stock_data = StockData(
                symbol=symbol_clean,
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
            records_added += 1
        
        db.commit()
        logger.info(f"   ✅ Added {records_added} records for {symbol}\n")
        return records_added
        
    except Exception as e:
        logger.error(f"   ❌ Error processing {symbol}: {str(e)}\n")
        db.rollback()
        return 0


def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 FinData Platform - Database Setup")
    print("=" * 60)
    print()
    
   
    logger.info("🔧 Initializing database schema...")
    init_db()
    logger.info("✅ Database schema ready!\n")
    
   
    db = SessionLocal()
    
    try:
     
        populate_companies(db)
        
    
        logger.info("📊 Fetching historical stock data...")
        logger.info("(This may take a few minutes...)\n")
        
        total_records = 0
        for symbol in data_collector.INDIAN_STOCKS[:5]:  
            records = populate_stock_data(db, symbol, days=90)
            total_records += records
        
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print(f"📊 Total records added: {total_records}")
        print(f"🏢 Companies in database: {db.query(Company).count()}")
        print(f"📈 Stock data points: {db.query(StockData).count()}")
        print("\n💡 You can now start the API server with: python run.py")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()