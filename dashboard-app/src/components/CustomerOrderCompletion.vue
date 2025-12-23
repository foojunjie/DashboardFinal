<template>
  <div class="dashboard">
    <!-- Title Section -->
    <div class="dashboard-title">
      <h1>% OF CUSTOMER ORDER COMPLETION</h1>
    </div>
    
    <!-- Charts Container -->
    <div class="top-section">
        <div class="meters-container">
            <div class="meter-box">
            <div class="meter-title">Daily Output</div>
            <div class="meter-content">
                <div ref="dailyOutput" class="chart"></div>
            </div>
            </div>
            <div class="meter-box">
            <div class="meter-title">Daily Ship</div>
            <div class="meter-content">
                <div ref="dailyShip" class="chart"></div>
            </div>
            </div>
        </div>

        <div class="linebar-container">
            <div class="linebar-box">
                <div class="linebar-header">
                <div class="linebar-title">Total CO</div>
                </div>
                <div ref="lineBarChart" class="chart"></div>
            </div>
        </div>
    </div>

    <div class="inventory-table-container">
    <table class="inventory-table">
      <thead>
        <tr>
          <th>CO #</th>
          <th>Part #</th>
          <th>Workcell</th>
          <th>CO (Qty)</th>
          <th>Plan (Qty)</th>
          <th>CarryForward</th>
          <th>Output (Cumm)</th>
          <th>Shipped (Qty)</th>
          <th>WIP (Qty)</th>
          <th>Bal (Qty)</th>
          <th>Order Fulfill (%)</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in tableData"
          :key="index"
          :class="{ 'alt-row': index % 2 === 1 }"
        >
          <td>{{ row.CO }}</td>
          <td>{{ row.Part }}</td>
          <td>{{ row.Workcell }}</td>
          <td>{{ row.COQty }}</td>
          <td>{{ row.PlanQty }}</td>
          <td>{{ row.CarryForward }}</td>
          <td>{{ row.Output }}</td>
          <td>{{ row.ShippedQty }}</td>
          <td>{{ row.WIPQty }}</td>
          <td>{{ row.BalQty }}</td>
          <td>{{ row.OrderFulfill }}%</td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'MainDashboard',
  data() {
    return {
      dailyOutput: null,
      dailyShip: null,
      lineBarChart: null,
      refreshInterval: null,
      tableData: [],

      dailyOutputValue: 0,
      dailyShipValue: 0,

      dates: [],
      shipped: [],
      wip: [],
      output: [],
      of: [],
      actOutTotals: []
    }
  },
  mounted() {
    this.initDailyOutput()
    this.initDailyShip()
    this.initLineBarChart()
    this.fetchCOCompletion()
    // Handle resize
    window.addEventListener('resize', this.handleResize)

    this.refreshInterval = setInterval(() => {
      this.fetchCOCompletion()
    }, 300000)
  },

  beforeUnmount() {
    // Clean up
    window.removeEventListener('resize', this.handleResize)
    clearInterval(this.refreshInterval) // Stop auto-refresh
    this.dailyOutput?.dispose()
    this.dailyShip?.dispose()
    this.lineBarChart?.dispose()
  },
  methods: {
    handleResize() {
      this.dailyOutput?.resize()
      this.dailyShip?.resize()
      this.lineBarChart?.resize()
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
    initDailyOutput() {
      this.dailyOutput = echarts.init(this.$refs.dailyOutput)
      this.dailyOutput.setOption(this.createMeterOption(this.dailyOutputValue))
    },
    initDailyShip() {
      this.dailyShip = echarts.init(this.$refs.dailyShip)
      this.dailyShip.setOption(this.createMeterOption(this.dailyShipValue))
    },

    async initLineBarChart() {
      this.lineBarChart = echarts.init(this.$refs.lineBarChart)

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
          data: ['Shipped', 'WIP', 'Output', 'OF'],
          bottom: 45,
          textStyle: {
            color: '#fff'
          }
        },
        xAxis: [
          {
            type: 'category',
            data: [],
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
            max: 100,
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
          },
          {
            type: 'value',
            axisLabel: { color: '#fff' },
            name: '',
            position: 'right',
            max:100,
            yAxisIndex: 1,
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
            name: 'Shipped',
            type: 'bar',
            barWidth: '15%',  // Makes the bars thinner
            barGap: '30%',
            barCategoryGap: '40%',
            data: [],
            label: {
              show: true,
              position: 'insideBottom',
              distance: 10,
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
            name: 'WIP',
            type: 'bar',
            barWidth: '15%',  // Makes the bars thinner
            barGap: '30%',
            data: [],
            label: {
              show: true,
              position: 'insideBottom',
              distance: 25,
              fontSize: 12,
              formatter: function(params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              },
              color: '#fff'
            },
            itemStyle: {
              color: '#27F557'
            }
          },
          {
            name: 'Output',
            type: 'bar',
            barGap: '30%',
            barWidth: '15%',  // Makes the bars thinner
            data: [],
            label: {
              show: true,
              position: 'insideBottom',
              distance: 40,
              fontSize: 12,
              formatter: function(params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              },
              color: '#fff'
            },
            itemStyle: {
              color: '#F52727'
            }
          },
          {
            name: 'OF',
            type: 'line',
            data: [],
            yAxisIndex: 1,
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
      this.lineBarChart.setOption(option)
    },

    async fetchCOCompletion() {
      try {
        this.$emit('api-loading', true)
        const res = await fetch('http://127.0.0.1:8000/api/COCompletion')
        const data = await res.json()

        // ---- Update meters ----
        this.dailyOutputValue = Number(data.dailyOutput.dailyOutput) || 0
        this.dailyShipValue = Number(data.dailyShip.dailyship) || 0

        this.dailyOutput.setOption(this.createMeterOption(this.dailyOutputValue))
        this.dailyShip.setOption(this.createMeterOption(this.dailyShipValue))

        // ---- Update weekly chart ----
        this.updateLineBarChart(data.weeklyResult)

        // ---- Update table ----
        this.tableData = data.COCompletion || []

        this.$emit('api-connected', true)
      } catch (err) {
        console.error('Failed to load COCompletion data', err)
        this.$emit('api-error', `Failed to load data: ${err.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    updateLineBarChart(weeklyData) {
      const dates = weeklyData.map(d => {
        const date = new Date(d.date)
        return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
      })

      const shipped = weeklyData.map(d => d.DeliverQuantity || 0)
      const wip = weeklyData.map(d => d.WIP || 0)
      const output = weeklyData.map(d => d.produce || 0)
      const of = weeklyData.map(d => d.OrderFulfill || 0)

      const leftMaxRaw = Math.max(
        ...shipped,
        ...wip,
        ...output,
        0
      )

      const rightMaxRaw = Math.max(
        ...of,
        0
      )

      const leftMax = Math.ceil(leftMaxRaw * 1.2)
      const rightMax = Math.ceil(rightMaxRaw * 1.2)

      this.lineBarChart.setOption({
        xAxis: [{ data: dates }],
        yAxis: [
          {
            max: leftMax
          },
          {
            max: rightMax
          }
        ],
        series: [
          { name: 'Shipped', data: shipped },
          { name: 'WIP', data: wip },
          { name: 'Output', data: output },
          { name: 'OF', data: of }
        ]
      })
    },
  }
}
</script>

<style scoped>
.dashboard {
  background: #1a1a1a; /* darker grey-black */
  color: white;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100vh;
  max-height: 100vh;
  overflow-y: hidden;
  overflow-x: hidden;
  box-sizing: border-box;
}

.dashboard-title {
  text-align: center;
  gap: 15px;
  padding: 5px;
}

.dashboard-title h1 {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
  color: #00baff;
  text-shadow: 0 0 10px rgba(0, 186, 255, 0.5);
  letter-spacing: 1px;
}

/* MAIN CHARTS ROW */
.top-section {
  display: flex;
  height: 45%;
  min-height: 320px;
  gap: 10px;
  padding: 5px;
}

.meters-container {
  display: flex;
  flex: 1.5;
  gap: 0;
}

.meter-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #2e2e2e;
  border: 15px solid #1a1a1a;
  border-right-width: 2px;
  height: 100%;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5);
}

.meter-box:last-child {
  border-right-width: 15px;
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
  background-color: #2e2e2e;
  flex: 1;
  padding: 8px;
}

.linebar-container {
  flex: 1.5;
  display: flex;
}

.linebar-box {
  background-color: #2e2e2e;
  padding: 8px;
  border-radius: 10px;
  border: 15px solid #1a1a1a;
  width: 100%;
  height: 100%;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.chart {
  width: 100%;
  height: 100%;
  flex: 1;
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

.inventory-table-container {
  flex: 1;
  background-size: 100%;     
  background-position: center;
  background-repeat: no-repeat;
  background-color: white;
  border: 2px solid #512f87;
  border-radius: 6px;
  overflow: auto;
  height: 100%;
  width: 100%;
  border: 15px solid #1a1a1a;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5);
}

.inventory-table-container::before {
  content: '';
  flex:1;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.6); /* white overlay, 60% opacity */
  z-index: 1;
}

.inventory-table {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  border-collapse: collapse;
  text-align: center;
  font-family: 'Segoe UI', sans-serif;
}

.inventory-table th {
  background-color: #7b2cbf;
  color: white;
  padding: 10px;
  font-weight: bold;
  border-bottom: 2px solid #512f87;
   border: 1px solid white;
}

.inventory-table td {
  padding: 8px;
  border: 1px solid white; 
}

/* Alternate row colors */
.inventory-table tr:nth-child(odd) td {
  background-color: #E6E6FA, 0.8; /* light purple */
}

.inventory-table tr:nth-child(even) td {
  background-color: #D3D3D3, 0.8; /* light grey */
}

.inventory-table .alt-row {
  background-color: rgba(123, 44, 191, 0.08);
}

.item-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-img {
  width: 50px;
  height: 50px;
  position: relative;
  object-fit: contain;
  opacity: 0.8; /* 60% transparent */
  border-radius: 4px;
}

.inventory-table th,
.inventory-table td {
  font-weight: bold;
}
</style>