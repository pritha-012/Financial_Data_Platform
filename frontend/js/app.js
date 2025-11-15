/**
 * Main Application Logic
 * Handles UI interactions and data flow
 */

// Application state
const state = {
    selectedSymbol: null,
    selectedDays: 30,
    compareSymbol: null,
    companies: [],
    stockData: [],
    compareData: []
};

/**
 * Initialize application
 */
async function initApp() {
    showToast('Initializing FinData Platform...', 'success');
    
    // Check API health
    const apiHealthy = await checkAPIHealth();
    if (!apiHealthy) {
        showToast('Warning: Unable to connect to API. Using demo mode.', 'warning');
        loadDemoData();
        return;
    }
    
    // Load initial data
    await loadCompanies();
    await loadTopMovers();
    
    // Setup event listeners
    setupEventListeners();
    
    showToast('Platform ready!', 'success');
}

/**
 * Load companies list
 */
async function loadCompanies() {
    const listElement = document.getElementById('companies-list');
    listElement.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const companies = await API.getCompanies();
        state.companies = companies;
        
        listElement.innerHTML = '';
        companies.forEach(company => {
            const button = document.createElement('button');
            button.className = 'company-item';
            button.innerHTML = `
                <div class="company-name">${company.symbol}</div>
                <div class="company-sector">${company.sector || 'N/A'}</div>
            `;
            button.onclick = () => selectStock(company.symbol);
            listElement.appendChild(button);
        });
        
        // Populate compare dropdown
        const compareSelect = document.getElementById('compare-select');
        compareSelect.innerHTML = '<option value="">Compare with...</option>';
        companies.forEach(company => {
            const option = document.createElement('option');
            option.value = company.symbol;
            option.textContent = company.symbol;
            compareSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading companies:', error);
        listElement.innerHTML = '<p style="color: #ef4444; text-align: center;">Failed to load companies</p>';
        showToast('Failed to load companies', 'error');
    }
}

/**
 * Load top movers (gainers and losers)
 */
async function loadTopMovers() {
    const gainersElement = document.getElementById('gainers-list');
    const losersElement = document.getElementById('losers-list');
    
    gainersElement.innerHTML = '<div class="loading-spinner"></div>';
    losersElement.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const movers = await API.getTopMovers(5);
        
        // Render gainers
        gainersElement.innerHTML = '';
        movers.gainers.forEach(stock => {
            const div = document.createElement('div');
            div.className = 'mover-item';
            div.innerHTML = `
                <span class="mover-symbol">${stock.symbol}</span>
                <span class="gain">+${stock.change_percent.toFixed(2)}%</span>
            `;
            gainersElement.appendChild(div);
        });
        
        // Render losers
        losersElement.innerHTML = '';
        movers.losers.forEach(stock => {
            const div = document.createElement('div');
            div.className = 'mover-item';
            div.innerHTML = `
                <span class="mover-symbol">${stock.symbol}</span>
                <span class="loss">${stock.change_percent.toFixed(2)}%</span>
            `;
            losersElement.appendChild(div);
        });
        
    } catch (error) {
        console.error('Error loading movers:', error);
        gainersElement.innerHTML = '<p style="color: #94a3b8; font-size: 0.85rem;">Failed to load</p>';
        losersElement.innerHTML = '<p style="color: #94a3b8; font-size: 0.85rem;">Failed to load</p>';
    }
}

/**
 * Select a stock and load its data
 */
async function selectStock(symbol) {
    state.selectedSymbol = symbol;
    state.compareSymbol = null;
    
    // Update UI
    document.getElementById('empty-state').style.display = 'none';
    document.getElementById('stock-content').style.display = 'block';
    document.getElementById('comparison-card').style.display = 'none';
    document.getElementById('chart-title').textContent = `${symbol} - Price Movement`;
    
    // Update active state in companies list
    document.querySelectorAll('.company-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent.includes(symbol)) {
            item.classList.add('active');
        }
    });
    
    // Reset compare dropdown
    document.getElementById('compare-select').value = '';
    
    // Load stock data
    await Promise.all([
        loadStockData(symbol),
        loadStockSummary(symbol),
        loadTechnicalIndicators(symbol)
    ]);
}

/**
 * Load stock data and render chart
 */
async function loadStockData(symbol) {
    try {
        const data = await API.getStockData(symbol, state.selectedDays);
        state.stockData = data;
        
        renderPriceChart(data, symbol);
        
    } catch (error) {
        console.error('Error loading stock data:', error);
        showToast(`Failed to load data for ${symbol}`, 'error');
    }
}

/**
 * Load stock summary statistics
 */
async function loadStockSummary(symbol) {
    try {
        const summary = await API.getStockSummary(symbol);
        
        document.getElementById('current-price').textContent = `₹${summary.current_price.toFixed(2)}`;
        document.getElementById('week52-high').textContent = `₹${summary.week52_high.toFixed(2)}`;
        document.getElementById('week52-low').textContent = `₹${summary.week52_low.toFixed(2)}`;
        document.getElementById('avg-close').textContent = `₹${summary.avg_close.toFixed(2)}`;
        document.getElementById('volatility').textContent = `${summary.volatility.toFixed(2)}%`;
        
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

/**
 * Load technical indicators
 */
async function loadTechnicalIndicators(symbol) {
    try {
        const technicals = await API.getTechnicalIndicators(symbol);
        
        // RSI
        const rsiValue = technicals.rsi;
        const rsiElement = document.getElementById('rsi-value');
        rsiElement.textContent = rsiValue.toFixed(2);
        rsiElement.style.color = rsiValue > 70 ? '#ef4444' : rsiValue < 30 ? '#10b981' : '#f59e0b';
        
        // MACD
        document.getElementById('macd-value').textContent = technicals.macd.macd_line.toFixed(2);
        
        // Support & Resistance
        document.getElementById('support-value').textContent = `₹${technicals.support_resistance.support.toFixed(2)}`;
        document.getElementById('resistance-value').textContent = `₹${technicals.support_resistance.resistance.toFixed(2)}`;
        
        // Predicted price
        const predictedPrice = technicals.predicted_next_price;
        const currentPrice = technicals.current_price;
        const priceDiff = ((predictedPrice - currentPrice) / currentPrice * 100);
        const predictedElement = document.getElementById('predicted-value');
        predictedElement.textContent = `₹${predictedPrice.toFixed(2)}`;
        predictedElement.style.color = priceDiff > 0 ? '#10b981' : '#ef4444';
        
        // Trend (from summary)
        const summary = await API.getStockSummary(symbol);
        const trendElement = document.getElementById('trend-value');
        trendElement.textContent = summary.trend.toUpperCase();
        trendElement.style.color = summary.trend === 'bullish' ? '#10b981' : 
                                     summary.trend === 'bearish' ? '#ef4444' : '#f59e0b';
        
    } catch (error) {
        console.error('Error loading technicals:', error);
    }
}

/**
 * Compare two stocks
 */
async function compareStocks(symbol2) {
    if (!state.selectedSymbol || !symbol2) return;
    
    state.compareSymbol = symbol2;
    
    try {
        // Load compare data
        const compareData = await API.getStockData(symbol2, state.selectedDays);
        state.compareData = compareData;
        
        // Update chart with comparison
        renderPriceChart(state.stockData, state.selectedSymbol, compareData, symbol2);
        
        // Load comparison statistics
        const comparison = await API.compareStocks(state.selectedSymbol, symbol2, state.selectedDays);
        
        // Show comparison card
        const comparisonCard = document.getElementById('comparison-card');
        comparisonCard.style.display = 'block';
        
        const comparisonContent = document.getElementById('comparison-content');
        comparisonContent.innerHTML = `
            <div class="comparison-item">
                <h4>${state.selectedSymbol}</h4>
                <div class="comparison-row">
                    <span>Return:</span>
                    <span class="${comparison.symbol1_return >= 0 ? 'gain' : 'loss'}">
                        ${comparison.symbol1_return.toFixed(2)}%
                    </span>
                </div>
                <div class="comparison-row">
                    <span>Volatility:</span>
                    <span>${comparison.symbol1_volatility.toFixed(2)}%</span>
                </div>
            </div>
            <div class="comparison-item">
                <h4>${symbol2}</h4>
                <div class="comparison-row">
                    <span>Return:</span>
                    <span class="${comparison.symbol2_return >= 0 ? 'gain' : 'loss'}">
                        ${comparison.symbol2_return.toFixed(2)}%
                    </span>
                </div>
                <div class="comparison-row">
                    <span>Volatility:</span>
                    <span>${comparison.symbol2_volatility.toFixed(2)}%</span>
                </div>
            </div>
            <div class="comparison-item" style="grid-column: 1 / -1;">
                <h4>Correlation Analysis</h4>
                <div class="comparison-row">
                    <span>Correlation:</span>
                    <span style="font-weight: 700;">${comparison.correlation.toFixed(4)}</span>
                </div>
                <div class="comparison-row">
                    <span>Better Performer:</span>
                    <span class="gain" style="font-weight: 700;">${comparison.better_performer}</span>
                </div>
            </div>
        `;
        
        showToast(`Comparing ${state.selectedSymbol} with ${symbol2}`, 'success');
        
    } catch (error) {
        console.error('Error comparing stocks:', error);
        showToast('Failed to compare stocks', 'error');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Time range buttons
    document.querySelectorAll('.btn-range').forEach(button => {
        button.addEventListener('click', async () => {
            const days = parseInt(button.dataset.days);
            state.selectedDays = days;
            
            // Update active state
            document.querySelectorAll('.btn-range').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Reload data if stock is selected
            if (state.selectedSymbol) {
                await loadStockData(state.selectedSymbol);
                if (state.compareSymbol) {
                    await compareStocks(state.compareSymbol);
                }
            }
        });
    });
    
    // Compare dropdown
    document.getElementById('compare-select').addEventListener('change', (e) => {
        const symbol2 = e.target.value;
        if (symbol2 && state.selectedSymbol) {
            compareStocks(symbol2);
        } else {
            // Reset comparison
            state.compareSymbol = null;
            document.getElementById('comparison-card').style.display = 'none';
            renderPriceChart(state.stockData, state.selectedSymbol);
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Load demo data (fallback when API is unavailable)
 */
function loadDemoData() {
    // Demo companies
    const demoCompanies = [
        { symbol: 'RELIANCE', name: 'Reliance Industries', sector: 'Energy' },
        { symbol: 'TCS', name: 'Tata Consultancy Services', sector: 'IT' },
        { symbol: 'INFY', name: 'Infosys', sector: 'IT' },
        { symbol: 'HDFC', name: 'HDFC Bank', sector: 'Banking' },
        { symbol: 'ICICI', name: 'ICICI Bank', sector: 'Banking' }
    ];
    
    state.companies = demoCompanies;
    
    const listElement = document.getElementById('companies-list');
    listElement.innerHTML = '';
    demoCompanies.forEach(company => {
        const button = document.createElement('button');
        button.className = 'company-item';
        button.innerHTML = `
            <div class="company-name">${company.symbol}</div>
            <div class="company-sector">${company.sector}</div>
        `;
        button.onclick = () => showToast('Demo mode: Real data unavailable', 'warning');
        listElement.appendChild(button);
    });
    
    document.getElementById('gainers-list').innerHTML = '<p style="color: #94a3b8;">Demo mode</p>';
    document.getElementById('losers-list').innerHTML = '<p style="color: #94a3b8;">Demo mode</p>';
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}