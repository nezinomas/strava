loadChart("chart-year-data", "chart-year-container");

function loadChart(idData, idContainer) {
    const chartData = JSON.parse(document.getElementById(idData).textContent);

    Highcharts.chart(idContainer, {
        chart: {
            type: "bullet"
        },
        title: {
            text: "",
        },
        xAxis: {
            categories: chartData.categories,
            gridLineWidth: 0,
        },
        yAxis: {
            title: {
                text: ""
            },
        },
        plotOptions: {
            series: {
                enableMouseTracking: false,
                targetOptions: {
                    borderWidth: 0,
                    height: 2,
                    color: "black",
                    width: "110%"
                }
            },
        },
        series: [{
            data: chartData.fact,
            // color: `rgba(${chartData.chart_column_color}, 0.65)`,
            // borderColor: `rgba(${chartData.chart_column_color}, 1)`,
            borderRadius: 0,
            dataLabels: [{
                enabled: true,
                // color: `rgba(${chartData.chart_column_color}, 1)`,
                style: {
                    fontSize: "11px",
                    fontWeight: "bold",
                    textOutline: false
                },
                formatter: function() {
                    console.log(this.x);
                    let goal = chartData.css_class[this.x];
                    console.log(goal);
                    let color = "blue";
                    if (goal == "goal_fail") {
                        color = "#EB5353";
                    }
                    if (goal == "goal_success") {
                        color = "#5D9C59";
                    }
                    return '<span style="color: ' + color + '">' + this.y + ' </span>';   
                },
            }]
        }, {
            type: "column",
            borderWidth: 0,
            data: chartData.targets,
            color: "rgba(0,0,0,0)",
            dataLabels: [{
                enabled: true,
                color: "black",
                align: "left",
                x: -30,
                y: -13,
                verticalAlign: "top",
                style: {
                    fontSize: "11px",
                    fontWeight: "bold",
                    textOutline: false
                }
            }]
        }]
    }, function (chartObj) {
        /* align datalabels for expenses that exceeds targets */
        // $.each(chartObj.series[1].data, function (i, point) {
            // let max = chartObj.series[0].data[point.x].y;
            // let {y} = point;

            // max = parseFloat(max.toFixed(1));
            // y = parseFloat(y.toFixed(1));

            // if (y <= max) {
            //     color = "#5D9C59";
            // }
            // else {
            //     p = 28;
            //     if (y < 100) { p = 21; }
            //     if (y < 10) { p = -2; }
            //     point.dataLabel.attr({ x: point.dataLabel.x + p });

            //     color = (y <= max * 1.1) ? "#FEB56A" : "#EB5353";
            // }
            // point.color = color;
            // point.graphic.attr({ fill: color });
        // });
        let arr = chartObj.series[0].data;
        arr.forEach((point, i, array) => {
            let css_class = chartData.css_class[i];
            // console.log(i, css_class);
            if (css_class == "goal_fail") {
                point.graphic.attr({ fill: "#EB5353" });
                // point.update({color: '#434348'})

            }

            if (css_class == "goal_success") {
                point.graphic.attr({ fill: "#5D9C59" });
            }
        });

        console.log(numbers);
    });
};