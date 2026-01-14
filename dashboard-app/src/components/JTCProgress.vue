<template>
  <div class="dashboard">
    <div class="dashboard-header-container">
      <h1 class="centered-title">JTC Progress</h1>
      <div class="global-nav">
        <button @click="prevPage" :disabled="stationPage === 0">◀ PREV STATIONS</button>
        <span class="page-indicator">PAGE {{ stationPage + 1 }} / {{ maxPages }}</span>
        <button @click="nextPage" :disabled="stationPage >= maxPages - 1">NEXT STATIONS ▶</button>
      </div>
    </div>
    
    <div class="main-content-grid">
      <div class="inventory-table-container">
        <table class="inventory-table">
          <thead>
            <tr>
              <th class="border-right">Order Number</th>
              <th v-for="(name, idx) in pagedStations" :key="name" 
                  :class="{'border-right': idx < pagedStations.length - 1}">
                {{ name }}
              </th>
              <th class="border-left">FG</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableRows" :key="row.orderNumber">
              <td class="order-cell border-right">{{ row.orderNumber }}</td>
              <td v-for="(name, idx) in pagedStations" :key="name"
                  :class="{'border-right': idx < pagedStations.length - 1}">
                {{ row[name] || '-' }}
              </td>
              <td class="border-left">-</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="top-linebar">
        <div class="linebar-box">
          <div class="linebar-title">{{ pagedStations[0] || '' }}</div>
          <div ref="chartRef0" class="chart"></div>
        </div>
      </div>

      <div class="bottom-linebars">
        <div v-for="i in 4" :key="i" class="linebar-box">
          <div class="linebar-title">{{ pagedStations[i] || '' }}</div>
          <div :ref="'chartRef' + i" class="chart"></div>
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
      progress: [],       
      progress_today: {}, 
      charts: [],
      stationPage: 0,
      stationPerPage: 5
    }
  },
  computed: {
    allStationNames() {
      if (!this.progress_today) return [];
      const names = new Set();
      Object.values(this.progress_today).forEach(group => {
        Object.values(group).forEach(item => names.add(item.stationName));
      });
      return Array.from(names);
    },
    pagedStations() {
      const start = this.stationPage * this.stationPerPage;
      return this.allStationNames.slice(start, start + this.stationPerPage);
    },
    tableRows() {
      if (!this.progress_today) return [];
      const rows = {};
      Object.values(this.progress_today).forEach(group => {
        Object.values(group).forEach(item => {
          if (!rows[item.orderNumber]) rows[item.orderNumber] = { orderNumber: item.orderNumber };
          rows[item.orderNumber][item.stationName] = item.quantity;
        });
      });
      return Object.values(rows);
    },
    maxPages() {
      return Math.ceil(this.allStationNames.length / this.stationPerPage) || 1;
    }
  },
  watch: {
    pagedStations() { this.updateCharts(); }
  },
  mounted() {
    this.initCharts();
    this.fetchData();
    window.addEventListener('resize', () => this.charts.forEach(c => c?.resize()));
  },
  methods: {
    initCharts() {
      this.charts = [];
      for (let i = 0; i < 5; i++) {
        const el = i === 0 ? this.$refs.chartRef0 : this.$refs['chartRef' + i][0];
        if (el) {
          const chart = echarts.init(el);
          this.charts.push(chart);
        }
      }
    },
    async fetchData() {
      this.$emit('api-loading', true)
      try {
        const res = await fetch('http://127.0.0.1:8000/api/JTCProgress');
        if (!res.ok) throw new Error(`API error: ${res.status}`)
        const data = await res.json();
        this.progress = data.progress || [];
        this.progress_today = data.progress_today || {};
        this.$nextTick(() => this.updateCharts());
        this.$emit('api-connected', true)
      } catch (e) { 
        console.error(e); 
        this.$emit('api-error', `Failed to load data: ${e.message}`)
        this.$emit('api-connected', false)
      } finally {
        this.$emit('api-loading', false)
      }
    },

    updateCharts() {
      // FORCE 4 CONSECUTIVE DATES (End at current time)
      const last4Dates = [];
      for (let i = 3; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        last4Dates.push(d.toISOString().split('T')[0]);
      }

      this.charts.forEach((chart, index) => {
        const name = this.pagedStations[index];

        const stationData = this.progress.filter(p => p.name === name);
        const labels = [];
        const actuals = [];
        const targets = [];

        last4Dates.forEach(dateStr => {
          const match = stationData.find(p => p.jtc_actualEndDate?.startsWith(dateStr));
          const dateObj = new Date(dateStr);
          
          labels.push(dateObj.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }));
          actuals.push(match ? (match.quantity || 0) : 0);
          targets.push(name ? (match ? match.jtc_quantityNeeded : 50) : 0);
        });

        chart.setOption({
          legend: { show: true, textStyle: { color: '#fff', fontSize: 10 }, top: '0%', itemWidth: 15 },
          tooltip: { trigger: 'axis' },
          grid: { top: 35, bottom: 20, left: 30, right: 10, containLabel: true },
          xAxis: { 
            type: 'category', 
            data: labels, 
            axisLabel: { color: '#fff', fontSize: 9, interval: 0 },
            axisTick: { alignWithLabel: true }
          },
          yAxis: { 
            type: 'value', 
            min: 0,
            max: 60,
            axisLabel: { color: '#fff', fontSize: 9 },
            splitLine: { lineStyle: { color: '#444' } }
          },
          series: [
            { 
                name: 'Actual', 
                type: 'bar', 
                data: actuals, 
                itemStyle: { 
                    color: '#F52727' 
                }, 
                barMaxWidth: 15,
                showBackground: true,
                backgroundStyle: { color: 'rgba(180, 180, 180, 0.1)'}
            },
            { name: 'Target', type: 'line', data: targets, itemStyle: { color: '#FFEB3B' }, symbolSize: 4, coonectNulls: true }
          ]
        }, true);
      });
    },
    prevPage() { if (this.stationPage > 0) this.stationPage--; },
    nextPage() { if (this.stationPage < this.maxPages - 1) this.stationPage++; }
  }
}
</script>

<style scoped>
.dashboard { 
  background: #1a1a1a; 
  color: white; 
  height: 100vh; 
  width: 100vw;
  padding: 10px; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  box-sizing: border-box;
}

.dashboard-header-container { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  margin-bottom: 5px; 
  flex-shrink: 0;
}

.centered-title {
    color: #00baff; 
    font-size: 1.8rem; 
    margin: 0; 
    text-transform: uppercase; 
}

.global-nav { 
    display: flex; 
    gap: 10px; 
    margin-top: 2px; 
    align-items: center; 
}

.global-nav button { 
    background: #00baff; 
    padding: 4px 10px; 
    border: none; 
    font-weight: bold; 
    cursor: pointer; 
    border-radius: 4px; 
    font-size: 0.8rem; 
}

.page-indicator { 
    font-size: 0.8rem; 
}

.main-content-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  grid-template-rows: 1fr 1fr;
  gap: 15px; 
  row-gap: 20px;
  flex: 1; 
  min-height: 0; 
  margin-top: 10px;
}

/* Table container takes up 3 columns */
.inventory-table-container { 
  grid-column: 1 / 4; 
  background: white; 
  border-radius: 4px; 
  overflow-y: auto; 
  max-height: 100%;
  border: 1px solid #512f87;
}

.inventory-table { 
  width: 100%; 
  border-collapse: collapse; 
  color: #333; 
  font-size: 16px; /* Scaled down slightly to fit more rows */
}

.inventory-table th { 
  background: #7b2cbf; 
  color: white; 
  padding: 8px; 
  position: sticky; 
  top: 0; 
  font-size: 12px;
}

.inventory-table td { 
  padding: 6px; 
  text-align: center; 
  font-weight: bold; 
  border-bottom: 1px solid #ddd; 
}

/* Header Separator Lines */
.border-right { border-right: 2px solid rgba(255,255,255,0.3) !important; }
.inventory-table td.border-right { border-right: 1px solid #ddd !important; }

/* Chart Styling */
.linebar-box { 
  background: #2e2e2e; 
  padding: 10px; 
  border-radius: 4px; 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  box-sizing: border-box;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}

.linebar-title { 
    color: #00baff; 
    font-size: 11px; 
    text-align: center; 
    font-weight: bold; 
    margin-bottom: 2px; 
}

.chart { 
    flex: 1; 
    width: 100%; 
    min-height: 0; 
}

.top-linebar { 
    grid-column: 4 / 5; 
    height: 100%; 
}

.bottom-linebars { 
  grid-column: 1 / 5; 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 15px; 
  height: 100%;
}
</style>