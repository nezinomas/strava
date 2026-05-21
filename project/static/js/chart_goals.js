function loadChart(idData, idContainer) {
    const chartData = JSON.parse(document.getElementById(idData).textContent);

    Highcharts.chart(idContainer, {
        chart: {
            type: 'bar',
            height: 90,
            style: {
                fontFamily: "'Inter', sans-serif"
            }
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: chartData.categories,
            gridLineWidth: 0,
            labels: {
                enabled: false
            }
        },
        yAxis: {
            max: chartData.ymax,
            title: {
                text: ''
            },
            gridLineColor: '#e2e8f0'
        },
        tooltip: {
            shared: true,
            headerFormat: '',
            pointFormat: '{series.name}: <b>{point.y:.1f}h</b><br/>',
            backgroundColor: '#ffffff',
            borderColor: '#e2e8f0',
            borderRadius: 8,
            style: {
                fontFamily: "'Inter', sans-serif",
                fontSize: '12px',
                color: '#1e293b'
            }
        },
        series: [{
            name: chartData.targetTitle,
            type: 'bar',
            color: 'rgba(15, 23, 42, 0.06)', // Soft slate overlay for target
            data: chartData.target,
            border: 0,
            dataLabels: {
                enabled: false,
            }
        }, {
            name: chartData.factTitle,
            type: 'bullet',
            data: chartData.fact,
            border: 0,
            borderRadius: 4,
            targetOptions: {
                borderWidth: 0,
                borderColor: '#64748b',
                height: 2,
                color: '#64748b',
                width: '250%'
            },
            dataLabels: {
                enabled: true,
                color: '#1e293b',
                align: 'right',
                y: -1,
                style: {
                    fontFamily: "'Inter', sans-serif",
                    fontWeight: '600',
                    textOutline: 'none',
                    fontSize: '13px',
                },
                formatter: function() {
                    return `${chartData.percent}%`;
                },
            },
        }]
    }, function (chartObj) {
        let max = chartObj.series[0].data[0].y;
        let point = chartObj.series[1].data[0];

        max = parseFloat(max.toFixed(1));
        y = parseFloat(point.y.toFixed(1));

        let color;
        if (y <= max) {
            color = '#fb7185'; // Modern soft red-400
        }
        else {
            color = '#19af23'; // Ekspla vibrant green
        }

        point.color = color;
        point.graphic.attr({ fill: color });
    });
}
