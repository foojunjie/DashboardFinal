<template>
  <div class="OutputVsDailyTarget">
    <!-- Title -->
    <div class="OutputVsDailyTarget-title">
      <h1>OUTPUT % VS DAILY TARGET (LIVE)</h1>
    </div>

    <!-- Main Layout -->
    <div class="main-content">
      <!-- LEFT SIDE -->
      <div class="left-panel">
        <!-- Bar Chart -->
        <div class="bottom-chart">
          <div class="bar-box">
            <div ref="BarChart" class="chart"></div>
          </div>
        </div>

        <!-- Table -->
        <div class="table-chart">
          <div class="table-box">
            <div class="table-title">{{ currentWorkcell }}</div>

            <div class="table-wrapper">
              <table class="workcell-table">
                <thead>
                  <tr>
                    <th>JTC #</th>
                    <th>Qty</th>
                    <th>Yield %</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in currentTableData" :key="row.jtc_orderNumber">
                    <td>{{ row.jtc_orderNumber }}</td>
                    <td>{{ row.jtc_quantityCompleted }}</td>
                    <td>{{ row.yield }}%</td>
                    <td>{{ formatTime(row.jtc_actualEndDate) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDE -->
      <div class="right-panel">
        <div class="station-box">
          <div class="box">
            <!-- Station boxes (4 at a time) -->
            <div v-for="station in displayedStations" :key="station.id" class="details-box">
              <div class="station-content">
                <div class="station-header">ST {{ station.id }}</div>
                <div class="station-info">
                  <div class="info-row">
                    <span class="label">Status:</span>
                    <span class="value" :class="station.is_running ? 'running' : 'idle'">
                      {{ station.is_running ? 'Running' : 'Idle' }}
                    </span>
                  </div>
                  <div class="info-row">
                    <span class="label">JTC #:</span>
                    <span class="value">{{ station.jtc_orderNumber }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">Counter:</span>
                    <span class="value">{{ getStationQty(station.id) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'OutputVsDailyTarget',
  data() {
    return {
      barChart: null,
      refreshInterval: null,
      stationRotationInterval: null,

      // API Data
      allOutputData: [],
      allStations: [],
      allTableData: [],
      allWorkcells: [],
      
      // Current display indices
      currentWorkcellIndex: 0,
      currentStationPage: 0
    }
  },

  computed: {
    currentWorkcell() {
      if (this.allWorkcells.length === 0) return 'No Data'
      return this.allWorkcells[this.currentWorkcellIndex] || 'No Data'
    },
    
    currentTableData() {
      if (this.allTableData.length === 0) return []
      return this.allTableData.filter(row => row.name === this.currentWorkcell)
    },
    
    currentOutputData() {
      if (this.allOutputData.length === 0) return null
      return this.allOutputData.find(d => d.workcell === this.currentWorkcell)
    },
    
    displayedStations() {
      if (this.allStations.length === 0) return []
      
      // Filter stations for current workcell
      const wcStations = this.allStations.filter(s => s.workcell_name === this.currentWorkcell)
      if (wcStations.length === 0) return []
      
      // Get 4 stations starting from currentStationPage
      const startIdx = (this.currentStationPage % Math.ceil(wcStations.length / 4)) * 4
      return wcStations.slice(startIdx, startIdx + 4)
    },
    
    allStationsForChart() {
      if (!this.currentOutputData) return [];

      const countKeys = Object.keys(this.currentOutputData.station_counts);

      const stationIdsFromCounts = countKeys.map(k =>
        Number(k.replace("station", "").replace("_qty", ""))
      );

      // Merge IDs from counts + status
      const combined = stationIdsFromCounts.map(id => {
        return (
          this.allStations.find(s => s.id === id) || 
          { id, workcell_name: this.currentWorkcell, is_running: false }
        );
      });

      return combined;
    }
  },

  mounted() {
    window.addEventListener('resize', this.handleResize)
    
    // Fetch data immediately
    this.fetchData()
    
    // Auto-refresh data every 5 minutes and rotate workcells
    this.refreshInterval = setInterval(() => {
      this.fetchData()
      if (this.allWorkcells.length > 1) {
        this.currentWorkcellIndex = (this.currentWorkcellIndex + 1) % this.allWorkcells.length
        this.currentStationPage = 0
      }
    }, 300000) // 5 minutes
    
    // Rotate stations every 5 minutes
    this.stationRotationInterval = setInterval(() => {
      const wcStations = this.allStations.filter(s => s.workcell_name === this.currentWorkcell)
      if (wcStations.length > 4) {
        this.currentStationPage = (this.currentStationPage + 1) % Math.ceil(wcStations.length / 4)
      }
      this.initBarChart()
    }, 30000) // 5 minutes
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    clearInterval(this.refreshInterval)
    clearInterval(this.stationRotationInterval)
    this.barChart?.dispose()
  },

  methods: {
    handleResize() {
      this.barChart?.resize()
    },

    getStationQty(stationId) {
      if (!this.currentOutputData || !this.currentOutputData.station_counts) return 0
      const key = `station${stationId}_qty`
      return this.currentOutputData.station_counts[key] || 0
    },

    formatTime(dateString) {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      } catch (e) {
        return dateString
      }
    },

    // Get last 4 hours data
    getLastHoursData() {
      const now = new Date()
      const hours = []
      const labels = []
      
      for (let i = 3; i >= 0; i--) {
        const hour = new Date(now)
        hour.setHours(hour.getHours() - i)
        hours.push(hour.getHours())
        labels.push(`${String(hour.getHours()).padStart(2, '0')}:00`)
      }
      
      return { hours, labels }
    },

    async fetchData() {
      this.$emit('api-loading', true)
      try {
        const response = await fetch('http://127.0.0.1:8000/api/OutputVsDailyTarget')
        if (!response.ok) throw new Error(`API error: ${response.status}`)
        const data = await response.json()
        
        console.log('API Response:', data)
        console.log('All Stations IDs:', data.status?.map(s => s.id) || [])
        
        // Parse data
        if (data.output && Array.isArray(data.output)) {
          this.allOutputData = data.output
        }
        
        if (data.status && Array.isArray(data.status)) {
          this.allStations = data.status
        }
        
        if (data.table && Array.isArray(data.table)) {
          this.allTableData = data.table
        }
        
        // Extract unique workcells
        if (this.allOutputData.length > 0) {
          this.allWorkcells = [...new Set(this.allOutputData.map(d => d.workcell))]
          this.currentWorkcellIndex = 0
          this.currentStationPage = 0
        }
        
        this.initBarChart()
        this.$emit('api-connected', true)
      } catch (error) {
        console.error('Error fetching data:', error)
        this.$emit('api-error', `Failed to load data: ${error.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    initBarChart() {
      if (!this.$refs.BarChart) return
      
      if (this.barChart) {
        this.barChart.dispose()
      }
      
      this.barChart = echarts.init(this.$refs.BarChart)

      const { labels } = this.getLastHoursData()
      const allStations = this.allStationsForChart
      const stationCounts = this.currentOutputData?.station_counts || {}

      const colors = allStations.map(() => {
        return '#' + Array.from({ length: 6 }, () =>
          Math.floor(Math.random() * 16).toString(16).toUpperCase()
        ).join('')
      })
      
      // Use jtc_quantityCompleted as the target (get first row's value)
      const targetValue = this.currentTableData[0]?.jtc_quantityCompleted || 50
      
      console.log('Target Value (from jtc_quantityCompleted):', targetValue)
      console.log('Station Counts:', stationCounts)
      console.log('Labels:', labels)
      console.log('All Stations for Chart:', allStations.map(s => s.id))

      // Generate data for ALL stations
      const series = allStations.map((station, index) => {
        const stationQty = stationCounts[`station${station.id}_qty`] || 0
        const baseValue = (stationQty / targetValue) * 100
        console.log(`ST ${station.id}: ${stationQty} qty -> ${baseValue.toFixed(2)}%`)
        return {
          name: `ST ${station.id}`,
          type: 'bar',
          data: Array(4).fill(baseValue),
          barWidth: '5%',
          itemStyle: { 
            color: colors[index % colors.length]
          }
        }
      })
      
      // Add target line at 100% based on quantityCompleted
      series.push({
        name: 'Target',
        type: 'line',
        data: Array(4).fill(100),
        itemStyle: { color: '#FFD700' },
        lineStyle: { color: '#FFD700', width: 2 }
      })

      const option = {
        title: {
          text: `${this.currentWorkcell} - Last 4 Hours Output % (${allStations.length} Stations)`,
          left: '20',
          top: '10',
          textStyle: {
            color: '#fff',
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#00baff',
          textStyle: { color: '#fff' }
        },
        legend: {
          data: series.map(s => s.name),
          top: '10',
          right: '1',
          textStyle: { color: '#fff', fontSize: 11 },
          type: 'scroll',
          orient: 'vertical',
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '60',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: { color: '#fff', fontSize: 12 },
          axisLine: { lineStyle: { color: '#444' } }
        },
        yAxis: {
          type: 'value',
          name: 'Output %',
          axisLabel: { color: '#fff', fontSize: 11 },
          axisLine: { lineStyle: { color: '#444' } },
          splitLine: { lineStyle: { color: '#333' } },
          min: 0,
          max: 120
        },
        series: series
      }

      this.barChart.setOption(option)
    }
  }
}
</script>

<style scoped>
.OutputVsDailyTarget {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
}

.OutputVsDailyTarget-title {
  padding: 20px;
  text-align: center;
  background-color: rgba(0, 186, 255, 0.1);
  border-bottom: 2px solid #00baff;
  margin-bottom: 20px;
}

.OutputVsDailyTarget-title h1 {
  font-size: 24px;
  color: #00baff;
  margin: 0;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 186, 255, 0.5);
}

.main-content {
  display: flex;
  gap: 20px;
  padding: 0 20px 20px 20px;
  flex: 1;
  height: calc(100% - 80px);
}

.left-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.bottom-chart {
  flex: 1;
  min-height: 300px;
}

.bar-box {
  width: 100%;
  height: 100%;
  background: rgba(30, 30, 40, 0.9);
  border: 2px solid #00baff;
  border-radius: 10px;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.chart {
  flex: 1;
  min-height: 250px;
  width: 100%;
}

.table-chart {
  flex: 1;
  min-height: 200px;
  max-height: 250px;
}

.table-box {
  width: 100%;
  height: 100%;
  background: rgba(30, 30, 40, 0.9);
  border: 2px solid #00baff;
  border-radius: 10px;
  padding: 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.table-title {
  font-size: 16px;
  font-weight: bold;
  color: #00baff;
  margin-bottom: 10px;
  text-align: center;
  text-transform: uppercase;
}

.table-wrapper {
  flex: 1;
  overflow-y: auto;
}

.workcell-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.workcell-table thead {
  position: sticky;
  top: 0;
  background: rgba(0, 186, 255, 0.2);
}

.workcell-table th {
  padding: 10px;
  text-align: center;
  color: #00baff;
  font-weight: bold;
  border-bottom: 1px solid #00baff;
}

.workcell-table td {
  padding: 8px;
  text-align: center;
  color: #fff;
  border-bottom: 1px solid #333;
}

.workcell-table tbody tr:hover {
  background: rgba(0, 186, 255, 0.1);
}

.station-box {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.box {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  flex: 1;
}

.details-box {
  background: rgba(30, 30, 40, 0.9);
  border: 2px solid #00baff;
  border-radius: 10px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.station-content {
  width: 100%;
  text-align: center;
}

.station-header {
  font-size: 16px;
  font-weight: bold;
  color: #00baff;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #00baff;
}

.station-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.label {
  color: #888;
  font-size: 12px;
  text-transform: uppercase;
  flex: 1;
}

.value {
  color: #fff;
  font-weight: bold;
  text-align: right;
  flex: 1;
  word-break: break-word;
}

.value.running {
  color: #4CAF50;
  animation: pulse 1s infinite;
}

.value.idle {
  color: #FF6B6B;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@media (max-width: 1400px) {
  .main-content {
    flex-direction: column;
  }

  .left-panel {
    flex: auto;
  }

  .right-panel {
    flex: auto;
  }

  .box {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 900px) {
  .box {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .box {
    grid-template-columns: 1fr;
  }

  .OutputVsDailyTarget-title h1 {
    font-size: 18px;
  }
}
</style>
