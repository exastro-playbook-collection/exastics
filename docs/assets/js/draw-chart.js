// Define a plugin to provide data labels
var dataLabelPlugin = {
    afterDatasetsDraw: function (chart, easing) {
        // To only draw at the end of animation, check for easing === 1
        var ctx = chart.ctx;

        chart.data.datasets.forEach(function (dataset, i) {
            var meta = chart.getDatasetMeta(i);
            if (!meta.hidden) {
                meta.data.forEach(function (element, index) {
                    // Draw the text in black, with the specified font
                    ctx.fillStyle = 'rgb(0, 0, 0)';

                    var fontSize = 16;
                    var fontStyle = 'normal';
                    var fontFamily = 'Helvetica Neue';
                    ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);

                    // Just naively convert to string for now
                    var dataString = dataset.data[index].toString();

                    // Make sure alignment settings are correct
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    var padding = 5;
                    var position = element.tooltipPosition();
                    ctx.fillText(dataString, position.x, position.y - (fontSize / 2) - padding);
                });
            }
        });
    }
};

function renderChartContainerTemplate(content, chartIndexEntry, chartNumber) {
    const chartContainerNode = content.querySelector('#chart-container');
    chartContainerNode.id = 'chart-container-' + chartNumber;

    const chartCaptionNode = content.querySelector('#chart-caption');
    chartCaptionNode.id = "chart-caption-" + chartNumber;
    chartCaptionNode.textContent = chartIndexEntry.caption;

    const chartCanvasNode = content.querySelector('#chart-canvas');
    chartCanvasNode.id = "chart-canvas-" + chartNumber;

    return content;
}

function attachBarChart(context, chartData) {
    var labels = [];
    var data = [];
    for (entry of chartData) {
        labels.push(entry.repos);
        data.push(entry.count);
    }

    const myBarChart = new Chart(context, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    ticks: {
                        autoSkip: false
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            legend: {
                display: false
            },
            plugins: [
                dataLabelPlugin,
                {
                    colorschemes: {
                        scheme: 'brewer.DarkTwo8'
                    }
                }
            ]
        }
    });
}

function trimChartData(forPastDays, chartDataOrigin) {
    if (forPastDays == 99999) {
        return chartDataOrigin;
    }
    
    var chartDataTrimed = [];
    dateTrimed = new Date();
    dateTrimed.setDate(dateTrimed.getDate() - forPastDays);

    for (entryOrigin of chartDataOrigin) {
        entryTrimed = {
            series : entryOrigin.series,
            points : []
        };

        var yBase = -1;
        for (pointOrigin of entryOrigin["points"]) {
            dateOrigin = new Date(pointOrigin.x);
            if (dateOrigin > dateTrimed) {
                if (yBase == -1) yBase = pointOrigin.y;
                pointOrigin.y = pointOrigin.y - yBase;
                entryTrimed.points.push(pointOrigin);
            }
        }
        chartDataTrimed.push(entryTrimed);
    }

    return chartDataTrimed;
}

function attachLineChart(context, chartData) {
    var datasets = [];
    for (entry of chartData) {
        datasets.push({
            label: entry.series,
            data: entry.points,
            fill: false
        });
    }

    const myLineChart = new Chart(context, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            legend: {
                position: 'right'
            },
            plugins: {
                colorschemes: {
                    scheme: 'brewer.DarkTwo8'
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const saveState = sessionStorage.getItem('forThePastDates');
    const forThePastDates = saveState ? parseInt(saveState, 10) : 99999;

    const parentNode = document.querySelector('#chart-plain');
    const templateContent = document.querySelector('#chart-container-template').content;

    fetch('assets/chart-index.json')
        .then(response => response.json())
        .then(chartIndex => {
            {
                const content = document.importNode(templateContent, true);
                const renderedContent = renderChartContainerTemplate(content, chartIndex[0], 0);
                parentNode.appendChild(renderedContent);

                fetch(chartIndex[0].data_file)
                    .then(response => response.json())
                    .then(chartData => {        
                        const context = document.getElementById("chart-canvas-" + 0);
                        attachBarChart(context, chartData)
                    });
            }
            for (let i = 1; i < chartIndex.length; i++) {
                const content = document.importNode(templateContent, true);
                const renderedContent = renderChartContainerTemplate(content, chartIndex[i], i);
                parentNode.appendChild(renderedContent);

                fetch(chartIndex[i].data_file)
                    .then(response => response.json())
                    .then(chartDataOrigin => trimChartData(forThePastDates, chartDataOrigin))
                    .then(chartData => {
                        const context = document.getElementById("chart-canvas-" + i);
                        attachLineChart(context, chartData)
                    });
            }
        });
});

var forThePast030Dates = document.getElementById('forThePast030Dates');
forThePast030Dates.addEventListener('click', () => {
    sessionStorage.setItem('forThePastDates', '30');
    location.reload();
});

var forThePast060Dates = document.getElementById('forThePast060Dates');
forThePast060Dates.addEventListener('click', () => {
    sessionStorage.setItem('forThePastDates', '60');
    location.reload();
});

var forThePast180Dates = document.getElementById('forThePast180Dates');
forThePast180Dates.addEventListener('click', () => {
    sessionStorage.setItem('forThePastDates', '180');
    location.reload();
});

var forThePastAllDates = document.getElementById('forThePastAllDates');
forThePastAllDates.addEventListener('click', () => {
    sessionStorage.removeItem('forThePastDates');
    location.reload();
});
