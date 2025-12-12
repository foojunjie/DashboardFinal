<template>
  <div class="wc-box" :class="barColor">
    <div class="wc-header">
      <div class="wc-title">{{ wc.title }}</div>
      <div class="status-column">
        <div class="wc-status" :class="statusClass">{{ wc.status }}</div>
        <div class="wc-connection" :class="connectionClass">{{ wc.connection || 'Connected' }}</div>
      </div>
    </div>
    
    <div class="wc-oee">
      <span class="oee-label">OEE:</span>
      <span class="oee-value">{{ wc.oee }}%</span>
    </div>
    
    <!-- Metrics Box -->
    <div class="metrics-box">
      <div class="metric-row">
        <div class="metric">
          <span class="metric-label">Availability</span>
          <span class="metric-value">{{ wc.availability !== undefined ? wc.availability : 85 }}%</span>
        </div>
        <div class="metric">
          <span class="metric-label">Performance</span>
          <span class="metric-value">{{ wc.performance !== undefined ? wc.performance : 90 }}%</span>
        </div>
        <div class="metric">
          <span class="metric-label">Quality</span>
          <span class="metric-value">{{ wc.quality !== undefined ? wc.quality : 95 }}%</span>
        </div>
      </div>
    </div>

    <!-- Bar Chart -->
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'WCBox',
  props: {
    wc: { type: Object, required: true },
    period: { type: String, default: 'TODAY' }
  },
  data() {
    return {
      chart: null,
      localWC: { ...this.wc, hourlyOEE: [...(this.wc.hourlyData || Array(24).fill(0))] }
    }
  },
  watch: {
    wc: {
      deep: true,
      handler(newVal) {
        this.localWC = { ...newVal, hourlyOEE: [...(newVal.hourlyData || Array(24).fill(0))] }
        this.updateChart()
      }
    }
  },
  computed: { 
    barColor() { 
      return `bar-${this.wc.bars}` || 'bar-gray' 
    }, 
    statusClass() { 
      return this.wc.status === 'Running' ? 'running' : 'not-running' 
    }, 
    connectionClass() { 
      const conn = this.wc.connection || 'Connected' 
      if (conn === 'Connected') return 'connected' 
      if (conn === 'Manual') return 'manual' 
      return 'not-connected' 
    } 
  },
  mounted() {
    this.initChart()
    this.updateHourlyData()
  },
  beforeUnmount() {
    if (this.chart) this.chart.dispose()
  },
  methods: {
    initChart() {
      if (!this.$refs.chartContainer) return
      this.chart = echarts.init(this.$refs.chartContainer)
      this.updateChart()
    },
    updateHourlyData() {
      const currentHour = new Date().getHours()
      this.localWC.hourlyOEE[currentHour] = this.localWC.oee
      this.updateChart()
    },
    updateChart() {
      if (!this.chart) return
      
      // Generate X-axis labels based on period
      let xAxisLabels = []
      let dataLength = 24
      
      if (this.period === 'TODAY' || this.period === 'DAY') {
        // 24 hours: 0, 1, 2, ..., 23
        xAxisLabels = Array.from({ length: 24 }, (_, i) => String(i))
        dataLength = 24
      } else if (this.period === 'WEEKLY') {
        // 7 days: 1, 2, 3, 4, 5, 6, 7
        xAxisLabels = Array.from({ length: 7 }, (_, i) => String(i + 1))
        dataLength = 7
      } else if (this.period === 'MONTHLY') {
        // 5 weeks: 1, 2, 3, 4, 5
        xAxisLabels = Array.from({ length: 5 }, (_, i) => String(i + 1))
        dataLength = 5
      } else if (this.period === 'ALL TIME') {
        // 12 months: 1, 2, ..., 12
        xAxisLabels = Array.from({ length: 12 }, (_, i) => String(i + 1))
        dataLength = 12
      }
      
      const data = this.wc.hourlyData && Array.isArray(this.wc.hourlyData) 
        ? this.wc.hourlyData 
        : Array(dataLength).fill(0)

      const option = {
        grid: { left: '8%', right: '5%', top: '10%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: xAxisLabels,
          axisLabel: { fontSize: 10, color: '#999', interval: 0 },
          axisLine: { lineStyle: { color: '#444' } }
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 10, color: '#999' },
          splitLine: { lineStyle: { color: '#333' } },
          axisLine: { lineStyle: { color: '#444' } }
        },
        tooltip: {
          trigger: 'axis',
          formatter: params => {
            const p = params[0]
            return `${p.axisValue}<br/>OEE: ${p.data.toFixed(1)}%`
          },
          backgroundColor: 'rgba(0,0,0,0.8)',
          borderColor: '#00baff',
          textStyle: { color: '#fff' }
        },
        series: [{
          type: 'bar',
          barWidth: '80%',
          data: data.map(value => ({
            value: Number(value) || 0,
            itemStyle: {
              color: value >= 80 ? '#4caf50' : value >= 50 ? '#ffeb3b' : '#f44336'
            }
          }))
        }]
      }

      this.chart.setOption(option)
    }
  }
}
</script>

<style scoped>
.wc-box {
  background: #2e2e2e;
  border: 3px solid #555;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: white;
  transition: all 0.3s ease;
}

.wc-box:hover {
  box-shadow: 0 0 15px rgba(0, 186, 255, 0.3);
  border-color: #00baff;
}

.wc-box.bar-green {
  border-left: 5px solid #4caf50;
}

.wc-box.bar-yellow {
  border-left: 5px solid #ffeb3b;
}

.wc-box.bar-red {
  border-left: 5px solid #ff6b6b;
}

.wc-box.bar-gray {
  border-left: 5px solid #999;
}

.wc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.status-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.wc-title {
  font-size: 16px;
  font-weight: bold;
  color: #00baff;
}

.wc-status {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.wc-status.running {
  background-color: #4caf50;
  color: white;
}

.wc-status.not-running {
  background-color: #ff6b6b;
  color: white;
}

.wc-connection {
  font-size: 10px;
  padding: 3px 6px;
  border-radius: 3px;
  font-weight: bold;
  text-transform: uppercase;
}

.wc-connection.connected {
  background-color: #4caf50;
  color: white;
}

.wc-connection.manual {
  background-color: #ff9800;
  color: white;
}

.wc-connection.not-connected {
  background-color: #f44336;
  color: white;
}

.wc-oee {
  display: flex;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.oee-label {
  color: #999;
}

.oee-value {
  color: #4caf50;
}

/* Metrics Box with White Border */
.metrics-box {
  border: 2px solid white;
  border-radius: 6px;
  padding: 10px;
  background-color: #1a1a1a;
}

.metric-row {
  display: flex;
  gap: 8px;
  justify-content: space-around;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.metric-label {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  font-weight: bold;
}

.metric-value {
  font-size: 14px;
  font-weight: bold;
  color: #4caf50;
}

/* Bar Chart */
.chart-container {
  width: 100%;
  height: 200px;
  margin-top: 10px;
}
</style>
