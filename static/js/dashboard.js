// Initialize Chart.js charts
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        y: { beginAtZero: true },
        x: { display: false }
    },
    plugins: { legend: { display: false } }
};

const cpuChart = new Chart(document.getElementById('cpu-chart').getContext('2d'), {
    type: 'line',
    data: {
        labels: Array(20).fill(''),
        datasets: [{
            data: Array(20).fill(0),
            borderColor: '#4CAF50',
            tension: 0.4,
            fill: false
        }]
    },
    options: chartOptions
});

const memoryChart = new Chart(document.getElementById('memory-chart').getContext('2d'), {
    type: 'line',
    data: {
        labels: Array(20).fill(''),
        datasets: [{
            data: Array(20).fill(0),
            borderColor: '#2196F3',
            tension: 0.4,
            fill: false
        }]
    },
    options: chartOptions
});

const networkChart = new Chart(document.getElementById('network-chart').getContext('2d'), {
    type: 'line',
    data: {
        labels: Array(20).fill(''),
        datasets: [{
            data: Array(20).fill(0),
            borderColor: '#9C27B0',
            tension: 0.4,
            fill: false
        }]
    },
    options: chartOptions
});

const diskChart = new Chart(document.getElementById('disk-chart').getContext('2d'), {
    type: 'line',
    data: {
        labels: Array(20).fill(''),
        datasets: [{
            data: Array(20).fill(0),
            borderColor: '#FF9800',
            tension: 0.4,
            fill: false
        }]
    },
    options: chartOptions
});

// WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard/`);

ws.onopen = function() {
    console.log('WebSocket connected');
    // Request initial stats
    ws.send(JSON.stringify({ type: 'get_stats' }));
    // Request initial packets
    ws.send(JSON.stringify({ type: 'get_packets' }));
};

ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'system_stats' && data.data) {
        updateSystemStats(data.data);
    } else if (data.type === 'recent_packets' && data.data) {
        updatePacketTable(data.data);
    }
};

ws.onclose = function() {
    console.log('WebSocket disconnected');
    // Try to reconnect after 5 seconds
    setTimeout(() => {
        window.location.reload();
    }, 5000);
};

function updateSystemStats(stats) {
    // Update display values
    document.getElementById('cpu-usage').textContent = stats.cpu_usage.toFixed(1);
    document.getElementById('memory-usage').textContent = stats.memory_usage.toFixed(1);
    document.getElementById('disk-usage').textContent = stats.disk_usage.toFixed(1);
    
    // Format network values to KB/s
    const networkIn = (stats.network_in / 1024).toFixed(1);
    const networkOut = (stats.network_out / 1024).toFixed(1);
    document.getElementById('network-sent').textContent = networkOut;
    document.getElementById('network-recv').textContent = networkIn;

    // Update charts
    updateChart(cpuChart, stats.cpu_usage);
    updateChart(memoryChart, stats.memory_usage);
    updateChart(diskChart, stats.disk_usage);
    updateChart(networkChart, (stats.network_in + stats.network_out) / 1024); // Total network in KB
}

function updateChart(chart, value) {
    chart.data.datasets[0].data.push(value);
    chart.data.datasets[0].data.shift();
    chart.update('none'); // Use 'none' mode for better performance
}

function updatePacketTable(packets) {
    const tbody = document.querySelector('#packet-table tbody');
    if (!tbody) return;

    tbody.innerHTML = packets.map(packet => `
        <tr class="hover:bg-gray-50">
            <td class="px-3 py-2 text-sm text-gray-500">
                ${new Date(packet.timestamp).toLocaleTimeString()}
            </td>
            <td class="px-3 py-2">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${getProtocolColor(packet.protocol)}">
                    ${packet.protocol}
                </span>
            </td>
            <td class="px-3 py-2 text-sm text-gray-500">${packet.source}</td>
            <td class="px-3 py-2 text-sm text-gray-500">${packet.destination}</td>
            <td class="px-3 py-2 text-sm text-gray-500">${packet.size} bytes</td>
        </tr>
    `).join('');
}

function getProtocolColor(protocol) {
    switch (protocol.toUpperCase()) {
        case 'TCP': return 'bg-blue-100 text-blue-800';
        case 'UDP': return 'bg-green-100 text-green-800';
        case 'ICMP': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// Request updates every second
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'get_stats' }));
        ws.send(JSON.stringify({ type: 'get_packets' }));
    }
}, 1000); 