// Initialize charts and data when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize traffic chart
    initTrafficChart();
    
    // Start system stat updates
    updateSystemStats();
    setInterval(updateSystemStats, 10000); // Update every 10 seconds
    
    // Set up the refresh button
    document.querySelector('.refresh-btn').addEventListener('click', function() {
        this.querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            window.location.reload();
        }, 500);
    });
});

// Initialize the traffic chart
function initTrafficChart() {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    
    // Fetch data from API
    fetch('/api/packet_stats')
        .then(response => response.json())
        .then(data => {
            // Create the chart
            const trafficChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: data.datasets.map(dataset => {
                        return {
                            ...dataset,
                            fill: false,
                            pointRadius: 3,
                            pointHoverRadius: 5,
                            tension: 0.3
                        };
                    })
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            titleColor: '#1e293b',
                            bodyColor: '#64748b',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            padding: 10,
                            displayColors: true,
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw} packets`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(226, 232, 240, 0.5)'
                            },
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching traffic data:', error);
            document.getElementById('trafficChart').parentElement.innerHTML = 
                '<div class="error-message">Failed to load traffic data. Please try refreshing.</div>';
        });
}
let trafficChart;

document.addEventListener('DOMContentLoaded', function () {
    // Initialize system stats
    updateSystemStats();
    setInterval(updateSystemStats, 10000);

    // Setup refresh button
    document.querySelector('.refresh-btn').addEventListener('click', function () {
        this.querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            window.location.reload();
        }, 500);
    });

    // Set up live traffic chart updates via WebSocket
    setupTrafficSocket();
});

function setupTrafficSocket() {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to traffic WebSocket');
    });

    socket.on('traffic_update', (data) => {
        if (!trafficChart) {
            trafficChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: data.datasets.map(dataset => ({
                        ...dataset,
                        fill: false,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        tension: 0.3
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            titleColor: '#1e293b',
                            bodyColor: '#64748b',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            padding: 10,
                            displayColors: true,
                            callbacks: {
                                label: function (context) {
                                    return `${context.dataset.label}: ${context.raw} packets`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(226, 232, 240, 0.5)'
                            },
                            ticks: { precision: 0 }
                        }
                    }
                }
            });
        } else {
            trafficChart.data.labels = data.labels;
            trafficChart.data.datasets.forEach((ds, i) => {
                ds.data = data.datasets[i].data;
            });
            trafficChart.update();
        }
    });

    socket.on('disconnect', () => {
        console.warn('Disconnected from traffic WebSocket');
    });
}

// Update system stats (CPU, memory)
function updateSystemStats() {
    fetch('/api/system_stats')
        .then(response => response.json())
        .then(data => {
            // Update CPU usage
            const cpuUsage = document.getElementById('cpu-usage');
            const cpuValue = document.getElementById('cpu-value');
            cpuUsage.style.width = `${data.cpu_percent}%`;
            cpuValue.textContent = `${data.cpu_percent}%`;
            
            // Update memory usage
            const memoryUsage = document.getElementById('memory-usage');
            const memoryValue = document.getElementById('memory-value');
            memoryUsage.style.width = `${data.memory_percent}%`;
            memoryValue.textContent = `${data.memory_percent}%`;
            
            // Set colors based on usage
            setCpuColor(cpuUsage, data.cpu_percent);
            setMemoryColor(memoryUsage, data.memory_percent);
        })
        .catch(error => {
            console.error('Error fetching system stats:', error);
        });
}

// Set CPU progress bar color based on usage
function setCpuColor(element, percent) {
    if (percent < 50) {
        element.style.backgroundColor = 'var(--color-low)';
    } else if (percent < 80) {
        element.style.backgroundColor = 'var(--color-medium)';
    } else {
        element.style.backgroundColor = 'var(--color-high)';
    }
}

// Set memory progress bar color based on usage
function setMemoryColor(element, percent) {
    if (percent < 60) {
        element.style.backgroundColor = 'var(--color-low)';
    } else if (percent < 85) {
        element.style.backgroundColor = 'var(--color-medium)';
    } else {
        element.style.backgroundColor = 'var(--color-high)';
    }
}

// Format large numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format bytes to appropriate units
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format ISO dates to relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return `${diffInSeconds} seconds ago`;
    } else if (diffInSeconds < 3600) {
        return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    } else if (diffInSeconds < 86400) {
        return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    } else {
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }
}