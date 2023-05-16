// Create a new Chart.js line chart with the daily revenue data
const dailyRevenueChart = new Chart($('#daily-revenue-chart'), {
    type: 'line',
    data: {
        // Use the array of daily revenue data as the chart data
        labels: [...Array(window.dailyRevenueData.length).keys()].map(function (i) {
            return i + 1;
        }),
        datasets: [{
            label: 'Daily Revenue',
            data: window.dailyRevenueData,
            fill: false,
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointBorderColor: '#fff',
            pointHoverRadius: 10,
            pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointHoverBorderColor: '#fff'
        }]
    },
    options: {
        // Customize the chart tooltip
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let euroSymbol = '\u20AC';
                        return euroSymbol + context.parsed.y.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
                    }
                }
            }
        },
        // Customize the chart title and axes
        title: {
            display: true,
            text: 'Daily Revenue for the Month',
            fontColor: 'white'
        },
        scales: {
            xAxes: [{
                ticks: {
                    fontColor: 'white',
                    fontSize: 14
                }
            }],
            yAxes: [{
                ticks: {
                    fontColor: 'white',
                    fontSize: 14,
                    beginAtZero: true,
                    stepSize: 5000,
                    callback: function (value, index, values) {
                        // Add a Euro symbol to the y-axis ticks and format them as currency
                        let euroSymbol = '\u20AC';
                        return euroSymbol + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
                    }
                }
            }]
        }
    }
});

// Get the country revenue data from the data attribute of the revenue-by-country-chart canvas element
const countryRevenueData = JSON.parse($('#revenue-by-country-chart').attr('data-country-revenue'));

// Sort the country revenue data in descending order
const sortedCountryRevenueData = Object.entries(countryRevenueData).sort(function (a, b) {
    return b[1] - a[1];
});

// Get the top 6 countries and group the remaining into "Others"
const topCountries = sortedCountryRevenueData.slice(0, 6).map(function (entry) {
    return entry[0];
});
const topRevenues = sortedCountryRevenueData.slice(0, 6).map(function (entry) {
    return entry[1];
});
const remainingRevenue = sortedCountryRevenueData.slice(6).reduce(function (sum, entry) {
    return sum + entry[1];
}, 0);

const backgroundColor = [
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    '#8C4646',
    '#A6D785',
    '#DE9E36',
];

// Add an "Others" category to the data
if (sortedCountryRevenueData.length > 6) {
    topCountries.push("Others");
    topRevenues.push(remainingRevenue);
    backgroundColor.push("#BBBBBB");
}

// Create a new Chart.js pie chart with the country revenue data
const countryRevenueChart = new Chart($('#revenue-by-country-chart'), {
    type: 'pie',
    data: {
        labels: topCountries,
        datasets: [{
            data: topRevenues,
            backgroundColor: backgroundColor
        }]
    },
    options: {
        responsive: true,
        // Customize the chart title
        title: {
            display: true,
            text: 'Revenue by Country',
            fontColor: 'white'
        },
        // Customize the tooltip
        tooltips: {
            callbacks: {
                label: function (tooltipItem, data) {
                    let dataset = data.datasets[tooltipItem.datasetIndex];
                    let value = dataset.data[tooltipItem.index];
                    let label = data.labels[tooltipItem.index];
                    if (typeof value === 'number') {
                        value = value.toFixed(2);
                    }
                    // Add the Euro symbol and country name to the tooltip
                    let euroSymbol = '\u20AC';
                    return label + ': ' + value + ' ' + euroSymbol;
                }
            }
        }
    }
});