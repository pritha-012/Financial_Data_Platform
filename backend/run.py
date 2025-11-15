"""
Development server runner with automatic setup
"""

import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_database():
    """Initialize database if it doesn't exist"""
    from app.database import init_db, DATA_DIR
    
    db_path = DATA_DIR / "stocks.db"
    
    if not db_path.exists():
        print("🔧 Initializing database...")
        init_db()
        print("✅ Database initialized!")
    else:
        print("✅ Database found!")

def main():
    """Run the development server"""
    print("🚀 Starting FinData Platform API Server...")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    print("\n📊 Server Configuration:")
    print(f"   Host: 0.0.0.0")
    print(f"   Port: 8000")
    print(f"   Docs: http://localhost:8000/api/docs")
    print(f"   ReDoc: http://localhost:8000/api/redoc")
    print("=" * 50)
    print("\n💡 Press CTRL+C to stop the server\n")
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()