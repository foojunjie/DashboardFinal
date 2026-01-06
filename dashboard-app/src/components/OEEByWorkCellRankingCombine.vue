<template>
  <div class="dashboard-container">
    <div class="header">OEE by Workcell (Ranking)</div>
    <div ref="BarChart1" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  data() {
    return {
      refreshInterval: null,
      chartInstance: null
    }
  },

  mounted() {
    this.fetchData()
    window.addEventListener("resize", this.resizeChart)

    this.refreshInterval = setInterval(() => {
      this.fetchData()
    }, 300000) // 5 mins
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.resizeChart)
    clearInterval(this.refreshInterval)
    this.chartInstance?.dispose()
  },

  methods: {
    resizeChart() {
      this.chartInstance?.resize()
    },

    async fetchData() {
        this.$emit('api-loading', true)
        try {
            const res = await fetch("http://127.0.0.1:8000/api/OEE_by_WorkCell")
            if (!res.ok) throw new Error("API error")
            const json = await res.json()

            const data = json.Oee.filter(i => i.workcell)

            const sorted = data.sort((a, b) => {
              // sort by OEE first
              if (b.oee !== a.oee) return b.oee - a.oee
              // if OEE same, then Availability
              if (b.availability !== a.availability) return b.availability - a.availability
              // if still same, then Performance
              if (b.performance !== a.performance) return b.performance - a.performance
              // finally, Quality
              return b.quality - a.quality
            })

            const labels        = sorted.map(i => i.workcell)
            const oee           = sorted.map(i => i.oee)
            const availability  = sorted.map(i => i.availability)
            const performance   = sorted.map(i => i.performance)
            const quality       = sorted.map(i => i.quality)

            // 📊 Draw chart
            this.initBarChart(labels, oee, availability, performance, quality)
            this.$emit('api-connected', true)
        } catch (err) {
            console.error("Fetch Error:", err)
            this.$emit('api-error', `Failed to load data: ${err.message}`)
            this.$emit('api-connected', false)
        }finally {
            this.$emit('api-loading', false)
        }
    },

    initBarChart(labels, oee, availability, performance, quality) {
      if (this.chartInstance) this.chartInstance.dispose()
      this.chartInstance = echarts.init(this.$refs.BarChart1)

      const option = {
        tooltip: { trigger: "axis" },
        legend: {
            data: ["OEE", "Availability", "Performance", "Quality"],
            textStyle: { color: "#fff" },
            bottom: -5,          // 👈 moves it below the chart near bottom
            left: "center"
        },
        grid: { left: 120, right: 40, top: 50, bottom: 30 },
        xAxis: {
            type: "value",
            max: 300,
            axisLabel: { color: "#fff", formatter: "{value} %" }
        },
        yAxis: {
            type: "category",
            data: labels,
            axisLabel: { color: "#00baff" },
            inverse: true
        },
        series: [
          {
            name: "OEE",
            type: "bar",
            stack: "total",
            data: oee,
            itemStyle: { color: "#4CAF50" },
            label: { show: true, position: "inside", formatter: "{c}%", color: "#fff"}
          },
          {
            name: "Availability",
            type: "bar",
            stack: "total",
            data: availability,
            itemStyle: { color: "#1E88E5" },
            label: { show: true, position: "inside", formatter: "{c}%", color: "#fff"}
          },
          {
            name: "Performance",
            type: "bar",
            stack: "total",
            data: performance,
            itemStyle: { color: "#FFC107" },
            label: { show: true, position: "inside", formatter: "{c}%", color: "#fff"}
          },
          {
            name: "Quality",
            type: "bar",
            stack: "total",
            data: quality,
            itemStyle: { color: "#FF6B6B" },
            label: { show: true, position: "inside", formatter: "{c}%", color: "#fff"}
          }
        ]
      }

      this.chartInstance.setOption(option)
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
  height: 90vh;
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
  height: 90%;
  gap: 10px;
}

.chart {
  flex: 1;
  height: 90%;
  min-width: 0;
  background: #2e2e2e;
  border-radius: 6px;
  padding: 5px;
}
</style>
