# 📊 FinData Platform - Financial Data Analysis Dashboard
A comprehensive mini financial data platform for real-time stock market analysis, visualization, and technical insights.

**Tech Stack:** Python FastAPI + Vanilla JavaScript + SQLite + Chart.js

**Features**

**Data Collection & Processing**
- ✅ Multi-source data architecture (Alpha Vantage + yfinance + Mock data)
- ✅ Automated data cleaning and transformation with Pandas
- ✅ Missing value handling and format correction
- ✅ Real-time and historical data support

**Backend REST API (FastAPI)**
- ✅ 6 RESTful endpoints with auto-generated Swagger documentation
- ✅ `/companies` - Get all available companies with filtering
- ✅ `/data/{symbol}` - Fetch historical stock data (configurable timeframes)
- ✅ `/summary/{symbol}` - Get 52-week statistics and volatility metrics
- ✅ `/compare` - Compare two stocks with correlation analysis
- ✅ `/movers` - Get top gainers and losers
- ✅ `/technicals/{symbol}` - Technical indicators (RSI, MACD, Support/Resistance)

**Interactive Visualization Dashboard**
- ✅ Real-time Chart.js price charts with zoom and hover details
- ✅ Moving averages overlay (MA7, MA30)
- ✅ Stock comparison with dual-line charts
- ✅ Top gainers/losers sidebar with live updates
- ✅ Technical indicators panel (RSI, MACD, trend detection)
- ✅ Responsive design (mobile, tablet, desktop)

**Custom Analytics & Insights** 
- ✅ **Volatility Scoring** - Risk classification (Low/Medium/High/Very High)
- ✅ **Correlation Analysis** - Statistical relationship between stocks
- ✅ **Trend Detection** - Automated bullish/bearish/neutral classification using linear regression
- ✅ **Momentum Score** - Custom metric: (Price - MA30) / MA30 × 100
- ✅ **Price Prediction** - Simple linear extrapolation for educational purposes
- ✅ **Volume Analysis** - Relative volume trends vs 20-day average

**Quick Start**

 **Prerequisites**
- Python 3.11 
- pip package manager
- Internet connection (for initial setup)

**Installation**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/financial-data-platform.git
cd financial-data-platform

# 2. Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Initialize database with mock data
cd ..
python scripts/generate_mock_data.py

# 5. Start backend server
cd backend
python run.py
```

**Backend will be available at:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/api/docs`

```bash
# 6. Start frontend (NEW TERMINAL - keep backend running)
cd frontend
python -m http.server 3000
```

**Frontend will be available at:** `http://localhost:3000`


**Data Collection Methods**

### **Method 1: Alpha Vantage API**  (Primary)

Professional financial data API with real-time stock prices.

```bash
# 1. Get FREE API key from: https://www.alphavantage.co/support/#api-key

# 2. Create .env file
cd backend
echo "ALPHA_VANTAGE_API_KEY=your_api_key_here" > .env

# 3. Fetch data (3-5 stocks due to free tier limits)
cd ..
python scripts/setup_with_alphavantage.py
```

**Features:**
- Real-time market data
- Company fundamentals
- 100+ data points per stock
- Professional-grade accuracy

**Limitations:**
- Free tier: 25 calls/day, 5 calls/minute
- Best for US stocks (AAPL, MSFT, GOOGL, etc.)


### **Method 2: yfinance (Open Source)** (Alternative)

Open-source library for Yahoo Finance data.

```bash
python scripts/setup_database.py
```

**Features:**
- Free and unlimited
- NSE/BSE stock support (RELIANCE.NS, TCS.NS)
- Historical data (20+ years)
- No API key required

**Note:** Currently experiencing API restrictions from Yahoo Finance. Use as fallback or for development.


### **Method 3: Mock Data Generator** 🎲 (Demo/Testing)

Generates realistic synthetic stock data for offline demos.

```bash
python scripts/generate_mock_data.py
```

**Features:**
- Works 100% offline
- Instant generation (15 stocks × 90 days in seconds)
- Realistic price movements and volatility
- Perfect for demos, testing, and presentations

**Use Cases:**
- Offline development
- Demos without API dependencies
- Testing data pipeline
- Understanding data structures


## 🔄 **Smart Data Service**

The platform uses an intelligent data routing system:

```python
Priority 1: Check Database Cache (fastest)
    ↓ If not found or stale
Priority 2: Try Alpha Vantage (if API key configured)
    ↓ If fails or rate limited
Priority 3: Try yfinance (fallback)
    ↓ If all fail
Return: 404 with helpful error message
```

**Benefits:**
- ✅ 100% uptime (multiple fallbacks)
- ✅ Fast response times (caching)
- ✅ Works online AND offline
- ✅ No single point of failure


## **Data Cleaning & Transformation**

All data sources go through rigorous cleaning:

### **1. Missing Value Handling**
```python
# Forward fill (use previous value)
df.ffill(inplace=True)

# Backward fill (use next value)
df.bfill(inplace=True)

# Remove remaining NaN
df.dropna(inplace=True)
```

### **2. Duplicate Removal**
```python
# Keep latest entry for duplicate dates
df.drop_duplicates(subset=['date'], keep='last', inplace=True)
```

### **3. Date Formatting**
```python
# Standardize date format
df['date'] = pd.to_datetime(df['date']).dt.date
```

### **4. Data Type Validation**
```python
# Ensure numeric columns are float/int
for col in ['open', 'high', 'low', 'close']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
```

---

## 📈 **Calculated Metrics**

### **Required Metrics** ✅

#### **1. Daily Return**
```python
daily_return = (CLOSE - OPEN) / OPEN × 100
```
*Measures daily price change percentage*

#### **2. 7-Day Moving Average (MA7)**
```python
ma7 = close.rolling(window=7).mean()
```
*Short-term trend indicator*

#### **3. 30-Day Moving Average (MA30)**
```python
ma30 = close.rolling(window=30).mean()
```
*Medium-term trend indicator*

#### **4. 52-Week High/Low**
```python
week52_high = max(high[-365:])
week52_low = min(low[-365:])
```
*Annual price range*

---

### **Custom Metrics** (Creative Analysis)

#### **1. Volatility Scoring**
```python
volatility = std(daily_returns) × √252  
```

**Classification:**
- Low: < 15% (Stable blue-chip stocks)
- Medium: 15-30% (Moderate risk)
- High: 30-50% (Growth stocks)
- Very High: > 50% (Speculative/penny stocks)

**Use Case:** Risk assessment for portfolio diversification

---

#### **2. Correlation Analysis**
```python
correlation = pearson_correlation(stock1_returns, stock2_returns)
```

**Interpretation:**
- +1.0: Perfect positive correlation (move together)
- 0.0: No correlation (independent)
- -1.0: Perfect negative correlation (move opposite)

**Use Case:** Portfolio hedging and diversification strategies

---

#### **3. Trend Detection**
```python
# Linear regression on recent prices
slope, r_squared = linear_regression(prices[-20:])

if r_squared > 0.5 and slope > 0: trend = "bullish"
elif r_squared > 0.5 and slope < 0: trend = "bearish"
else: trend = "neutral"
```

**Use Case:** Automated trading signals and market sentiment

---

#### **4. Momentum Score**
```python
momentum_score = (current_price - MA30) / MA30 × 100
```

**Interpretation:**
- Positive: Price above average (bullish momentum)
- Negative: Price below average (bearish momentum)
- |Score| > 5%: Strong momentum

**Use Case:** Entry/exit timing for trades

---

#### **5. Volume Trend Analysis**
```python
volume_trend = (current_volume - avg_volume_20d) / avg_volume_20d × 100
```

**Interpretation:**
- High volume + price up = Strong buying
- High volume + price down = Strong selling
- Low volume = Weak conviction

**Use Case:** Confirmation of price movements

---

## 🔌 **API Documentation**

### **Base URL:** `http://localhost:8000/api/v1`

### **Endpoints:**

#### **1. Get All Companies**
```http
GET /companies
GET /companies?sector=IT

Response: 200 OK
[
  {
    "symbol": "RELIANCE",
    "name": "Reliance Industries",
    "sector": "Energy",
    "industry": "Oil & Gas",
    "market_cap": 1500000000000
  }
]
```

---

#### **2. Get Stock Data**
```http
GET /data/{symbol}?days=30

Example: GET /data/RELIANCE?days=30

Response: 200 OK
[
  {
    "date": "2025-11-15",
    "open": 2850.50,
    "high": 2875.00,
    "low": 2840.25,
    "close": 2865.75,
    "volume": 5234567,
    "daily_return": 0.53,
    "ma7": 2858.30,
    "ma30": 2820.45
  }
]
```

---

#### **3. Get Summary Statistics**
```http
GET /summary/{symbol}

Example: GET /summary/TCS

Response: 200 OK
{
  "symbol": "TCS",
  "current_price": 3650.25,
  "week52_high": 3800.00,
  "week52_low": 3200.50,
  "avg_close": 3550.75,
  "total_volume": 125000000,
  "volatility": 1.85,
  "daily_return": 0.75,
  "trend": "bullish"
}
```

---

#### **4. Compare Two Stocks**
```http
GET /compare?symbol1=INFY&symbol2=TCS&days=90

Response: 200 OK
{
  "symbol1": "INFY",
  "symbol2": "TCS",
  "correlation": 0.7234,
  "symbol1_return": 12.45,
  "symbol2_return": 8.32,
  "symbol1_volatility": 2.15,
  "symbol2_volatility": 1.85,
  "better_performer": "INFY"
}
```

---

#### **5. Get Top Movers**
```http
GET /movers?limit=5

Response: 200 OK
{
  "gainers": [
    {
      "symbol": "RELIANCE",
      "name": "Reliance Industries",
      "current_price": 2865.75,
      "change_percent": 2.34,
      "volume": 5234567
    }
  ],
  "losers": [
    {
      "symbol": "SBIN",
      "name": "State Bank of India",
      "current_price": 645.20,
      "change_percent": -1.85,
      "volume": 8765432
    }
  ]
}
```

---

#### **6. Get Technical Indicators**
```http
GET /technicals/{symbol}

Example: GET /technicals/RELIANCE

Response: 200 OK
{
  "symbol": "RELIANCE",
  "rsi": 65.34,
  "macd": {
    "macd_line": 12.45,
    "signal_line": 10.20,
    "histogram": 2.25
  },
  "support_resistance": {
    "support": 2800.00,
    "resistance": 2950.00
  },
  "predicted_next_price": 2875.50,
  "current_price": 2865.75
}
```

## 🖥️ **Frontend Features**

### **1. Interactive Price Charts**
- Line charts with Chart.js 4.4
- Hover tooltips showing exact prices
- Zoom and pan functionality
- Moving averages overlay (MA7, MA30)
- Date range selection (7D, 30D, 90D, 180D)

### **2. Stock Comparison**
- Dual-line charts comparing two stocks
- Correlation coefficient display
- Side-by-side performance metrics
- Returns and volatility comparison

### **3. Real-time Updates**
- Top gainers/losers auto-refresh
- Summary statistics cards
- Technical indicators panel
- Responsive toast notifications

### **4. Responsive Design**
- Mobile-first approach
- Tablet optimization
- Desktop full-screen layout
- Dark theme with glassmorphism effects


## 🧪 **Testing**

### **Manual Testing via Swagger UI**

1. Start backend: `python backend/run.py`
2. Open: `http://localhost:8000/api/docs`
3. Test each endpoint using "Try it out" button

### **Automated Tests**

```bash
# Run test suite
pytest tests/test_api.py -v

# With coverage
pytest --cov=app tests/
```

### **Frontend Testing**

1. Start both servers
2. Open: `http://localhost:3000`
3. Test checklist:
   - ✅ Click on companies
   - ✅ View charts
   - ✅ Change time ranges
   - ✅ Compare two stocks
   - ✅ Check technical indicators

---

