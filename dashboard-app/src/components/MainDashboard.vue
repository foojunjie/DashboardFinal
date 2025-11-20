<template>
  <div class="dashboard">
    <!-- Title Section -->
    <div class="dashboard-title">
      <h1>OUTPUT STATUS (SUMMARY WEEKLY AND MONTHLY OUTPUT UPDATE)</h1>
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
      <div ref="lineBarChart" class="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'MainDashboard',
  data() {
    return {
      pieChart: null,
      weeklyMeter: null,
      monthlyMeter: null,
      productionMeter: null,
      lineBarChart: null
    }
  },
  mounted() {
    this.initPieChart()
    this.initWeeklyMeter()
    this.initMonthlyMeter()
    this.initProductionMeter()
    this.initLineBarChart()
    
    // Handle resize
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    // Clean up
    window.removeEventListener('resize', this.handleResize)
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
    initPieChart() {
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
            radius: '90%',
            center: ['50%', '55%'],
            avoidLabelOverlap: true,
            data: [
              { value: 46, name: 'On Time Ship' },
              { value: 18, name: 'Delay Produce' },
              { value: 9, name: 'Delay Ship' },
              { value: 27, name: 'On Time Produce' }
            ],
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              position: 'inside',
              formatter: function(params) {
                // Calculate total
                const total = 46 + 18 + 9 + 27;
                const percent = ((params.value / total) * 100).toFixed(1);
                return `${params.name}\n${percent}%`;
              },
              fontSize: 12,
              lineHeight: 16,
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
      const option = this.createMeterOption(90)
      this.weeklyMeter.setOption(option)
    },
    initMonthlyMeter() {
      this.monthlyMeter = echarts.init(this.$refs.monthlyMeter)
      const option = this.createMeterOption(82)
      this.monthlyMeter.setOption(option)
    },
    initProductionMeter() {
      this.productionMeter = echarts.init(this.$refs.productionMeter)
      const option = this.createMeterOption(90)
      this.productionMeter.setOption(option)
    },
    async initLineBarChart() {
      this.lineBarChart = echarts.init(this.$refs.lineBarChart)
      const response = await fetch('http://127.0.0.1:8000/api/monthlyOutputperWorkcell')
      const result = await response.json()

      const postgresData = result.last_month || []
      
      const workcells = postgresData.map(item => item.name)
      const actOutTotals = postgresData.map(item => Number(item.total))

      const option = {
        title: {
          text: 'Monthly Production Output by Workcell',
          left: 'center',
          textStyle: { color: '#fff' }
        },
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
          bottom: 0
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
          },
          {
            type: 'value',
            axisLabel: { color: '#fff' },
            name: '',
            position: 'right',
            max: Math.ceil(Math.max(...actOutTotals) * 1.2),
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
            yAxisIndex: 1,
            data: actOutTotals,
            label: {
              show: true,
              position: 'right',
              formatter: function(params) {
                return params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
              }
            },
            itemStyle: {
              color: '#FFEB3B'
            },
            symbolSize: 8,
            lineStyle: {
              width: 3
            }
          }
        ]
      }
      this.lineBarChart.setOption(option)
    }
  }
}
</script>

<style scoped>
.dashboard {
  background: linear-gradient(180deg, #2E004F 0%, #003366 100%);
  color: white;
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-title {
  text-align: center;
  padding: 10px;
}

.dashboard-title h1 {
  margin: 0;
  color: #fff;
}

.charts-container {
  display: flex;
  gap: 20px;
  height: 60%;
}

.pie-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 350px;
}
.pie-box {
  background-color: rgba(255,255,255,0.05);
  padding: 10px;
  border-radius: 10px;
  width: 100%;
  height: 100%;
  min-height: 350px; 
}
.pie-title {
  text-align: center;
  font-weight: bold;
  margin-bottom: 5px;
}
.pie-content {
  flex: 1;
  height: 100%;
  margin-top: -35px;
}

.meters-container {
  display: flex;
  flex: 2;
  gap: 0;
  margin-left: 20px;
}

.meter-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-right: none;
}

.meter-box:last-child {
  border-right: 1px solid #e0e0e0;
}

.meter-title {
  background-color: #1e88e5;
  color: white;
  padding: 10px;
  text-align: center;
  font-weight: bold;
  font-size: 14px;
}

.meter-content {
  background-color: white;
  flex: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.bottom-chart {
  flex: 1;
  padding: 15px;
  min-height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>