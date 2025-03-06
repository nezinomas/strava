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
                    width: "105%"
                }
            },
        },
        series: [{
            data: chartData.fact,
            opacity: 0.85,
            borderRadius: 0,
            dataLabels: [{
                enabled: true,
                style: {
                    fontSize: "11px",
                    fontWeight: "bold",
                    textOutline: false
                },
                formatter: function() {
                    let goal = chartData.css_class[this.x];
                    let color = "#000000";

                    if (goal == "goal_fail") {
                        color = "#c60202";
                    }
                    if (goal == "goal_success") {
                        color = "#5D9C59";
                    }

                    if(chartData.collected[this.x] > 0) {
                        return `<span style="color: ${color}">${Highcharts.numberFormat(this.y, 0)}</span>`;
                    }
                    return "";
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
                x: -27,
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
        let arr = chartObj.series[0].data;
        arr.forEach((point, i, array) => {
            let css_class = chartData.css_class[i];

            if (css_class == "goal_fail") {
                point.graphic.attr({ fill: "#EB5353" });
                point.dataLabel.attr({ y: point.dataLabel.y + 25 });

            }

            if (css_class == "goal_success") {
                point.graphic.attr({ fill: "#5D9C59" });
            }
        });
    });
};