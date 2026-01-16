<template>
  <div class="dashboard-container">
    <div class="header">OEE by Station (Ranking)</div>    
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
    const today = new Date()
    const todayISO = today.toISOString().split('T')[0]
    return {
      refreshInterval: null,
      tabs: ['TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
      activePeriod: 'TODAY',
      selectedDate: todayISO,
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
    selectPeriod(period) {
      this.activePeriod = period
      this.fetchData()
    },

    resizeChart() {
      this.chartInstance?.resize();
    },

    async fetchData() {
      this.$emit("api-loading", true);
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
        const res = await fetch(fullUrl);
        if (!res.ok) throw new Error("API error");
        const json = await res.json();

        const data = json.Oee || json.Oee_per_Day || json.Oee_per_Week || json.Oee_per_Month || []
        const filtered = data.filter(i => i.workcell);

        const sorted = filtered.sort((a, b) => {
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
          max: 400,
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
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
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
  margin: 10px 0;
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

/* Scrollable container */
.chart-scroll-container {
  max-height: 100%; /* visible area */
  overflow-y: auto;
}

/* Chart grows dynamically */
.chart {
  width: 100%;
  min-height: 600px; /* minimum height */
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 5px;
}

.chart:hover {
  border-color: #00baff;
  box-shadow: 0 0 18px rgba(0, 186, 255, 0.4);
}
</style>
