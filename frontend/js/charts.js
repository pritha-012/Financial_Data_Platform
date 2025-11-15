/**
 * Chart Rendering Module
 * Handles Chart.js visualization for stock price data
 */

// Global chart instance
let priceChart = null;

// Chart color scheme
const CHART_COLORS = {
    primary: '#3b82f6',      // Blue
    secondary: '#06b6d4',    // Cyan
    success: '#10b981',      // Green
    danger: '#ef4444',       // Red
    warning: '#f59e0b',      // Yellow/Orange
    grid: '#334155',         // Gray
    text: '#94a3b8'          // Light Gray
};

/**
 * Render or update the price chart with stock data
 * @param {Array} data - Stock data array with date, open, high, low, close, volume
 * @param {string} symbol - Stock symbol for the main line
 * @param {Array} compareData - Optional comparison stock data
 * @param {string} compareSymbol - Optional comparison stock symbol
 */
function renderPriceChart(data, symbol, compareData = null, compareSymbol = null) {
    const canvas = document.getElementById('price-chart');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Prepare main stock dataset
    const datasets = [
        {
            label: `${symbol} Close Price`,
            data: data.map(d => ({
                x: d.date,
                y: d.close
            })),
            borderColor: CHART_COLORS.primary,
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: CHART_COLORS.primary,
            tension: 0.4,
            fill: true
        }
    ];
    
    // Add 7-day moving average if available
    if (data[0]?.ma7) {
        datasets.push({
            label: '7-Day MA',
            data: data.map(d => ({
                x: d.date,
                y: d.ma7
            })),
            borderColor: CHART_COLORS.warning,
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            borderDash: [5, 5],
            tension: 0.4,
            fill: false
        });
    }
    
    // Add 30-day moving average if available
    if (data[0]?.ma30) {
        datasets.push({
            label: '30-Day MA',
            data: data.map(d => ({
                x: d.date,
                y: d.ma30
            })),
            borderColor: CHART_COLORS.success,
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            borderDash: [10, 5],
            tension: 0.4,
            fill: false
        });
    }
    
    // Add comparison stock if provided
    if (compareData && compareSymbol) {
        datasets.push({
            label: `${compareSymbol} Close Price`,
            data: compareData.map(d => ({
                x: d.date,
                y: d.close
            })),
            borderColor: CHART_COLORS.secondary,
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            borderWidth: 3,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: CHART_COLORS.secondary,
            tension: 0.4,
            fill: true
        });
    }
    
    // Destroy existing chart if it exists
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: CHART_COLORS.text,
                        padding: 15,
                        font: {
                            size: 12,
                            family: "'Inter', 'system-ui', sans-serif"
                        },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    borderColor: CHART_COLORS.grid,
                    borderWidth: 1,
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    padding: 12,
                    displayColors: true,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        title: function(context) {
                            // Format date nicely
                            const date = new Date(context[0].parsed.x);
                            return date.toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                            });
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '₹' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'MMM dd',
                            week: 'MMM dd',
                            month: 'MMM yyyy'
                        }
                    },
                    grid: {
                        color: CHART_COLORS.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: CHART_COLORS.text,
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 10,
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: CHART_COLORS.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: CHART_COLORS.text,
                        callback: function(value) {
                            return '₹' + value.toFixed(0);
                        },
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Chart rendered successfully');
}

/**
 * Destroy the current chart instance
 */
function destroyChart() {
    if (priceChart) {
        priceChart.destroy();
        priceChart = null;
    }
}

// Export functions to global scope
window.renderPriceChart = renderPriceChart;
window.destroyChart = destroyChart;