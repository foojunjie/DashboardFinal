<template>
  <div class="wc-box" :class="barColor">
    <div class="wc-header">
      <div class="wc-title">{{ wc.title }}</div>

      <div class="header-right">
        <!-- Top-right stats - missed and output boxes -->
        <div class="top-right-stats" v-if="wc">
          <div class="stat-row"><span class="stat-label">Missed:</span> <span class="stat-value">{{ wc.missed_quantity || 0 }}</span></div>
          <div class="stat-row"><span class="stat-label">Output:</span> <span class="stat-value">{{ wc.output_done || 0 }}</span></div>
        </div>

        <div class="status-column">
          <div class="wc-status" :class="statusClass">{{ wc.status }}</div>
          <div class="wc-connection" :class="connectionClass">{{ wc.connection || 'Connected' }}</div>
        </div>
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

    <!-- Bar+Line Chart for Actual vs Ideal Duration -->
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'WCBoxDetailedPerDay',
  props: {
    wc: { type: Object, required: true },
    period: { type: String, default: 'TODAY' }
  },
  data() {
    return {
      chart: null,
      localWC: { ...this.wc }
    }
  },
  watch: {
    wc: {
      deep: true,
      handler(newVal) {
        this.localWC = { ...newVal }
        this.updateChart()
      }
    },
    period: {
      handler() {
        this.updateChart()
      }
    }
  },
  computed: { 
    barColor() { 
      return `bar-${this.wc.bars}` || 'bar-gray' 
    }, 
    statusClass() {
      if (this.wc.status === 'Running') return 'running'
      if (this.wc.status === 'Partially Running') return 'partially'
      return 'idle' // for Idle
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
    updateChart() {
      if (!this.chart) return
      
      // Generate X-axis labels based on period
      let xAxisLabels = []
      let actualDurationData = Array(24).fill(0)
      let idealDurationData = Array(24).fill(0)
      
      if (this.period === 'TODAY' || this.period === 'DAY') {
        // 24 hours: 0, 1, 2, ..., 23
        xAxisLabels = Array.from({ length: 24 }, (_, i) => String(i))
        actualDurationData = (this.wc.actual_duration && Array.isArray(this.wc.actual_duration)) 
          ? this.wc.actual_duration.map(Number) 
          : Array(24).fill(0)
        idealDurationData = (this.wc.ideal_duration && Array.isArray(this.wc.ideal_duration)) 
          ? this.wc.ideal_duration.map(Number) 
          : Array(24).fill(0)
      } else if (this.period === 'WEEKLY') {
        // 7 days: 1, 2, 3, 4, 5, 6, 7
        xAxisLabels = Array.from({ length: 7 }, (_, i) => String(i + 1))
        actualDurationData = Array(7).fill(0)
        idealDurationData = Array(7).fill(0)
      } else if (this.period === 'MONTHLY') {
        // 5 weeks: 1, 2, 3, 4, 5
        xAxisLabels = Array.from({ length: 5 }, (_, i) => String(i + 1))
        actualDurationData = Array(5).fill(0)
        idealDurationData = Array(5).fill(0)
      } else if (this.period === 'ALL TIME') {
        // 12 months: 1, 2, ..., 12
        xAxisLabels = Array.from({ length: 12 }, (_, i) => String(i + 1))
        actualDurationData = Array(12).fill(0)
        idealDurationData = Array(12).fill(0)
      }

      const option = {
        grid: { left: '8%', right: '5%', top: '10%', bottom: '15%', containLabel: true },
        legend: {
          data: ['Actual Duration', 'Ideal Duration'],
          textStyle: { color: '#fff' },
          bottom: 0
        },
        xAxis: {
          type: 'category',
          data: xAxisLabels,
          axisLabel: { fontSize: 10, color: '#999', interval: 0 },
          axisLine: { lineStyle: { color: '#444' } }
        },
        yAxis: {
          type: 'value',
          name: 'Duration (seconds)',
          axisLabel: { fontSize: 10, color: '#999' },
          splitLine: { lineStyle: { color: '#333' } },
          axisLine: { lineStyle: { color: '#444' } }
        },
        tooltip: {
          trigger: 'axis',
          formatter: params => {
            let html = `${params[0].axisValue}<br/>`
            params.forEach(p => {
              const value = typeof p.data === 'object' ? p.data.value : p.data
              html += `${p.seriesName}: ${Math.round(value)}<br/>`
            })
            return html
          },
          backgroundColor: 'rgba(0,0,0,0.8)',
          borderColor: '#00baff',
          textStyle: { color: '#fff' }
        },
        series: [
          {
            name: 'Actual Duration',
            type: 'line',
            data: actualDurationData.map((value, index) => {
              const actualVal = Number(value) || 0
              const idealVal = Number(idealDurationData[index]) || 0
              // Red if actual > ideal, else green
              const color = actualVal > idealVal ? '#FF4444' : '#44FF44'
              return {
                value: actualVal,
                itemStyle: { color: color }
              }
            }),
            lineStyle: { 
              color: (ctx) => {
                // Determine line color based on data point values
                const data = ctx.data
                if (Array.isArray(data) && data.length > 0) {
                  let hasRedPoints = false
                  for (let i = 0; i < Math.min(data.length, idealDurationData.length); i++) {
                    const actual = typeof data[i] === 'object' ? data[i].value : data[i]
                    const ideal = idealDurationData[i] || 0
                    if (actual > ideal) {
                      hasRedPoints = true
                      break
                    }
                  }
                  return hasRedPoints ? '#FF4444' : '#44FF44'
                }
                return '#44FF44'
              },
              width: 2 
            },
            itemStyle: { borderWidth: 2 },
            smooth: true,
            yAxisIndex: 0
          },
          {
            name: 'Ideal Duration',
            type: 'line',
            data: idealDurationData.map(v => Number(v) || 0),
            lineStyle: { color: '#00baff', width: 2, type: 'dashed' },
            itemStyle: { color: '#00baff' },
            smooth: true,
            yAxisIndex: 0
          }
        ]
      }

      this.chart.setOption(option)
    }
  }
}
</script>

<style scoped>
.wc-box {
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
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
  border-left: 5px solid #f44336;
}

.wc-box.bar-gray {
  border-left: 5px solid #999;
}

.wc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.wc-title {
  font-weight: bold;
  font-size: 16px;
  color: #fff;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.top-right-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  background-color: rgba(0, 186, 255, 0.1);
  padding: 6px 8px;
  border-radius: 4px;
  border: 1px solid #00baff;
}

.stat-row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.stat-label {
  color: #00baff;
  font-weight: 600;
}

.stat-value {
  color: #fff;
  font-weight: bold;
}

.status-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: right;
}

.wc-status {
  font-size: 11px;
  font-weight: bold;
  padding: 3px 6px;
  border-radius: 3px;
  background-color: #333;
  color: #fff;
}

.wc-status.running {
  background-color: #4caf50;
  color: white;
}

.wc-status.idle {
  background-color: #f44336;
  color: white;
}

.wc-status.partially {
  background-color: #ffeb3b;
  color: #333;
}

.wc-connection {
  font-size: 9px;
  padding: 2px 4px;
  border-radius: 2px;
  background-color: #333;
  color: #999;
}

.wc-connection.connected {
  color: #4caf50;
}

.wc-connection.manual {
  color: #ffeb3b;
}

.wc-connection.not-connected {
  color: #f44336;
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
  color: #00baff;
}

.metrics-box {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #333;
}

.metric-row {
  display: flex;
  justify-content: space-around;
  gap: 8px;
}

.metric {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 11px;
  color: #999;
}

.metric-value {
  font-size: 14px;
  font-weight: bold;
  color: #00baff;
}

.chart-container {
  width: 100%;
  height: 200px;
}
</style>
