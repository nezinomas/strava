function loadChart(idData, idContainer) {
    const chartData = JSON.parse(document.getElementById(idData).textContent);

    Highcharts.chart(idContainer, {
        chart: {
            type: 'bar',
            // height: 85,
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
            pointFormat: '{series.name}: <b>{point.y:.1f}</b><br/>',
        },
        series: [{
            name: chartData.targetTitle,
            type: 'bar',
            color: 'rgba(0,0,0,0.07)',
            data: chartData.target,
            pointWidth: 19,
            dataLabels: {
                enabled: true,
                color: '#000',
                x: -2,
                y: -15,
                overflow: 'none',
                crop: false,
                format: '{point.y:.0f}',
                style: {
                    fontSize: '9px',
                    fontWeight: 'bold',
                    textOutline: false
                }
            }
        }, {
            name: chartData.factTitle,
            type: 'bullet',
            data: chartData.fact,
            pointWidth: 13,
            borderRadius: 0,
            targetOptions: {
                borderWidth: 2,
                borderColor: 'red',
                height: 2,
                color: '#000',
                width: '200%'
            },
            dataLabels: {
                format: '{point.y:.0f}',
                enabled: true,
                color: '#000',
                align: 'right',
                y: -1,
                style: {
                    fontWeight: 'bold',
                    textOutline: false,
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
            color = 'rgb(254, 83, 106)';
        }
        else {
            color = '#28a745';
        }

        point.color = color;
        point.graphic.attr({ fill: color });
    });
};
