"""
Custom calculations and metrics for financial analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict
from scipy import stats


def calculate_sharpe_ratio(
    returns: List[float], 
    risk_free_rate: float = 0.05
) -> float:
    """
    Calculate Sharpe Ratio
    Measures risk-adjusted return
    
    Formula: (Mean Return - Risk Free Rate) / Std Dev of Returns
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
   
    sharpe = (mean_return - risk_free_rate/252) / std_return * np.sqrt(252)
    return round(sharpe, 4)


def calculate_beta(
    stock_returns: List[float], 
    market_returns: List[float]
) -> float:
    """
    Calculate Beta - measure of stock volatility relative to market
    
    Beta > 1: More volatile than market
    Beta < 1: Less volatile than market
    Beta = 1: Moves with market
    """
    if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
        return 1.0
    
    covariance = np.cov(stock_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)
    
    if market_variance == 0:
        return 1.0
    
    beta = covariance / market_variance
    return round(beta, 4)


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    
    RSI > 70: Overbought
    RSI < 30: Oversold
    """
    if len(prices) < period + 1:
        return 50.0
    

    deltas = np.diff(prices)
    
 
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
   
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_macd(
    prices: List[float], 
    fast: int = 12, 
    slow: int = 26, 
    signal: int = 9
) -> Dict[str, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Returns dict with:
    - macd_line: Fast EMA - Slow EMA
    - signal_line: 9-day EMA of MACD line
    - histogram: MACD - Signal
    """
    if len(prices) < slow:
        return {'macd_line': 0, 'signal_line': 0, 'histogram': 0}
    
    prices_series = pd.Series(prices)
    
    # Calculate EMAs
    ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return {
        'macd_line': round(macd_line.iloc[-1], 2),
        'signal_line': round(signal_line.iloc[-1], 2),
        'histogram': round(histogram.iloc[-1], 2)
    }


def calculate_bollinger_bands(
    prices: List[float], 
    period: int = 20, 
    num_std: int = 2
) -> Dict[str, float]:
    """
    Calculate Bollinger Bands
    
    Returns dict with:
    - upper_band: SMA + (std * num_std)
    - middle_band: SMA
    - lower_band: SMA - (std * num_std)
    """
    if len(prices) < period:
        return {'upper_band': 0, 'middle_band': 0, 'lower_band': 0}
    
    recent_prices = prices[-period:]
    sma = np.mean(recent_prices)
    std = np.std(recent_prices)
    
    return {
        'upper_band': round(sma + (std * num_std), 2),
        'middle_band': round(sma, 2),
        'lower_band': round(sma - (std * num_std), 2),
        'current_price': round(prices[-1], 2)
    }


def detect_trend(prices: List[float], window: int = 20) -> str:
    """
    Detect price trend using linear regression
    
    Returns: 'bullish', 'bearish', or 'neutral'
    """
    if len(prices) < window:
        return 'neutral'
    
    recent_prices = prices[-window:]
    x = np.arange(len(recent_prices))
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_prices)
    
    # Determine trend based on slope and R-squared
    r_squared = r_value ** 2
    
    if r_squared < 0.5:  # Weak correlation
        return 'neutral'
    
    if slope > 0:
        return 'bullish'
    elif slope < 0:
        return 'bearish'
    else:
        return 'neutral'


def calculate_support_resistance(
    highs: List[float], 
    lows: List[float], 
    window: int = 20
) -> Dict[str, float]:
    """
    Calculate support and resistance levels
    """
    if len(highs) < window or len(lows) < window:
        return {'resistance': 0, 'support': 0}
    
    recent_highs = highs[-window:]
    recent_lows = lows[-window:]
    
    resistance = np.percentile(recent_highs, 95)
    support = np.percentile(recent_lows, 5)
    
    return {
        'resistance': round(resistance, 2),
        'support': round(support, 2)
    }


def calculate_volatility_score(returns: List[float]) -> str:
    """
    Calculate volatility score and classify
    
    Returns: 'low', 'medium', 'high', or 'very_high'
    """
    if not returns or len(returns) < 2:
        return 'medium'
    
    volatility = np.std(returns) * np.sqrt(252)  # Annualized
    
    if volatility < 0.15:
        return 'low'
    elif volatility < 0.30:
        return 'medium'
    elif volatility < 0.50:
        return 'high'
    else:
        return 'very_high'


def predict_next_price(prices: List[float], method: str = 'linear') -> float:
    """
    Simple price prediction using various methods
    
    Methods:
    - 'linear': Linear regression
    - 'ma': Moving average
    - 'ema': Exponential moving average
    """
    if len(prices) < 10:
        return prices[-1] if prices else 0
    
    if method == 'linear':
        x = np.arange(len(prices))
        slope, intercept, _, _, _ = stats.linregress(x, prices)
        next_price = slope * len(prices) + intercept
        
    elif method == 'ma':
        next_price = np.mean(prices[-10:])
        
    elif method == 'ema':
        prices_series = pd.Series(prices)
        ema = prices_series.ewm(span=10, adjust=False).mean()
        next_price = ema.iloc[-1]
        
    else:
        next_price = prices[-1]
    
    return round(next_price, 2)