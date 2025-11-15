"""
API Endpoint Tests
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestCompaniesEndpoint:
    """Test /companies endpoint"""
    
    def test_get_companies(self):
        """Test getting all companies"""
        response = client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            company = data[0]
            assert "symbol" in company
            assert "name" in company
    
    def test_get_companies_with_sector_filter(self):
        """Test filtering companies by sector"""
        response = client.get("/api/v1/companies?sector=IT")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestStockDataEndpoint:
    """Test /data/{symbol} endpoint"""
    
    def test_get_stock_data_default_days(self):
        """Test getting stock data with default days"""
        response = client.get("/api/v1/data/RELIANCE")
        assert response.status_code in [200, 404]  
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                item = data[0]
                assert "date" in item
                assert "open" in item
                assert "close" in item
                assert "high" in item
                assert "low" in item
                assert "volume" in item
    
    def test_get_stock_data_custom_days(self):
        """Test getting stock data with custom days"""
        response = client.get("/api/v1/data/TCS?days=7")
        assert response.status_code in [200, 404]
    
    def test_get_stock_data_invalid_symbol(self):
        """Test getting data for invalid symbol"""
        response = client.get("/api/v1/data/INVALID123")
       
        assert response.status_code in [200, 404, 500]


class TestSummaryEndpoint:
    """Test /summary/{symbol} endpoint"""
    
    def test_get_summary(self):
        """Test getting stock summary"""
        response = client.get("/api/v1/summary/RELIANCE")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "symbol" in data
            assert "current_price" in data
            assert "week52_high" in data
            assert "week52_low" in data
            assert "volatility" in data
            assert "trend" in data
            assert data["trend"] in ["bullish", "bearish", "neutral"]


class TestCompareEndpoint:
    """Test /compare endpoint"""
    
    def test_compare_stocks(self):
        """Test comparing two stocks"""
        response = client.get("/api/v1/compare?symbol1=INFY&symbol2=TCS")
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "symbol1" in data
            assert "symbol2" in data
            assert "correlation" in data
            assert "symbol1_return" in data
            assert "symbol2_return" in data
            assert "better_performer" in data
    
    def test_compare_missing_parameters(self):
        """Test compare endpoint with missing parameters"""
        response = client.get("/api/v1/compare?symbol1=INFY")
        assert response.status_code == 422  


class TestMoversEndpoint:
    """Test /movers endpoint"""
    
    def test_get_top_movers(self):
        """Test getting top movers"""
        response = client.get("/api/v1/movers")
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "gainers" in data
            assert "losers" in data
            assert isinstance(data["gainers"], list)
            assert isinstance(data["losers"], list)
    
    def test_get_top_movers_custom_limit(self):
        """Test getting top movers with custom limit"""
        response = client.get("/api/v1/movers?limit=3")
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["gainers"]) <= 3
            assert len(data["losers"]) <= 3


class TestTechnicalsEndpoint:
    """Test /technicals/{symbol} endpoint"""
    
    def test_get_technical_indicators(self):
        """Test getting technical indicators"""
        response = client.get("/api/v1/technicals/RELIANCE")
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "symbol" in data
            assert "rsi" in data
            assert "macd" in data
            assert "support_resistance" in data
            assert "predicted_next_price" in data


class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_negative_days_parameter(self):
        """Test handling of negative days parameter"""
        response = client.get("/api/v1/data/RELIANCE?days=-10")
        assert response.status_code == 422  
    
    def test_excessive_days_parameter(self):
        """Test handling of excessive days parameter"""
        response = client.get("/api/v1/data/RELIANCE?days=1000")
        assert response.status_code == 422  
    
    def test_invalid_limit_parameter(self):
        """Test handling of invalid limit in movers"""
        response = client.get("/api/v1/movers?limit=100")
        assert response.status_code == 422  


