<template>
  <div class="dashboard-container">
    <!-- Header with Navigation -->
    <div class="header-section">
      <button class="nav-btn" @click="previousWorkcell" v-if="filteredData.length > 0">◀</button>
      <div class="header">
        {{ currentWorkcellLabel }}
      </div>
      <button class="nav-btn" @click="nextWorkcell" v-if="filteredData.length > 0">▶</button>
    </div>

    <div class="barGraph-container">
      <div class="column">
        <div class="chart-card">
          <div class="card-title">{{ chartData.lineTop.title }}</div>
          <div ref="BarChart1" class="line-barchart"></div>
        </div>
        <div class="chart-card">
          <div class="card-title">{{ chartData.barTop.title }}</div>
          <div ref="BarChart2" class="chart"></div>
        </div>
      </div>

      <div class="column">
        <div class="chart-card">
          <div class="card-title">{{ chartData.lineBottom.title }}</div>
          <div ref="BarChart3" class="line-barchart"></div>
        </div>
        <div class="chart-card">
          <div class="card-title">{{ chartData.barBottom.title }}</div>
          <div ref="BarChart4" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  data() {
    return {
      refreshInterval: null,
      currentWorkcellIndex: 0,
      rawApiData: [],
      filteredData: [],
      chartData: {
        barTop: {
          title: 'Down Time Categories (Daily)',
          name: [],
          value: []
        },
        barBottom: {
          title: 'Down Time Categories (Hourly)',
          name: [],
          value: []
        },
        lineTop: {
          title: 'Uptime (Daily)',
          legend: [],
          barValue: [],
          lineValue: []
        },
        lineBottom: {
          title: 'Uptime (Hourly)',
          legend: [],
          barValue: [],
          lineValue: []
        }
      }
    }
  },

  computed: {
    currentWorkcellLabel() {
      if (this.filteredData.length === 0) return 'UPTIME VS DOWNTIME'
      const current = this.filteredData[this.currentWorkcellIndex]
      return `${current.workcell} Zone ${current.zone}`
    }
  },

  mounted() {
    window.addEventListener('resize', this.handleResize)
    this.fetchData()
    this.refreshInterval = setInterval(() => {
      this.fetchData()
    }, 300000) // 5 minutes
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    clearInterval(this.refreshInterval)
    ;[this.$refs.BarChart1, this.$refs.BarChart2, this.$refs.BarChart3, this.$refs.BarChart4].forEach(ref => {
      ref && echarts.getInstanceByDom(ref)?.dispose()
    })
  },

  methods: {
    handleResize() {
      [this.$refs.BarChart1, this.$refs.BarChart2, this.$refs.BarChart3, this.$refs.BarChart4].forEach(ref => {
        ref && echarts.getInstanceByDom(ref)?.resize()
      })
    },

    getDateLabels() {
      const labels = []
      const today = new Date()
      for (let i = 3; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        labels.push(`${month}-${day}`)
      }
      return labels
    },

    getHourLabels() {
      const labels = []
      const now = new Date()
      const currentHour = now.getHours()
      for (let i = 3; i >= 0; i--) {
        const hour = (currentHour - i + 24) % 24
        labels.push(`${String(hour).padStart(2, '0')}:00`)
      }
      return labels
    },

    previousWorkcell() {
      if (this.currentWorkcellIndex > 0) {
        this.currentWorkcellIndex--
        this.updateCharts()
      }
    },

    nextWorkcell() {
      if (this.currentWorkcellIndex < this.filteredData.length - 1) {
        this.currentWorkcellIndex++
        this.updateCharts()
      }
    },

    async fetchData() {
      this.$emit('api-loading', true)
      try {
        const response = await fetch('http://127.0.0.1:8000/api/UpTimeVSDownTime')
        if (!response.ok) throw new Error(`API error: ${response.status}`)
        const json = await response.json()
        
        if (json && json.UptimeVSDownTime) {
          this.rawApiData = json.UptimeVSDownTime
          this.groupByWorkcellZone()
          this.currentWorkcellIndex = 0
          this.updateCharts()
        }

        this.$emit('api-connected', true)
      } catch (error) {
        console.error('Error fetching data:', error)
        this.$emit('api-error', `Failed to load data: ${error.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    groupByWorkcellZone() {
      const grouped = {}
      this.rawApiData.forEach(station => {
        const key = `${station.workcell}|${station.zone}`
        if (!grouped[key]) {
          grouped[key] = {
            workcell: station.workcell,
            zone: station.zone,
            stations: []
          }
        }
        grouped[key].stations.push(station)
      })
      this.filteredData = Object.values(grouped)
    },

    updateCharts() {
      if (this.filteredData.length === 0) return
      
      const currentGroup = this.filteredData[this.currentWorkcellIndex]
      const downtimeCategories = ['qc', 'mp', 'ms', 'mc', 'me', 'bt']
      const categoryLabels = {
        'qc': 'Quality Check',
        'mp': 'Man Power Check',
        'ms': 'Machine Setup',
        'mc': 'Material Check',
        'me': 'Machine Error',
        'bt': 'Break Time'
      }

      // Color palette for different stations
      const colors = [
        '#00baff', '#00ff00', '#ff6b6b', '#ffa500', '#9966ff', 
        '#00ffcc', '#ffff00', '#ff00ff', '#00ff99', '#ff0066'
      ]

      // Daily uptime - collect per station and day
      const dailyUptimeSeries = currentGroup.stations.map((station, idx) => ({
        name: station.name,
        data: station.daily_uptime.map(d => d.uptime || 0),
        color: colors[idx % colors.length]
      }))

      // Daily downtime totals (sum of uptime across stations for each day)
      const dailyDowntimeTotals = [0, 0, 0, 0]
      currentGroup.stations.forEach(station => {
        station.daily_uptime.forEach((day, dayIdx) => {
          dailyDowntimeTotals[dayIdx] += day.uptime || 0
        })
      })

      // Hourly uptime - collect per station and hour
      const hourlyUptimeSeries = currentGroup.stations.map((station, idx) => ({
        name: station.name,
        data: station.hourly_uptime.map(h => h.uptime || 0),
        color: colors[idx % colors.length]
      }))

      // Hourly downtime totals (sum of uptime across stations for each hour)
      const hourlyDowntimeTotals = [0, 0, 0, 0]
      currentGroup.stations.forEach(station => {
        station.hourly_uptime.forEach((hour, hourIdx) => {
          hourlyDowntimeTotals[hourIdx] += hour.uptime || 0
        })
      })

      // Daily downtime categories (sum of qc, mp, etc. for today)
      const dailyDowntimeCategories = {
        qc: 0, mp: 0, ms: 0, mc: 0, me: 0, bt: 0
      }
      currentGroup.stations.forEach(station => {
        dailyDowntimeCategories.qc += station.qc || 0
        dailyDowntimeCategories.mp += station.mp || 0
        dailyDowntimeCategories.ms += station.ms || 0
        dailyDowntimeCategories.mc += station.mc || 0
        dailyDowntimeCategories.me += station.me || 0
        dailyDowntimeCategories.bt += station.bt || 0
      })

      // Hourly downtime categories (from last hour)
      const hourlyDowntimeCategories = {
        qc: 0, mp: 0, ms: 0, mc: 0, me: 0, bt: 0
      }
      currentGroup.stations.forEach(station => {
        if (station.hourly_uptime.length > 3) {
          const lastHour = station.hourly_uptime[3]
          hourlyDowntimeCategories.qc += lastHour.qc || 0
          hourlyDowntimeCategories.mp += lastHour.mp || 0
          hourlyDowntimeCategories.ms += lastHour.ms || 0
          hourlyDowntimeCategories.mc += lastHour.mc || 0
          hourlyDowntimeCategories.me += lastHour.me || 0
          hourlyDowntimeCategories.bt += lastHour.bt || 0
        }
      })

      // Prepare chart data - Daily Uptime
      const maxDailyUptime = Math.max(...dailyDowntimeTotals, 1)
      const dailyPerformancePercent = dailyDowntimeTotals.map(v => Math.round((v / maxDailyUptime) * 100))

      this.chartData.lineTop = {
        title: 'Uptime (Daily - Last 4 Days)',
        legend: dailyUptimeSeries.map(s => s.name),
        xaxis: this.getDateLabels(),
        barValue: dailyUptimeSeries.map(s => s.data),
        lineValue: dailyPerformancePercent,
        colors: dailyUptimeSeries.map(s => s.color)
      }

      // Daily downtime bar chart
      const dailyDowntimeValues = Object.values(dailyDowntimeCategories)
      const dailyMaxValue = Math.max(...dailyDowntimeValues, 1)
      this.chartData.barTop = {
        title: 'Down Time Categories (Daily - Today)',
        categories: downtimeCategories,
        categoryLabels: categoryLabels,
        value: dailyDowntimeValues,
        maxValue: dailyMaxValue * 1.2
      }

      // Hourly uptime
      const maxHourlyUptime = Math.max(...hourlyDowntimeTotals, 1)
      const hourlyPerformancePercent = hourlyDowntimeTotals.map(v => Math.round((v / maxHourlyUptime) * 100))

      this.chartData.lineBottom = {
        title: 'Uptime (Hourly - Last 4 Hours)',
        legend: hourlyUptimeSeries.map(s => s.name),
        xaxis: this.getHourLabels(),
        barValue: hourlyUptimeSeries.map(s => s.data),
        lineValue: hourlyPerformancePercent,
        colors: hourlyUptimeSeries.map(s => s.color)
      }

      // Hourly downtime bar chart
      const hourlyDowntimeValues = Object.values(hourlyDowntimeCategories)
      const hourlyMaxValue = Math.max(...hourlyDowntimeValues, 1)
      this.chartData.barBottom = {
        title: 'Down Time Categories (Hourly - Last Hour)',
        categories: downtimeCategories,
        categoryLabels: categoryLabels,
        value: hourlyDowntimeValues,
        maxValue: hourlyMaxValue * 1.2
      }

      this.$nextTick(() => {
        this.initLineBarCharts()
        this.initBarCharts()
      })
    },

    initBarCharts() {
      const charts = [
        { ref: this.$refs.BarChart2, key: 'barTop' },
        { ref: this.$refs.BarChart4, key: 'barBottom' }
      ]

      // Color palette for bar categories
      const barColors = [
        '#00baff',  // QC - Quality Check
        '#00ff00',  // MP - Man Power
        '#ff6b6b',  // MS - Machine Setup
        '#ffa500',  // MC - Material Check
        '#9966ff',  // ME - Machine Error
        '#00ffcc'   // BT - Break Time
      ]

      charts.forEach(({ ref, key }) => {
        if (!ref) return
        echarts.getInstanceByDom(ref)?.dispose()
        const chart = echarts.init(ref)
        const data = this.chartData[key]

        const categoryLabels = {
          'qc': 'Quality Check',
          'mp': 'Man Power',
          'ms': 'Machine Setup',
          'mc': 'Material Check',
          'me': 'Machine Error',
          'bt': 'Break Time'
        }

        chart.setOption({
          title: { text: data.title, left: 'center', textStyle: { color: '#00baff' } },
          tooltip: { trigger: 'axis' },
          grid: { left: 120, right: 40, bottom: 30, top: 40 },
          xAxis: {
            type: 'value',
            axisLabel: { color: '#fff' },
            splitLine: { lineStyle: { color: '#444' } },
            max: data.maxValue
          },
          yAxis: {
            type: 'category',
            data: data.categories.map(cat => categoryLabels[cat]),
            axisLabel: { color: '#00baff' },
            inverse: true,
            animationDuration: 300,
            animationDurationUpdate: 300
          },
          series: [{
            type: 'bar',
            data: data.value.map((v, idx) => ({ 
              value: v, 
              itemStyle: { color: barColors[idx % barColors.length] } 
            })),
            label: { show: true, position: 'right', color: '#fff' }
          }]
        })
      })
    },

    initLineBarCharts() {
      const charts = [
        { ref: this.$refs.BarChart1, key: 'lineTop' },
        { ref: this.$refs.BarChart3, key: 'lineBottom' }
      ]

      charts.forEach(({ ref, key }) => {
        if (!ref) return
        echarts.getInstanceByDom(ref)?.dispose()
        const chart = echarts.init(ref)
        const data = this.chartData[key]

        const seriesData = data.legend.map((stationName, idx) => ({
          name: stationName,
          type: 'bar',
          data: data.barValue[idx],
          itemStyle: { color: data.colors[idx] }
        }))

        seriesData.push({
          name: 'Uptime',
          type: 'line',
          data: data.lineValue,
          lineStyle: { color: '#ffa500', width: 2 },
          itemStyle: { color: '#ffa500' },
          smooth: true,
          yAxisIndex: 1
        })

        chart.setOption({
          title: { text: data.title, left: 'center', textStyle: { color: '#00baff' } },
          tooltip: { trigger: 'axis' },
          legend: { 
            data: [...data.legend, 'Uptime'],
            textStyle: { color: '#00baff' },
            bottom: 0
          },
          grid: { left: 60, right: 20, bottom: 60, top: 40 },
          xAxis: {
            type: 'category',
            axisLabel: { color: '#fff' },
            splitLine: { lineStyle: { color: '#444' } },
            data: data.xaxis
          },
          yAxis: [
            {
              type: 'value',
              axisLabel: { color: '#00baff' },
              animationDuration: 300,
              animationDurationUpdate: 300
            },
            {
              type: 'value',
              max: 100,
              position: 'right',
              axisLabel: { color: '#ffa500', formatter: '{value}%' },
              splitLine: { show: false }
            }
          ],
          series: seriesData
        })
      })
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #1a1a1a;
  padding: 10px;
  color: white;
  height: 80vh;
}

.header-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.header {
  font-size: 24px;
  font-weight: bold;
  color: #00baff;
  text-align: center;
  text-shadow: 0 0 8px rgba(0,186,255,0.3);
  flex: 1;
}

.nav-btn {
  background: #00baff;
  border: none;
  color: #1a1a1a;
  font-size: 20px;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.nav-btn:hover {
  background: #0099cc;
  transform: scale(1.1);
}

.nav-btn:active {
  transform: scale(0.95);
}

.barGraph-container-row {
  display: none;
}

.barGraph-container {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 10px;
}

.column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #2e2e2e;
  border-radius: 6px;
  padding: 6px;
}

.card-title {
  color: #00baff;
  font-weight: 600;
  margin-bottom: 6px;
  text-align: center;
}

.chart {
  flex: 1;
  height: 100%;
  min-width: 0;
  background: #2e2e2e;
  border-radius: 6px;
  padding: 5px;
}

.line-barchart {
  flex: 1;
  height: 100%;
  min-width: 0;
  background: #2e2e2e;
  border-radius: 6px;
  padding: 5px;
}
</style>
