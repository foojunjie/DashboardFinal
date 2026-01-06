<template>
  <div class="dashboard-container">
    <div class="header">OEE by Station (Ranking)</div>
    <div class="chart-scroll-container">
      <div ref="BarChart1" class="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import { nextTick } from "vue";

export default {
  data() {
    return {
      refreshInterval: null,
      chartInstance: null
    };
  },

  mounted() {
    this.fetchData();
    window.addEventListener("resize", this.resizeChart);

    this.refreshInterval = setInterval(() => {
      this.fetchData();
    }, 300000); // refresh every 5 mins
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.resizeChart);
    clearInterval(this.refreshInterval);
    this.chartInstance?.dispose();
  },

  methods: {
    resizeChart() {
      this.chartInstance?.resize();
    },

    async fetchData() {
      this.$emit("api-loading", true);
      try {
        const res = await fetch("http://127.0.0.1:8000/api/OEE_by_Station");
        if (!res.ok) throw new Error("API error");
        const json = await res.json();

        const data = json.Oee.filter(i => i.workcell);

        const sorted = data.sort((a, b) => {
          if (b.oee !== a.oee) return b.oee - a.oee;
          if (b.availability !== a.availability) return b.availability - a.availability;
          if (b.performance !== a.performance) return b.performance - a.performance;
          return b.quality - a.quality;
        });

        const labels = sorted.map(i => `${i.workcell} Zone ${i.zone} ${i.name}`);
        const oee = sorted.map(i => i.oee);
        const availability = sorted.map(i => i.availability);
        const performance = sorted.map(i => i.performance);
        const quality = sorted.map(i => i.quality);

        this.initBarChart(labels, oee, availability, performance, quality);
        this.$emit("api-connected", true);
      } catch (err) {
        console.error("Fetch Error:", err);
        this.$emit("api-error", `Failed to load data: ${err.message}`);
        this.$emit("api-connected", false);
      } finally {
        this.$emit("api-loading", false);
      }
    },

    initBarChart(labels, oee, availability, performance, quality) {
      if (!this.chartInstance) {
        this.chartInstance = echarts.init(this.$refs.BarChart1);
      }

      // Set chart height dynamically based on number of labels
      const barHeight = 50; // px per bar (adjustable)
      const chartHeight = labels.length * barHeight;
      this.$refs.BarChart1.style.height = `${chartHeight}px`;

      const option = {
        tooltip: { trigger: "axis" },
        legend: {
          data: ["OEE", "Availability", "Performance", "Quality"],
          textStyle: { color: "#fff" },
          bottom: -5,
          left: "center"
        },
        grid: { left: 120, right: 40, top: 50, bottom: 30 },
        xAxis: {
          type: "value",
          min: 0,
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
          { name: "OEE", type: "bar", stack: "total", data: oee, itemStyle: { color: "#4CAF50" }, label: { show: true, position: "inside", color: "#fff", formatter: "{c}%" } },
          { name: "Availability", type: "bar", stack: "total", data: availability, itemStyle: { color: "#1E88E5" }, label: { show: true, position: "inside", color: "#fff", formatter: "{c}%" } },
          { name: "Performance", type: "bar", stack: "total", data: performance, itemStyle: { color: "#FFC107" }, label: { show: true, position: "inside", color: "#fff", formatter: "{c}%" } },
          { name: "Quality", type: "bar", stack: "total", data: quality, itemStyle: { color: "#FF6B6B" }, label: { show: true, position: "inside", color: "#fff", formatter: "{c}%" } }
        ]
      };

      nextTick(() => {
        this.chartInstance.resize();
        this.chartInstance.setOption(option);
      });
    }
  }
};
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

/* Scrollable container */
.chart-scroll-container {
  max-height: 100%; /* visible area */
  overflow-y: auto;
}

/* Chart grows dynamically */
.chart {
  width: 100%;
  min-height: 600px; /* minimum height */
  background: #2e2e2e;
  border-radius: 6px;
  padding: 5px;
}
</style>
