<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY STATION (RANKING)
    </div>

    <!-- Tabs for period selection -->
    <div class="footer">
      <button 
        v-for="tab in tabs" 
        :key="tab" 
        class="tab-btn"
        :class="{ active: activePeriod === tab }"
        @click="selectPeriod(tab)">
        {{ tab }}
      </button>
    </div>

    <!-- Date Picker for DAY tab -->
    <div v-if="activePeriod === 'DAY'" class="date-picker-section">
      <input 
        type="date" 
        v-model="selectedDate" 
        class="date-input"
        @change="fetchData"
      />
    </div>

    <!-- 4 Horizontal Bar Charts in one row -->
    <div class="barGraph-container-row">
      <div ref="BarChart1" class="chart"></div>
      <div ref="BarChart2" class="chart"></div>
      <div ref="BarChart3" class="chart"></div>
      <div ref="BarChart4" class="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  data() {
    const today = new Date()
    const todayISO = today.toISOString().split('T')[0]
    return {
      refreshInterval: null,
      tabs: ['TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
      activePeriod: 'TODAY',
      selectedDate: todayISO,
      OEERanking: null,
      AvailabilityRanking: null,
      PerformanceRanking: null,
      QualityRanking: null,
    }
  },

  mounted() {
    window.addEventListener('resize', this.handleResize)

    // Fetch data immediately
    this.fetchData()

    // Auto-refresh every 5 minutes
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
    selectPeriod(period) {
      this.activePeriod = period
      this.fetchData()
    },

    handleResize() {
      [this.$refs.BarChart1, this.$refs.BarChart2, this.$refs.BarChart3, this.$refs.BarChart4].forEach(ref => {
        ref && echarts.getInstanceByDom(ref)?.resize()
      })
    },

    async fetchData() {
      this.$emit('api-loading', true)
      try {
        let endpoint = 'http://127.0.0.1:8000/api'
        let params = {}
        
        if (this.activePeriod === 'TODAY') {
          endpoint += '/OEE_by_Station_per_Day'
        } else if (this.activePeriod === 'DAY') {
          endpoint += '/OEE_by_Station_per_Day'
          params.date = this.selectedDate
        } else if (this.activePeriod === 'WEEKLY') {
          endpoint += '/OEE_by_Station_per_Week'
        } else if (this.activePeriod === 'MONTHLY') {
          endpoint += '/OEE_by_Station_per_Month'
        } else if (this.activePeriod === 'ALL TIME') {
          endpoint += '/OEE_by_Station'
        }

        const queryString = new URLSearchParams(params).toString()
        const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint
        const response = await fetch(fullUrl)
        if (!response.ok) throw new Error(`API error: ${response.status}`)
        const json = await response.json();
        const data = json.Oee || json.Oee_per_Day || json.Oee_per_Week || json.Oee_per_Month || []
        const valid = data.filter(i => i.workcell);

        const sortedOEE          = [...valid].sort((a,b)=> b.oee - a.oee);
        const sortedAvailability = [...valid].sort((a,b)=> b.availability - a.availability);
        const sortedPerformance  = [...valid].sort((a,b)=> b.performance - a.performance);
        const sortedQuality      = [...valid].sort((a,b)=> b.quality - a.quality);

        const OEEData = {
          name: sortedOEE.map(i => `${i.workcell} Zone ${i.zone} ${i.name}`),
          value: sortedOEE.map(i => i.oee)
        };
        const AVData = {
          name: sortedAvailability.map(i => `${i.workcell} Zone ${i.zone} ${i.name}`),
          value: sortedAvailability.map(i => i.availability)
        };
        const PFData = {
          name: sortedPerformance.map(i => `${i.workcell} Zone ${i.zone} ${i.name}`),
          value: sortedPerformance.map(i => i.performance)
        };
        const QLData = {
          name: sortedQuality.map(i => `${i.workcell} Zone ${i.zone} ${i.name}`),
          value: sortedQuality.map(i => i.quality)
        };

        this.OEERanking = OEEData;
        this.AvailabilityRanking = AVData;
        this.PerformanceRanking = PFData;
        this.QualityRanking = QLData;

        this.initBarCharts();
        this.$emit('api-connected', true)
      } catch (error) {
        console.error('Error fetching data:', error)
        this.$emit('api-error', `Failed to load data: ${error.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    initBarCharts() {
      const charts = [
        { ref: this.$refs.BarChart1, title: 'OEE' ,data: this.OEERanking},
        { ref: this.$refs.BarChart2, title: 'Availability', data: this.AvailabilityRanking},
        { ref: this.$refs.BarChart3, title: 'Performance', data: this.PerformanceRanking},
        { ref: this.$refs.BarChart4, title: 'Quality', data: this.QualityRanking},
      ]

      charts.forEach(({ ref, data, title }) => {
        if (!ref) return
        echarts.getInstanceByDom(ref)?.dispose()
        const chart = echarts.init(ref)

        const paired = data.value.map((val, i) => ({
          val,
          label: data.name[i] 
        }));

        paired.sort((a, b) => b.val - a.val)
        const sortedData = paired.map(p => p.val);
        const sortedLabels = paired.map(p => p.label);
        
        const individualGraphMax = Math.max(...data.value) * 1.2;

        // Color by value
        const colors = sortedData.map(v => {
          if (v >= 85) return '#4CAF50'; // green
          else if (v >= 50) return '#FFC107'; // yellow
          else return '#FF6B6B'; // red
        });

        chart.setOption({
            title: { text: title, left: 'center', textStyle: { color: '#00baff' } },
            tooltip: { trigger: 'axis' },
            grid: { left: 60, right: 20, bottom: 30, top: 40 },
            dataZoom: [
                {
                    type: 'inside',
                    yAxisIndex: 0,
                    start: 0,
                    end: Math.min(100, (10 / sortedLabels.length) * 100)
                },
                {
                    type: 'slider',
                    yAxisIndex: 0,
                    right: 0,
                    width: 10,
                    start: 0,
                    end: Math.min(100, (10 / sortedLabels.length) * 100),
                    handleSize: 8,
                    showDetail: false
                }
            ],
                xAxis: {
                type: 'value',
                axisLabel: { color: '#fff' },
                splitLine: { lineStyle: { color: '#444' } },
                max: individualGraphMax
            },
                yAxis: {
                type: 'category',
                data: sortedLabels,
                axisLabel: { color: '#00baff' },
                inverse: true,
                animationDuration: 300,
                animationDurationUpdate: 300
            },
            series: [{
                type: 'bar',
                data: sortedData.map((val, idx) => ({
                    value: val,
                    itemStyle: { color: colors[idx] }
            })),
            label: { show: true, position: 'right', color: '#fff' }
            }]
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
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  padding: 10px;
  color: white;
  height: 100vh;
}

.header {
  font-size: 24px;
  font-weight: bold;
  color: #00baff;
  text-align: center;
  text-shadow: 0 0 8px rgba(0,186,255,0.3);
}

.footer {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 10px 20px;
  border-bottom: 2px solid #333;
}

.tab-btn {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #666;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background-color: #3a3a3a;
  border-color: #00baff;
}

.tab-btn.active {
  background-color: #00baff;
  border-color: #00baff;
  color: white;
  box-shadow: 0 0 12px #00baff88;
}

.date-picker-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
  padding: 10px;
  background-color: #2e2e2e;
  border-radius: 8px;
  border: 1px solid #444;
}

.date-input {
  background-color: #1a1a1a;
  border: 2px solid #00baff;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.date-input:hover {
  border-color: #00d4ff;
  box-shadow: 0 0 8px #00baff44;
}

.date-input:focus {
  outline: none;
  border-color: #00d4ff;
  box-shadow: 0 0 12px #00baff66;
}

.barGraph-container-row {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 10px;
}

.chart {
  flex: 1;
  height: 100%;
  min-width: 0;
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 5px;
  box-sizing: border-box;
}

.chart:hover {
  border-color: #00baff;
  box-shadow: 0 0 18px rgba(0, 186, 255, 0.4);
}
</style>
