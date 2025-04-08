function waitForAppData() {
    try {
        const appData = Alpine.store('appData');
        if (appData && appData.current_section && appData.current_section.id) {
            Alpine.store('charts').initPieChartAndWatch();
        } else {
            setTimeout(waitForAppData, 100);
        }
    } catch (e) {
        setTimeout(waitForAppData, 100);
    }
}

document.addEventListener('alpine:init', () => {
    Alpine.store('charts', {
        currentRenderer: null,
        prevSectionId: null,
        currentPeriod: '',
        currentChartType: 'pie',
        periods: [
            {label: 'Неделя', value: 'week'},
            {label: 'Месяц', value: 'month'},
            {label: 'Год', value: 'year'}
        ],
        expensesData: {},
        currency: {},
        cache: {},
        setPeriod(newPeriod) {
            this.initPieChartAndWatch(newPeriod);
        },
        async fetchGraphData(sectionId, chartType, period) {
            const key = `${sectionId}-${chartType}-${period}`;
            if (this.cache[key]) return this.cache[key];
            const url = `/api/sections/${sectionId}/expenses/?period=${period}&chart_type=${chartType}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Network error: ${response.status}`);
            const rawData = await response.json();
            this.cache[key] = rawData;
            return rawData;
        },
        async initPieChartAndWatch(newPeriod) {
            const sectionId = Alpine.store('appData').current_section.id;
            const period = newPeriod || this.currentPeriod || 'week';
            const rawData = await this.fetchGraphData(sectionId, this.currentChartType, period);
            if (rawData && rawData.period) {
                this.currentPeriod = rawData.period;
            }
            if (rawData && rawData.expenses_data) {
                this.expensesData = rawData.expenses_data;
            }
            if (rawData && rawData.currency) {
                this.currency = rawData.currency;
            }
            const canvas = document.getElementById("mainChart");
            if (this.currentRenderer) {
                await this.currentRenderer.updateDataFromCache(rawData);
            } else {
                this.currentRenderer = new this.PieChartRenderer(canvas.id, '');
                await this.currentRenderer.updateDataFromCache(rawData);
            }
            this.prevSectionId = sectionId;
            Alpine.effect(() => {
                const cs = Alpine.store('appData').current_section;
                if (cs && cs.id && cs.id !== this.prevSectionId) {
                    this.prevSectionId = cs.id;
                    this.fetchGraphData(cs.id, this.currentChartType, this.currentPeriod)
                        .then(data => {
                            this.currentRenderer.updateDataFromCache(data);
                        })
                        .catch(e => console.error(e));
                }
            });
        },
        PieChartRenderer: class {
            constructor(canvasId, dataUrl) {
                this.canvasId = canvasId;
                this.dataUrl = dataUrl;
                this.rawData = {};
                this.segmentObjects = [];
                this.chartInstance = null;
                this.canvas = null;
            }

            async init() {
                await this.fetchData();
                this.prepareSegments();
                const config = this.generateConfig();
                this.render(config);
                this.renderCustomLegend();
            }

            async updateDataFromCache(rawData) {
                this.rawData = rawData;
                if (rawData && rawData.expenses_data) {
                    Alpine.store('charts').expensesData = rawData.expenses_data;
                }
                if (rawData && rawData.currency) {
                    Alpine.store('charts').currency = rawData.currency;
                }
                this.prepareSegments();
                const config = this.generateConfig();
                if (!this.canvas) {
                    this.canvas = document.getElementById(this.canvasId);
                }
                if (!this.canvas) {
                    console.error(`Canvas element with id ${this.canvasId} not found`);
                    return;
                }
                const ctx = this.canvas.getContext('2d');
                if (this.chartInstance) {
                    this.chartInstance.data.labels = config.data.labels;
                    this.chartInstance.data.datasets[0].data = config.data.datasets[0].data;
                    this.chartInstance.data.datasets[0].backgroundColor = config.data.datasets[0].backgroundColor;
                    this.chartInstance.options.title.text = config.options.title.text;
                    this.chartInstance.update();
                } else {
                    this.chartInstance = new Chart(ctx, config);
                }
                this.renderCustomLegend();
            }

            async fetchData() {
                try {
                    const response = await fetch(this.dataUrl);
                    if (!response.ok) throw new Error(`Network error: ${response.status}`);
                    this.rawData = await response.json();
                    if (this.rawData && this.rawData.period) {
                        Alpine.store('charts').currentPeriod = this.rawData.period;
                    }
                    if (this.rawData && this.rawData.expenses_data) {
                        Alpine.store('charts').expensesData = this.rawData.expenses_data;
                    }
                    if (this.rawData && this.rawData.currency) {
                        Alpine.store('charts').currency = this.rawData.currency;
                    }
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
            }

            prepareSegments() {
                this.segmentObjects = this.rawData.chart_data.data.data.map(item => ({
                    id: item.category_id,
                    name: item.category_name,
                    value: item.value,
                    currencies: item.currencies,
                    backgroundColor: item.category_color || this.getRandomColor()
                }));
            }

            getRandomColor() {
                const r = Math.floor(Math.random() * 256);
                const g = Math.floor(Math.random() * 256);
                const b = Math.floor(Math.random() * 256);
                return `rgba(${r}, ${g}, ${b}, 0.6)`;
            }

            generateConfig() {
                return {
                    type: 'pie',
                    data: {
                        labels: this.segmentObjects.map(s => s.name),
                        datasets: [{
                            data: this.segmentObjects.map(s => s.value),
                            backgroundColor: this.segmentObjects.map(s => s.backgroundColor),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        devicePixelRatio: window.devicePixelRatio,
                        legend: {display: false},
                        title: {
                            display: !!this.rawData.chart_data.data.chart_title,
                            text: this.rawData.chart_data.data.chart_title,
                        },
                        tooltips: {
                            enabled: false,
                            custom: this.customTooltip.bind(this)
                        }
                    }
                };
            }

            render(config) {
                this.canvas = document.getElementById(this.canvasId);
                const ctx = this.canvas.getContext('2d');
                if (this.chartInstance) this.chartInstance.destroy();
                this.chartInstance = new Chart(ctx, config);
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
                    const cat = this.segmentObjects[dp.index];
                    const breakdown = Object.keys(cat.currencies)
                        .map(currency => {
                            const curr = cat.currencies[currency];
                            return currency + ': ' + curr.original;
                        })
                        .join(', ');
                    innerHtml += "<div><strong>" + cat.name + "</strong></div>";
                    innerHtml += "<div>Всего: " + cat.value + "</div>";
                    innerHtml += "<div>Валюты: " + breakdown + "</div>";
                }
                tooltipEl.innerHTML = innerHtml;
                const canvasRect = this.canvas.getBoundingClientRect();
                const tooltipX = canvasRect.left + window.pageXOffset + tooltipModel.caretX;
                const tooltipY = canvasRect.top + window.pageYOffset + tooltipModel.caretY;
                tooltipEl.style.opacity = 1;
                tooltipEl.style.position = 'absolute';
                tooltipEl.style.left = tooltipX + 'px';
                tooltipEl.style.top = tooltipY + 'px';
                tooltipEl.style.fontFamily = tooltipModel.bodyFontFamily;
                tooltipEl.style.fontSize = tooltipModel.bodyFontSize + 'px';
                tooltipEl.style.fontStyle = tooltipModel.bodyFontStyle;
                tooltipEl.style.padding = tooltipModel.yPadding + 'px ' + tooltipModel.xPadding + 'px';
            }

            renderCustomLegend() {
                const legendContainer = document.getElementById("chartLegend");
                legendContainer.innerHTML = '';
                const meta = this.chartInstance.getDatasetMeta(0);
                this.segmentObjects.forEach((segment, index) => {
                    const item = document.createElement("div");
                    item.classList.add("legend-item");
                    if (meta.data[index] && meta.data[index].hidden) item.classList.add("disabled");
                    const colorBox = document.createElement("div");
                    colorBox.classList.add("legend-color-box");
                    colorBox.style.background = segment.backgroundColor;
                    colorBox.style.width = "16px";
                    colorBox.style.height = "16px";
                    colorBox.style.marginRight = "8px";
                    const label = document.createElement("span");
                    label.innerText = `${segment.name}`;
                    item.appendChild(colorBox);
                    item.appendChild(label);
                    item.addEventListener('click', () => {
                        const meta = this.chartInstance.getDatasetMeta(0);
                        const element = meta.data[index];
                        if (element) {
                            element.hidden = !element.hidden;
                            this.chartInstance.update();
                            this.renderCustomLegend();
                        }
                    });
                    legendContainer.appendChild(item);
                });
            }
        }
    });
});

document.addEventListener('alpine:init', () => {
    waitForAppData();
});