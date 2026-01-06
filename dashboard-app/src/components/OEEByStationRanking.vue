<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY STATION (RANKING)
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
    return {
      refreshInterval: null,
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
    handleResize() {
      [this.$refs.BarChart1, this.$refs.BarChart2, this.$refs.BarChart3, this.$refs.BarChart4].forEach(ref => {
        ref && echarts.getInstanceByDom(ref)?.resize()
      })
    },

    async fetchData() {
      this.$emit('api-loading', true)
      try {
      const response = await fetch('http://127.0.0.1:8000/api/OEE_by_Station')
      if (!response.ok) throw new Error(`API error: ${response.status}`)
      const json = await response.json();
      const data = json.Oee

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
  background: #1a1a1a;
  padding: 10px;
  color: white;
  height: 80vh;
}

.header {
  font-size: 24px;
  font-weight: bold;
  color: #00baff;
  text-align: center;
  text-shadow: 0 0 8px rgba(0,186,255,0.3);
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
  background: #2e2e2e;
  border-radius: 6px;
  padding: 5px;
}
</style>
