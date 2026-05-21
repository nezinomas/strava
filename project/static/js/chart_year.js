loadChart("chart-year-data", "chart-year-container");

function loadChart(idData, idContainer) {
    const chartData = JSON.parse(document.getElementById(idData).textContent);

    let fail_col_color = "#fb7185";  // Modern soft rose-400
    let fail_txt_color = "#e11d48";  // Rose-600
    let success_col_color = "#19af23"; // Ekspla vibrant green
    let success_txt_color = "#006432"; // Ekspla dark green

    Highcharts.chart(idContainer, {
        chart: {
            type: "bullet",
            style: {
                fontFamily: "'Inter', sans-serif"
            }
        },
        title: {
            text: "",
        },
        xAxis: {
            categories: chartData.categories,
            gridLineWidth: 0,
            labels: {
                style: {
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "11px",
                    color: "#64748b"
                }
            }
        },
        yAxis: {
            title: {
                text: ""
            },
            gridLineColor: "#e2e8f0"
        },
        plotOptions: {
            series: {
                enableMouseTracking: false,
                targetOptions: {
                    borderWidth: 0,
                    height: 2,
                    color: "#64748b",
                    width: "105%"
                }
            },
        },
        series: [{
            data: chartData.fact,
            opacity: 0.85,
            borderRadius: 4,
            dataLabels: [{
                enabled: true,
                crop: false,
                overflow: "allow",
                style: {
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "11px",
                    fontWeight: "600",
                    textOutline: "none"
                },
                formatter: function() {
                    let goal = chartData.css_class[this.x];
                    let color = "#1e293b";

                    if (goal == "goal_fail") {
                        color = fail_txt_color;
                    }
                    if (goal == "goal_success") {
                        color = success_txt_color;
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
                color: "#64748b",
                align: "left",
                x: -27,
                y: -13,
                verticalAlign: "top",
                style: {
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "11px",
                    fontWeight: "600",
                    textOutline: "none"
                }
            }]
        }]
    }, function (chartObj) {
        let arr = chartObj.series[0].data;
        arr.forEach((point, i, array) => {
            let css_class = chartData.css_class[i];

            if (css_class == "goal_fail") {
                point.graphic.attr({ fill: fail_col_color });
                point.dataLabel.attr({ y: point.dataLabel.y + 25 });
            }

            if (css_class == "goal_success") {
                point.graphic.attr({ fill: success_col_color });
            }
        });
    });
}