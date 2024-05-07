function loadChart(idData, idContainer) {
    const chartData = JSON.parse(document.getElementById(idData).textContent);

    Highcharts.chart(idContainer, {
        chart: {
            type: 'bar',
            height: 90,
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
            title: {
                text: ''
            },
        },
        tooltip: {
            shared: true,
            headerFormat: '',
            pointFormat: '{series.name}: <b>{point.y:.0f}</b><br/>',
        },
        series: [{
            name: chartData.targetTitle,
            type: 'bar',
            color: 'rgba(0,0,0,0.07)',
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
            borderRadius: 0,
            targetOptions: {
                borderWidth: 0,
                borderColor: '#000',
                height: 2,
                color: 'black',
                width: '250%'
            },
            dataLabels: {
                format: '{point.y:.0f}',
                enabled: true,
                color: '#000',
                align: 'right',
                y: -1,
                style: {
                    fontWeight: 'regular',
                    textOutline: false,
                    fontSize: '14px',
                },
            },
        }
    ]
    }, function (chartObj) {
        let max = chartObj.series[0].data[0].y;
        let point = chartObj.series[1].data[0];

        max = parseFloat(max.toFixed(1));
        y = parseFloat(point.y.toFixed(1));

        if (y <= max) {
            color = 'hsl(0, 100%, 80%)';
        }
        else {
            color = '#28a745';
        }

        point.color = color;
        point.graphic.attr({ fill: color });
    });
};
