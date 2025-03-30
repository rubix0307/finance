var config_pie = {
    selectedCurrency: "USD",
    categories: [
        {
            label: "продукты",
            backgroundColor: "rgba(255, 99, 132, 0.6)",
            borderColor: "rgba(255, 99, 132, 1)",
            date: "2025-03-24",
            currency: "USD",
            value: 120,
            currencies: [{currency: "EUR", value: 50}, {currency: "UAH", value: 489}]
        },
        {
            label: "электроника",
            backgroundColor: "rgba(54, 162, 235, 0.6)",
            borderColor: "rgba(54, 162, 235, 1)",
            date: "2025-03-24",
            currency: "USD",
            value: 200,
            currencies: [{currency: "EUR", value: 60}, {currency: "UAH", value: 420}]
        },
        {
            label: "уход за собой",
            backgroundColor: "rgba(255, 206, 86, 0.6)",
            borderColor: "rgba(255, 206, 86, 1)",
            date: "2025-03-24",
            currency: "USD",
            value: 90,
            currencies: [{currency: "EUR", value: 30}, {currency: "UAH", value: 450}]
        },
        {
            label: "алкоголь",
            backgroundColor: "rgba(75, 192, 192, 0.6)",
            borderColor: "rgba(75, 192, 192, 1)",
            date: "2025-03-24",
            currency: "USD",
            value: 55.9,
            currencies: [{currency: "EUR", value: 40}, {currency: "UAH", value: 250}]
        }
    ]
};


var config_stacked_bar = {
    selectedCurrency: "USD",
    timeData: [
        {
            date: "03.20.2024",
            categories: [
                {
                    label: "алкоголь",
                    value: 65.72,
                    currency: "USD",
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    currencies: [{currency: "EUR", value: 40}, {currency: "UAH", value: 250}]
                },
                {
                    label: "продукты",
                    value: 100,
                    currency: "USD",
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    currencies: [{currency: "USD", value: 100}]
                }
            ]
        },
        {
            date: "03.21.2024",
            categories: [
                {
                    label: "алкоголь",
                    value: 12,
                    currency: "USD",
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    currencies: [{currency: "EUR", value: 12}]
                },
                {
                    label: "продукты",
                    value: 120,
                    currency: "USD",
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    currencies: [{currency: "USD", value: 120}]
                },
                {
                    label: "электроника",
                    value: 210,
                    currency: "USD",
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    currencies: [{currency: "USD", value: 210}]
                },
                {
                    label: "новая категория",
                    value: 75,
                    currency: "USD",
                    backgroundColor: "rgba(200, 150, 50, 0.6)",
                    borderColor: "rgba(200, 150, 50, 1)",
                    currencies: [{currency: "USD", value: 75}]
                }
            ]
        },
        {
            date: "03.22.2024",
            categories: [
                {
                    label: "электроника",
                    value: 180,
                    currency: "USD",
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    currencies: [{currency: "USD", value: 180}]
                },
                {
                    label: "уход за собой",
                    value: 95,
                    currency: "USD",
                    backgroundColor: "rgba(255, 206, 86, 0.6)",
                    borderColor: "rgba(255, 206, 86, 1)",
                    currencies: [{currency: "USD", value: 95}]
                },
                {
                    label: "продукты",
                    value: 130,
                    currency: "USD",
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    currencies: [{currency: "USD", value: 130}]
                }
            ]
        }
    ]
};


class ChartManager {
    constructor(canvasId, legendId) {
        this.canvas = document.getElementById(canvasId);
        this.legendContainer = document.getElementById(legendId);
        this.ctx = this.canvas.getContext("2d");
        this.chart = null;
        this.currentMode = "pie";
        this.globalVisibility = {};
        this.originalStackedData = {};
        this.currentConfig = null;
        this.currentTooltipContent = "";
    }

    updateChartData() {
        if (this.currentMode === "pie") {
            const newData = config_pie.categories.map(cat =>
                this.globalVisibility[cat.label] ? cat.value : 0
            );
            this.chart.data.datasets[0].data = newData;
        } else if (this.currentMode === "stackedBar") {
            this.chart.data.datasets.forEach(dataset => {
                const orig = this.originalStackedData[dataset.label];
                dataset.data = orig.map(val =>
                    this.globalVisibility[dataset.label] ? val : 0
                );
            });
        }
        this.chart.update();
    }

    updateLegend() {
        this.legendContainer.innerHTML = '';
        let legendItems = [];
        if (this.currentMode === "pie") {
            legendItems = config_pie.categories.map(cat => cat.label);
        } else if (this.currentMode === "stackedBar") {
            let set = new Set();
            config_stacked_bar.timeData.forEach(day => {
                day.categories.forEach(cat => set.add(cat.label));
            });
            legendItems = Array.from(set);
        }
        legendItems.forEach(label => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = label;
            let bg = 'rgba(0,0,0,0.3)', bc = 'rgba(0,0,0,1)';
            if (this.currentMode === "pie") {
                const cat = config_pie.categories.find(c => c.label === label);
                if (cat) {
                    bg = cat.backgroundColor;
                    bc = cat.borderColor;
                }
            } else if (this.currentMode === "stackedBar") {
                for (let day of config_stacked_bar.timeData) {
                    const cat = day.categories.find(c => c.label === label);
                    if (cat) {
                        bg = cat.backgroundColor;
                        bc = cat.borderColor;
                        break;
                    }
                }
            }
            legendItem.style.backgroundColor = bg;
            legendItem.style.borderColor = bc;
            legendItem.style.opacity = this.globalVisibility[label] ? 1 : 0.5;
            legendItem.addEventListener('click', () => {
                this.globalVisibility[label] = !this.globalVisibility[label];
                this.updateChartData();
                this.updateLegend();
            });
            this.legendContainer.appendChild(legendItem);
        });
    }

    customTooltip(tooltipModel) {
        let tooltipEl = document.getElementById('chartjs-tooltip');
        if (!tooltipEl) {
            tooltipEl = document.createElement('div');
            tooltipEl.id = 'chartjs-tooltip';
            document.body.appendChild(tooltipEl);
        }
        if (tooltipModel.opacity === 0) {
            tooltipEl.style.opacity = 0;
            return;
        }
        let innerHtml = "";
        if (tooltipModel.dataPoints) {
            const dp = tooltipModel.dataPoints[0];
            if (this.currentMode === "pie") {
                const cat = this.currentConfig.categories[dp.index];
                const breakdown = cat.currencies
                    .map(item => item.currency + ': ' + item.value)
                    .join(', ');
                innerHtml += "<div><strong>" + cat.label + "</strong></div>";
                innerHtml += "<div>Всего: " + cat.value + " " + cat.currency + "</div>";
                innerHtml += "<div>Валюты: " + breakdown + "</div>";
                innerHtml += "<div>" + cat.date + "</div>";
            } else if (this.currentMode === "stackedBar") {
                const day = this.currentConfig.timeData[dp.index];
                const categoryLabel = this.chart.data.datasets[dp.datasetIndex].label;
                const catData = day.categories.find(c => c.label === categoryLabel);
                if (catData) {
                    const breakdown = catData.currencies
                        .map(item => item.currency + ': ' + item.value)
                        .join(', ');
                    innerHtml += "<div><strong>" + catData.label + "</strong></div>";
                    innerHtml += "<div>Всего: " + catData.value + " " + catData.currency + "</div>";
                    innerHtml += "<div>Валюты: " + breakdown + "</div>";
                    innerHtml += "<div>" + day.date + "</div>";
                } else {
                    innerHtml += "<div>No data for " + categoryLabel + "</div>";
                }
            }
        }
        tooltipEl.innerHTML = innerHtml;
        this.currentTooltipContent = innerHtml;
        const canvasRect = this.canvas.getBoundingClientRect();
        const tooltipX = canvasRect.left + window.pageXOffset + tooltipModel.caretX;
        const tooltipY = canvasRect.top + window.pageYOffset + tooltipModel.caretY;
        tooltipEl.style.opacity = 1;
        tooltipEl.style.position = 'absolute';
        tooltipEl.style.left = tooltipX + 'px';
        tooltipEl.style.top = tooltipY + 'px';
        tooltipEl.style.fontFamily = tooltipModel._bodyFontFamily;
        tooltipEl.style.fontSize = tooltipModel.bodyFontSize + 'px';
        tooltipEl.style.fontStyle = tooltipModel._bodyFontStyle;
        tooltipEl.style.padding = tooltipModel.yPadding + 'px ' + tooltipModel.xPadding + 'px';
        tooltipEl.style.pointerEvents = 'none';
    }


    attachClickHandler() {
        this.canvas.onclick = (evt) => {
            setTimeout(() => {
                document.getElementById("chart_info").innerHTML = this.currentTooltipContent || "";
            }, 0);
        };
    }

    initPieChart(configPie) {
        this.currentMode = "pie";
        this.currentConfig = configPie;
        configPie.categories.forEach(cat => {
            if (!(cat.label in this.globalVisibility)) {
                this.globalVisibility[cat.label] = true;
            }
        });
        const chartData = {
            type: "pie",
            data: {
                labels: configPie.categories.map(cat => cat.label),
                datasets: [{
                    data: configPie.categories.map(cat => this.globalVisibility[cat.label] ? cat.value : 0),
                    backgroundColor: configPie.categories.map(cat => cat.backgroundColor),
                    borderColor: configPie.categories.map(cat => cat.borderColor),
                    borderWidth: 1,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                legend: {display: false},
                tooltips: {
                    enabled: false,
                    custom: this.customTooltip.bind(this)
                }
            }
        };
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.ctx, chartData);
        this.updateLegend();
        this.attachClickHandler();
    }

    initStackedBarChart(configStacked) {
        this.currentMode = "stackedBar";
        this.currentConfig = configStacked;
        let set = new Set();
        configStacked.timeData.forEach(day => {
            day.categories.forEach(cat => set.add(cat.label));
        });
        Array.from(set).forEach(label => {
            if (!(label in this.globalVisibility)) {
                this.globalVisibility[label] = true;
            }
        });
        let dates = configStacked.timeData.map(item => item.date);
        let categoryLabels = Array.from(set);
        let datasets = categoryLabels.map(label => {
            let found = null;
            let dataArr = [];
            configStacked.timeData.forEach(day => {
                let cat = day.categories.find(c => c.label === label);
                if (cat) {
                    dataArr.push(cat.value);
                    if (!found) {
                        found = cat;
                    }
                } else {
                    dataArr.push(0);
                }
            });
            this.originalStackedData[label] = dataArr.slice();
            return {
                label: label,
                data: dataArr.map(val => this.globalVisibility[label] ? val : 0),
                backgroundColor: found ? found.backgroundColor : 'rgba(0,0,0,0.3)',
                borderColor: found ? found.borderColor : 'rgba(0,0,0,1)',
                borderWidth: 1
            };
        });
        const chartData = {
            type: "bar",
            data: {
                labels: dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                legend: {display: false},
                scales: {
                    xAxes: [{
                        stacked: true,
                        categoryPercentage: 1.0,
                        barPercentage: 0.9,
                        ticks: {autoSkip: false}
                    }],
                    yAxes: [{
                        stacked: true
                    }]
                },
                tooltips: {
                    enabled: false,
                    custom: this.customTooltip.bind(this)
                }
            }
        };
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.ctx, chartData);
        this.updateLegend();
        this.attachClickHandler();
    }
}

const manager = new ChartManager("myChart", "chart_legend");
manager.initPieChart(config_pie);

document.getElementById("toggleMode").addEventListener("click", function () {
    if (manager.currentMode === "pie") {
        manager.initStackedBarChart(config_stacked_bar);
    } else {
        manager.initPieChart(config_pie);
    }
});
