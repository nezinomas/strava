Highcharts.theme = {
    colors: [
        "#006432", // Ekspla Dark Green
        "#19af23", // Ekspla Vibrant Green
        "#475569", // Slate 600
        "#64748b", // Slate 500
        "#94a3b8", // Slate 400
        "#cbd5e1"  // Slate 300
    ],
    chart: {
        backgroundColor: null,
        style: {
            fontFamily: "'Inter', -apple-system, sans-serif"
        }
    },
    title: {
        verticalAlign: "top",
        style: {
            fontFamily: "'Outfit', sans-serif",
            fontSize: "16px",
            fontWeight: "600",
            color: "#1e293b",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
        }
    },
    xAxis: {
        lineColor: "#cbd5e1",
        lineWidth: 1,
        gridLineColor: "#f1f5f9",
        gridLineWidth: 1,
        labels: {
            style: {
                fontFamily: "'Inter', sans-serif",
                fontSize: "10px",
                color: "#64748b"
            }
        }
    },
    yAxis: {
        gridLineColor: "#e2e8f0",
        title: {
            style: {
                fontFamily: "'Outfit', sans-serif",
                color: "#64748b",
                textTransform: "uppercase",
                letterSpacing: "0.05em"
            }
        },
        labels: {
            style: {
                fontFamily: "'Inter', sans-serif",
                fontSize: "10px",
                color: "#64748b"
            }
        },
        minorTicks: false
    },
    legend: {
        enabled: false,
        layout: "horizontal",
        align: "right",
        verticalAlign: "top",
        floating: true,
        borderWidth: 0,
        backgroundColor: "transparent",
        itemStyle: {
            fontFamily: "'Inter', sans-serif",
            fontWeight: "600",
            fontSize: "12px",
            color: "#1e293b"
        }
    },
    credits: {
        enabled: false
    },
    tooltip: {
        shadow: true,
        useHTML: true,
        backgroundColor: "#ffffff",
        borderWidth: 1,
        borderColor: "#e2e8f0",
        borderRadius: 8,
        style: {
            fontFamily: "'Inter', sans-serif",
            fontSize: "12px",
            color: "#1e293b"
        }
    },
    plotOptions: {
        candlestick: {
            lineColor: "#475569"
        },
        series: {
            dataLabels: {
                style: {
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '11px',
                    fontWeight: '600',
                    textOutline: 'none',
                    color: '#1e293b'
                }
            }
        }
    }
};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);
