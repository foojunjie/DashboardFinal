<template>
  <div class="dashboard">
    <!-- Title Section -->
    <div class="dashboard-title">
      <h1>OUTPUT STATUS (SUMMARY WEEKLY AND MONTHLY OUTPUT UPDATE)</h1>
      <div class="title-controls">
        <select class="title-dropdown" v-model="selectedPart" @change="onPartChange">
          <option v-for="p in productList" :key="p.customer_part_num" :value="p.customer_part_num">
            {{ p.customer_part_num }}
          </option>
        </select>
        <input type="date" class="date-picker" v-model="selectedDate" @change="onDateChange" />
      </div>
    </div>
    
    <!-- Charts Container -->
    <div class="charts-container">
      <!-- Left Side - Pie Chart -->
      <div class="pie-container">
        <div class="pie-box">
          <div class="pie-title">On Time Delivery</div>
          <div class="pie-content">
            <div ref="pieChart" class="chart"></div>
          </div>
        </div>
      </div>
      
      <!-- Right Side - Meter Charts -->
      <div class="meters-container">
        <div class="meter-box">
          <div class="meter-title">Weekly CO%</div>
          <div class="meter-content">
            <div ref="weeklyMeter" class="chart"></div>
          </div>
        </div>
        <div class="meter-box">
          <div class="meter-title">Monthly CO%</div>
          <div class="meter-content">
            <div ref="monthlyMeter" class="chart"></div>
          </div>
        </div>
        <div class="meter-box">
          <div class="meter-title">Monthly Production%</div>
          <div class="meter-content">
            <div ref="productionMeter" class="chart"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bottom - Line Bar Chart -->
    <div class="bottom-chart">
      <div class="linebar-box">
        <div class="linebar-header">
          <div class="linebar-title">Production Output by Workcell</div>

          <div class="linebar-buttons">
            <button class="switch-btn" @click="showMonthlyFake">Monthly</button>
            <button class="switch-btn" @click="showDailyLive">DailyLive</button>
            <button class="switch-btn" @click="showWeeklyLive">WeeklyLive</button>
            <button class="switch-btn" @click="showMonthlyLive">MonthlyLive</button>
          </div>
        </div>
        <div ref="lineBarChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'MainDashboard',
  data() {
    const localDate = new Date();
    // Adjusts for timezone offset to get the correct local YYYY-MM-DD
    const todayISO = new Date(localDate.getTime() - (localDate.getTimezoneOffset() * 60000))
                    .toISOString().split('T')[0];
    return {
      selectedDate: todayISO,
      productList: [],
      selectedPart: null,
      productionResult: null,
      deliverResult: null,
      target: null,
      weeklyCO: 0,
      weeklyProduction: 0,
      monthlyCO: 0,
      monthlyProduction: 0,
      pieChart: null,
      weeklyMeter: null,
      monthlyMeter: null,
      productionMeter: null,
      lineBarChart: null,
      refreshInterval: null,
      activeMode: 'monthlyFake',  // default mode
    }
  },
  async mounted() {
    this.initPieChart()
    this.initWeeklyMeter()
    this.initMonthlyMeter()
    this.initProductionMeter()
    this.initLineBarChart()

    await this.loadPartDropdown()

    if (this.productList.length > 0 && !this.selectedPart) {
      this.selectedPart = this.productList[0].customer_part_num
      await this.loadSummaryCO(this.selectedPart)
    }
    
    // Handle resize
    window.addEventListener('resize', this.handleResize)

    this.refreshInterval = setInterval(() => {
      // 1. Calculate what "Today" actually is right now
      const now = new Date();
      const actualToday = new Date(now.getTime() - (now.getTimezoneOffset() * 60000))
                            .toISOString().split('T')[0];

      // 2. Check is it Today
      if (this.selectedDate >= actualToday || this.isShowingCurrentDate(actualToday)) {
          this.selectedDate = actualToday;
      }

      // 3. Proceed with the refresh
      this.loadSummaryCO(this.selectedPart);

      const modeMap = {
        'weekly': this.showWeeklyLive,
        'monthly': this.showMonthlyLive,
        'daily': this.showDailyLive,
        'monthlyFake': this.showMonthlyFake
      };
      
      if (modeMap[this.activeMode]) {
        modeMap[this.activeMode]();
      }
    }, 300000);
  },

  beforeUnmount() {
    // Clean up
    window.removeEventListener('resize', this.handleResize)
    clearInterval(this.refreshInterval) // Stop auto-refresh
    this.pieChart?.dispose()
    this.weeklyMeter?.dispose()
    this.monthlyMeter?.dispose()
    this.productionMeter?.dispose()
    this.lineBarChart?.dispose()
  },
  methods: {
    handleResize() {
      this.pieChart?.resize()
      this.weeklyMeter?.resize()
      this.monthlyMeter?.resize()
      this.productionMeter?.resize()
      this.lineBarChart?.resize()
    },

    isShowingCurrentDate(actualToday) {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayISO = yesterday.toISOString().split('T')[0];
      
      return this.selectedDate === actualToday || this.selectedDate === yesterdayISO;
    },

    async onDateChange() {
      const oldPart = this.selectedPart

      await this.loadPartDropdown()

      // keep part if still exists for new date
      const stillExists = this.productList.some(
        p => p.customer_part_num === oldPart
      )

      if (stillExists) {
        this.selectedPart = oldPart
        await this.loadSummaryCO(this.selectedPart)
      } else if (this.productList.length > 0) {
        this.selectedPart = this.productList[0].customer_part_num
        await this.loadSummaryCO(this.selectedPart)
      } else {
        this.selectedPart = null
      }

      if (this.activeMode === 'daily') {
        await this.showDailyLive()
      } else if (this.activeMode === 'weekly') {
        await this.showWeeklyLive()
      } else if (this.activeMode === 'monthly') {
        await this.showMonthlyLive()
      } else if (this.activeMode === 'monthlyFake') {
        this.showMonthlyFake()
      }
    },

    async onPartChange() {
      if (!this.selectedPart) return
      await this.loadSummaryCO(this.selectedPart)
    },

    async loadPartDropdown() {
      this.$emit('api-loading', true)
      try {
        const queryDate = this.selectedDate ? `?date=${this.selectedDate}` : ''
        const res = await fetch(`http://127.0.0.1:8000/api/summaryCO${queryDate}`)
        if (!res.ok) throw new Error(`API error: ${res.status}`)
        const data = await res.json()
        this.productList = data.productList || []
      } catch (error) {
        console.error('Error loading parts:', error)
        this.productList = []
      } finally {
        this.$emit('api-loading', false)
      }
    },

    async sendSelectedPart() {
      // Reuse loadSummaryCO to maintain consistent parsing and chart updates
      try {
        await this.loadSummaryCO(this.selectedPart)
      } catch (err) {
        console.error('Error loading summary for part:', err)
      }
    },

    async loadSummaryCO(selectedPart) {
      this.$emit('api-loading', true)
      try {
        const queryDate = this.selectedDate ? `&date=${this.selectedDate}` : '';
        const res = await fetch(`http://127.0.0.1:8000/api/summaryCO?partNumber=${selectedPart}${queryDate}`);
        if (!res.ok) throw new Error(`API error: ${res.status}`)
        const data = await res.json();

        // Keep the raw arrays/objects so we can handle multiple shapes
        this.productionResult = data.productionResult;
        this.deliverResult = data.deliverResult;
        this.target = data.target && (Array.isArray(data.target) ? data.target[0] : data.target);
        this.monthlyCO = Array.isArray(data.monthlyCO) ? data.monthlyCO[0] : data.monthlyCO;
        this.monthlyProduction = Array.isArray(data.monthlyProduction) ? data.monthlyProduction[0] : data.monthlyProduction;
        this.weeklyCO = data.weeklyCO ? (Array.isArray(data.weeklyCO) ? data.weeklyCO[0] : data.weeklyCO) : 0;

        this.initPieChart();  // <-- update chart when data updates
        this.initMonthlyMeter()
        this.initWeeklyMeter()
        this.initProductionMeter()
        
        this.$emit('api-connected', true)
      } catch (error) {
        console.error('Error loading summary CO:', error)
        this.$emit('api-error', `Failed to load data: ${error.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    initPieChart() {
        // normalize production/delivery/target shapes (support arrays, objects, or numbers)
        if (!this.productionResult || !this.deliverResult || (this.target === null || this.target === undefined)) return;

        let onTimeProduce = 0, lateProduce = 0, onTimeDeliver = 0, lateDeliver = 0;
        // productionResult can be: array [onTime, late], object {OnTimeProduce, LateProduce} or number
        if (Array.isArray(this.productionResult)) {
          onTimeProduce = Number(this.productionResult[0]) || 0;
          lateProduce = Number(this.productionResult[1]) || 0;
        } else if (typeof this.productionResult === 'object' && this.productionResult !== null) {
          onTimeProduce = Number(this.productionResult.OnTimeProduce ?? this.productionResult.onTimeProduce) || 0;
          lateProduce = Number(this.productionResult.LateProduce ?? this.productionResult.lateProduce) || 0;
        } else {
          onTimeProduce = Number(this.productionResult) || 0;
          lateProduce = 0;
        }

        // deliverResult can be: array [onTime, late], object {OnTimeDeliver, LateDeliver} or number
        if (Array.isArray(this.deliverResult)) {
          onTimeDeliver = Number(this.deliverResult[0]) || 0;
          lateDeliver = Number(this.deliverResult[1]) || 0;
        } else if (typeof this.deliverResult === 'object' && this.deliverResult !== null) {
          onTimeDeliver = Number(this.deliverResult.OnTimeDeliver ?? this.deliverResult.onTimeDeliver) || 0;
          lateDeliver = Number(this.deliverResult.LateDeliver ?? this.deliverResult.lateDeliver) || 0;
        } else {
          onTimeDeliver = Number(this.deliverResult) || 0;
          lateDeliver = 0;
        }

        // target can be object with Target property, array [value], or number
        let total = 0;
        if (typeof this.target === 'object' && this.target !== null) {
          total = Number(this.target.Target ?? this.target) || 0;
        } else {
          total = Number(this.target) || 0;
        }

        const data = [
          { value: onTimeDeliver, name: "On Time Ship" },
          { value: lateProduce, name: "Delay Produce" },
          { value: lateDeliver, name: "Delay Ship" },
          { value: onTimeProduce, name: "On Time Produce" }
        ];
      this.pieChart = echarts.init(this.$refs.pieChart)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          show: false  // This hides the legend
        },
        series: [
          {
            name: 'Access From',
            type: 'pie',
            radius: '75%',
            center: ['50%', '50%'],
            avoidLabelOverlap: true,
            data,
            itemStyle: {
              borderColor: '#2e2e2e',
              borderWidth: 2
            },
            label: {
              show: true,
              position: 'inside',
              formatter: function(params) {
                // Calculate total for percentage
                const percent = ((params.value / total*2) * 100).toFixed(1);
                return `${params.name}\n${percent}%`;
              },
              fontSize: 11,
              lineHeight: 15,
              align: 'center',
              color: '#fff',
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      this.pieChart.setOption(option)
    },

    createMeterOption(value) {
      return {
        series: [
          {
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            splitNumber: 5,
            min: 0,
            max: 100,
            radius: '100%',
            center: ['50%', '70%'],
            axisLine: {
              lineStyle: {
                width: 15,
                color: [
                  [0.5, '#ff4d4d'],  // red zone (0–50)
                  [0.8, '#ffcc00'],  // yellow zone (50–80)
                  [1, '#4caf50']     // green zone (80–100)
                ]
              }
            },
            pointer: {
              show: true,
              length: '50%',
              width: 6
            },
            progress: {
              show: false
            },
            splitLine: {
              show: true,
              distance: -15,
              length: 15,
              lineStyle: {
                width: 2,
                color: '#fff'
              }
            },
            axisTick: {
              show: false
            },
            axisLabel: {
              color: '#999',
              distance: 20,
              fontSize: 20,
              formatter: function (value) {
                // Only show specific values
                if ([0, 20, 40, 60, 80, 100].includes(value)) {
                  return value + '%';
                }
                return '';
              }
            },
            anchor: {
              show: true,
              size: 10,
              itemStyle: {
                color: '#fff'
              }
            },
            title: {
              show: false
            },
            detail: {
              valueAnimation: true,
              color: '#fff',
              fontSize: 22,
              offsetCenter: [0, '25%'],
              formatter: function (value) {
                return value + '%';
              }
            },
            data: [{ value }]
          }
        ]
      }
    },
    initWeeklyMeter() {
      this.weeklyMeter = echarts.init(this.$refs.weeklyMeter)
      const option = this.createMeterOption(this.weeklyCO ?? 0)
      this.weeklyMeter.setOption(option)
    },
    initMonthlyMeter() {
      if (this.monthlyCO === null || this.monthlyCO === undefined) return;

      const monthlyCO = this.monthlyCO;
      this.monthlyMeter = echarts.init(this.$refs.monthlyMeter)
      const option = this.createMeterOption(monthlyCO)
      this.monthlyMeter.setOption(option)
    },
    initProductionMeter() {
      if (this.monthlyProduction === null || this.monthlyProduction === undefined) return;

      const monthlyProduction = this.monthlyProduction
      this.productionMeter = echarts.init(this.$refs.productionMeter)
      const option = this.createMeterOption(monthlyProduction)
      this.productionMeter.setOption(option)
    },
    async initLineBarChart() {
      this.$emit('api-loading', true)
      this.lineBarChart = echarts.init(this.$refs.lineBarChart)
      const queryDate = this.selectedDate ? `?date=${this.selectedDate}` : '';
      const response = await fetch(`http://127.0.0.1:8000/api/monthlyOutputperWorkcell${queryDate}`)
      const result = await response.json()

      const postgresData = result.last_month || []
      
      const workcells = postgresData.map(item => item.name)
      const actOutTotals = postgresData.map(item => Number(item.total))
      const tarOut = postgresData.map(item => Number(item.tartotal))

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              // Add thousand separator and show values with 2 decimal places
              let value = param.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              result += param.marker + ' ' + param.seriesName + ': ' + value + '<br/>';
            });
            return result;
          }
        },
        legend: {
          data: ['Act Out', 'Target Out'],
          bottom: 45,
          textStyle: {
            color: '#fff'
          }
        },
        xAxis: [
          {
            type: 'category',
            data: workcells,
            axisLabel: {
              interval: 0, // Show all labels
              rotate: 0, // Make labels horizontal
              textStyle: {
                fontSize: 12,
                color: '#fff'
              }
            },
            axisPointer: {
              type: 'shadow'
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '25%', // More room for bar labels and x-axis labels
          top: '15%',    // Room for line data labels
          containLabel: true
        },
        yAxis: [
          {
            type: 'value',
            axisLabel: { color: '#fff' },
            name: '',
            position: 'left',
            max: Math.ceil(Math.max(...actOutTotals) * 1.2),
            offset: 0,
            axisLine: {
              show: true
            },
            axisTick: {
              show: true
            },
            splitLine: {
              show: true
            }
          }
        ],
        series: [
          {
            name: 'Act Out',
            type: 'bar',
            barWidth: '30%',  // Makes the bars thinner
            data:  actOutTotals,
            label: {
              show: true,
              position: 'insideBottom',
              distance: 15,
              fontSize: 12,
              formatter: function(params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              },
              color: '#fff'
            },
            itemStyle: {
              color: '#3498db'
            }
          },
          {
            name: 'Target Out',
            type: 'line',
            data: tarOut,
            yAxisIndex: 0,
            label: {
              show: true,
              position: 'right',
              color: '#FFEB3B',
              formatter: function(params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              }
            },
            itemStyle: {
              color: '#FFEB3B'
            },
            symbolSize: 8,
            lineStyle: {
              width: 3,
              color: '#FFEB3B'
            }
          }
        ]
      }
      this.$emit('api-connected', true)
      this.lineBarChart.setOption(option)
      this.$emit('api-loading', false)
    },

    showMonthlyFake() {
      this.activeMode = 'monthlyFake'
      const fakeNames = ['M.WC 1', 'M.WC 2', 'M.WC 3', 'M.WC 4', 'M.WC 5', 'M.WC 6', 'M.WC 7', 'HB.WC 1', 'HB.WC 2', 'PP (Total)', 'Pipe Bending',
                     'Pipe Cutting', 'Rolling 1', 'Rolling 2', 'TIG 1', 'TIG 2', 'TIG 3', 'TIG 4'];
      const fakeTotals = [5000, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500];
      const tarTotals = [10000, 5000, 3000, 2000, 5000, 4500, 5000, 8000, 6000, 7000, 6000, 5000, 1000, 1500, 6000, 6000, 4000, 3000];
      
      this.updateLineBarChart(fakeNames, fakeTotals, tarTotals);
    },

    async showWeeklyLive() {
      this.$emit('api-loading', true)
      this.activeMode = 'weekly'
      try {
        const queryDate = this.selectedDate ? `?date=${this.selectedDate}` : '';
        const res = await fetch(`http://127.0.0.1:8000/api/weeklyOutput${queryDate}`);
        const result = await res.json();

        const data = result.this_week || [];
        const names = data.map(i => i.name);
        const totals = data.map(i => Number(i.total));
        const tarTotals = data.map(i => Number(i.tartotal));

        this.updateLineBarChart(names, totals, tarTotals);
        this.$emit('api-connected', true)
      } catch (err) {
        console.error("Error fetching weekly:", err);
        this.$emit('api-error', `Failed to load data: ${err.message}`)
        this.$emit('api-connected', false)
      }finally {
        this.$emit('api-loading', false)
      }
    },

    async showMonthlyLive() {
      this.$emit('api-loading', true)
      this.activeMode = 'monthly'
      try {
        const queryDate = this.selectedDate ? `?date=${this.selectedDate}` : '';
        const response = await fetch(`http://127.0.0.1:8000/api/monthlyOutputperWorkcell${queryDate}`);
        const result = await response.json();

        const data = result.last_month || [];
        const names = data.map(i => i.name);
        const totals = data.map(i => Number(i.total));
        const tarTotals = data.map(i => Number(i.tartotal));

        this.updateLineBarChart(names, totals, tarTotals);
        this.$emit('api-connected', true)
      } catch (e) {
        console.error("MonthlyLive error:", e);
        this.$emit('api-error', `Failed to load data: ${e.message}`)
        this.$emit('api-connected', false)
      }finally {
        this.$emit('api-loading', false)
      }
    },

    async showDailyLive() {
      this.$emit('api-loading', true)
      this.activeMode = 'daily'
      try {
        const queryDate = this.selectedDate ? `?date=${this.selectedDate}` : '';
        const res = await fetch(`http://127.0.0.1:8000/api/dailyOutput${queryDate}`);
        const result = await res.json();

        const data = result.today || [];
        const names = data.map(i => i.name);
        const totals = data.map(i => Number(i.total));
        const tarTotals = data.map(i => Number(i.tartotal));

        this.updateLineBarChart(names, totals, tarTotals);
        this.$emit('api-connected', true)
      } catch (e) {
        console.error("Weekly API error:", e);
        this.$emit('api-error', `Failed to load data: ${e.message}`)
        this.$emit('api-connected', false)
      }finally {
          this.$emit('api-loading', false)
      }
    },

    updateLineBarChart(workcells, actOutTotals, tarOut) {
      // Calculate the max value for left Y-axis
      const maxLeft = Math.ceil(Math.max(
        ...actOutTotals,
        ...tarOut
      ) * 1.2);

      const option = {
        xAxis: [{ data: workcells }],
        yAxis: [
          { 
            type: 'value',
            max: maxLeft,
            axisLabel: { color: '#fff' },
            axisLine: { show: true },
            axisTick: { show: true },
            splitLine: { show: true }
          }
        ],
        series: [
          {
            name: 'Act Out',
            type: 'bar',
            barWidth: '30%',
            data: actOutTotals,
            label: {
              show: true,
              position: 'insideBottom',
              distance: 15,
              fontSize: 12,
              formatter: function (params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              },
              color: '#fff'
            },
            itemStyle: {
              color: '#3498db'
            }
          },
          {
            name: 'Target Out',
            type: 'line',
            data: tarOut,
            symbolSize: 8,
            label: {
              show: true,
              position: 'right',
              color: '#FFEB3B',
              formatter: function (params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              }
            },
            itemStyle: {
              color: '#FFEB3B'
            },
            lineStyle: {
              width: 3,
              color: '#FFEB3B'
            }
          }
        ]
      };

      this.lineBarChart.setOption(option);
    }


  }
}
</script>

<style scoped>
.dashboard {
  background: linear-gradient(135deg, rgba(3, 23, 57, 0.95) 0%, rgba(1, 15, 35, 0.98) 100%);
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
  padding: 8px;
}

.dashboard-title {
  text-align: center;
  padding: 5px;
  flex-shrink: 0;
}

.title-controls {
  display: flex;
  justify-content: center;
  gap: 12px;
  align-items: center;
  padding:10px;
  align-items: center;
  padding: 0 15px;
}

.date-picker {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #00baff;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  font-weight: bold;
  box-shadow: 0 0 8px #00baff55;
}

.date-picker:hover {
  border-color: #00eaff;
  box-shadow: 0 0 12px #00eaffaa;
}

.date-picker::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.title-dropdown {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #00baff;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  font-weight: bold;
  text-align: center;
  box-shadow: 0 0 8px #00baff55;
}

.title-dropdown:hover {
  border-color: #00eaff;
  box-shadow: 0 0 12px #00eaffaa;
}

.dashboard-title h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
  color: #00baff;
  text-shadow: 0 0 10px rgba(0, 186, 255, 0.5);
  letter-spacing: 1px;
}

/* MAIN CHARTS ROW */
.charts-container {
  display: flex;
  gap: 8px;
  flex: 1;
  min-height: 0;
}

/* PIE BOX LEFT */
.pie-container {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
}

.pie-box {
  background: rgba(3, 23, 57, 0.8);
  padding: 8px;
  border-radius: 10px;
  border: 1px solid rgba(0, 186, 255, 0.2);
  width: 100%;
  box-sizing: border-box;
  height: 100%;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.pie-box:hover {
  border-color: #00baff;
  box-shadow: 0 0 18px rgba(0, 186, 255, 0.4);
}

.pie-title {
  text-align: center;
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 16px;
  color: #00baff;
  text-shadow: 0 0 8px rgba(0, 186, 255, 0.3);
  background: linear-gradient(90deg, rgba(0,186,255,0.1) 0%, rgba(0,186,255,0.05) 100%);
  padding: 6px;
  border-radius: 6px;
}

.pie-content {
  flex: 1;
  min-height: 0;
  height: calc(100% - 20px);
}

/* METERS RIGHT */
.meters-container {
  display: flex;
  flex: 1.5;
  gap: 8px;
  min-height: 0;
  height: 100%;
}

.meter-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  height: 100%;
  min-height: 0;
  border-radius: 10px;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  overflow: hidden;
  box-sizing: border-box;
}

.meter-box:hover {
  border-color: #00baff;
  box-shadow: 0 0 18px rgba(0, 186, 255, 0.4);
}

.meter-title {
  background: linear-gradient(135deg, #0d7cb5 0%, #00baff 100%);
  color: white;
  padding: 8px;
  text-align: center;
  font-weight: bold;
  font-size: 13px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid rgba(0, 186, 255, 0.5);
}

.meter-content {
  background: rgba(3, 23, 57, 0.6);
  flex: 1;
  padding: 4px;
}

/* BOTTOM LINE-BAR BOX */
.bottom-chart {
  flex: 1;
  min-height: 0;
  padding: 0;
}

.linebar-box {
  background: rgba(3, 23, 57, 0.8);
  padding: 8px;
  border-radius: 10px;
  border: 1px solid rgba(0, 186, 255, 0.2);
  width: 100%;
  height: 100%;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.linebar-box:hover {
  border-color: #00baff;
  box-shadow: 0 0 18px rgba(0, 186, 255, 0.4);
}

.chart {
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 0;
}

.linebar-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.linebar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: 0;
  font-weight: bold;
  color: #00baff;
  font-size: 22px;
  margin: 0;
  line-height: 30px;
  text-shadow: 0 0 8px rgba(0, 186, 255, 0.3);
}

/* Button group */
.linebar-buttons {
  position: static;
  right: 400px;
  top: 0;
  display: flex;
  gap: 8px;
}

/* Button styling */
.switch-btn {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #00baff;
  padding: 6px 15px;
  font-size: 12px;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 8px rgba(0, 186, 255, 0.3);
}

.switch-btn:hover {
  background-color: #00baff;
  color: #1a1a1a;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.6);
}

.switch-btn:active {
  transform: scale(0.95);
}
</style>