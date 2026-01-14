<template>
  <div class="app-wrapper">
    <!-- Global Connection Status Bar -->
    <div class="app-header">
      <div class="nav-wrapper">
        <button class="scroll-btn" @click="scrollNav('left')">‹</button>

        <div class="nav-buttons" ref="navContainer">
          <button @click="currentView = 'dashboard'" :class="{ active: currentView === 'dashboard' }">Output status</button>
          <button @click="currentView = 'table'" :class="{ active: currentView === 'table' }">Table E24-100-WF</button>
          <button @click="currentView = 'table2'" :class="{ active: currentView === 'table2' }">Table E25-100-WF</button>
          <button @click="currentView = 'OutputVsDailyTarget'" :class="{ active: currentView === 'OutputVsDailyTarget' }">Output vs Daily Target</button>
          <button @click="currentView = 'attendance'" :class="{ active: currentView === 'attendance' }">Attendance</button>
          <button @click="currentView = 'COCompletion'" :class="{ active: currentView === 'COCompletion' }">Customer Order Completion</button>
          <button @click="currentView = 'oee'" :class="{ active: currentView === 'oee' }">OEE by Work Cell</button>
          <button @click="currentView = 'oeebyzone'" :class="{ active: currentView === 'oeebyzone' }">OEE by Zone</button>
          <button @click="currentView = 'oeebystation'" :class="{ active: currentView === 'oeebystation' }">OEE by Station</button>
          <button @click="currentView = 'oeestationdetailedperday'" :class="{ active: currentView === 'oeestationdetailedperday' }">OEEByStationDetailedPerDay</button>
          <button @click="currentView = 'oeeranking'" :class="{ active: currentView === 'oeeranking' }">OEEByWorkCellRanking</button>
          <button @click="currentView = 'oeezoneranking'" :class="{ active: currentView === 'oeezoneranking' }">OEEByZoneRanking</button>
          <button @click="currentView = 'oeestationranking'" :class="{ active: currentView === 'oeestationranking' }">OEEByStationRanking</button>
          <button @click="currentView = 'oeerankingcombine'" :class="{ active: currentView === 'oeerankingcombine' }">OEEByWorkCellRankingCombine</button>
          <button @click="currentView = 'oeezonerankingcombine'" :class="{ active: currentView === 'oeezonerankingcombine' }">OEEByZoneRankingCombine</button>
          <button @click="currentView = 'oeestationrankingcombine'" :class="{ active: currentView === 'oeestationrankingcombine' }">OEEByStationRankingCombine</button>
          <button @click="currentView = 'uptimevsdowntime'" :class="{ active: currentView === 'uptimevsdowntime' }">Uptime vs Downtime</button>
          <button @click="currentView = 'jtcprogress'" :class="{ active: currentView === 'jtcprogress' }">JTC Progress</button>
          
        </div>

        <button class="scroll-btn" @click="scrollNav('right')">›</button>
      </div>
      
      <!-- Connection Status -->
      <div class="connection-status" :class="{ connected: apiConnected, disconnected: !apiConnected }">
        <div class="status-dot" :class="{ connected: apiConnected, disconnected: !apiConnected }"></div>
        <span>{{ apiConnected ? 'Connected' : 'Disconnected' }}</span>
      </div>
    </div>

    <!-- Global Loading Popup -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-popup">
        <div class="spinner"></div>
        <p>Loading data...</p>
      </div>
    </div>

    <!-- Global Error Popup -->
    <div v-if="errorMessage" class="error-overlay" @click="closeError">
      <div class="error-popup" @click.stop>
        <div class="error-header">
          <span class="error-title">⚠️ Error</span>
          <button class="error-close" @click="closeError">✕</button>
        </div>
        <p class="error-text">{{ errorMessage }}</p>
        <button class="error-btn" @click="closeError">Close</button>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div class="app-content">
      <component :is="currentComponent" @api-loading="setLoading" @api-error="setError" @api-connected="setConnected" />
    </div>
  </div>
</template>

<script>
import MainDashboard from './components/MainDashboard.vue'
import OEEByWorkCell from './components/OEEByWorkCell.vue'
import TableDashboard from './components/tableDashboard.vue'
import TableDashboard2 from './components/tableDashboard2.vue'
import OutputVsDailyTarget from './components/OutputVsDailyTarget.vue'
import Attendance from './components/AttendanceView.vue'
import CustomerOrderCompletion from './components/CustomerOrderCompletion.vue'
import OEEByWorkCellRanking from './components/OEEByWorkCellRanking.vue'
import OEEByWorkCellRankingCombine from './components/OEEByWorkCellRankingCombine.vue'
import OEEByZone from './components/OEEByZone.vue'
import OEEByZoneRanking from './components/OEEByZoneRanking.vue'
import OEEByZoneRankingCombine from './components/OEEByZoneRankingCombine.vue'
import OEEByStation from './components/OEEByStation.vue'
import OEEByStationRanking from './components/OEEByStationRanking.vue'
import OEEByStationRankingCombine from './components/OEEByStationRankingCombine.vue'
import UptimeVSDownTime from './components/UptimeVSDownTime.vue'
import OEEByStationDetailedPerDay from './components/OEEByStationDetailedPerDay.vue'
import JTCProgress from './components/JTCProgress.vue'

export default {
  name: 'App',
  components: {
    MainDashboard,
    TableDashboard,
    TableDashboard2,
    OEEByWorkCell,
    OEEByWorkCellRanking,
    OEEByWorkCellRankingCombine,
    OEEByZone,
    OEEByZoneRanking,
    OEEByZoneRankingCombine,
    OEEByStation,
    OEEByStationRanking,
    OEEByStationRankingCombine,
    OutputVsDailyTarget,
    Attendance,
    CustomerOrderCompletion,
    UptimeVSDownTime,
    OEEByStationDetailedPerDay,
    JTCProgress
  },
  data() {
    return {
      currentView: 'dashboard',
      isLoading: false,
      errorMessage: '',
      apiConnected: false
    }
  },
  computed: {
    currentComponent() {
      return this.currentView === 'dashboard' ? 'MainDashboard' 
      : this.currentView === 'oee' ? 'OEEByWorkCell'
      : this.currentView === 'oeeranking' ? 'OEEByWorkCellRanking'
      : this.currentView === 'oeerankingcombine' ? 'OEEByWorkCellRankingCombine'
      : this.currentView === 'oeebyzone' ? 'OEEByZone'
      : this.currentView === 'oeezoneranking' ? 'OEEByZoneRanking'
      : this.currentView === 'oeezonerankingcombine' ? 'OEEByZoneRankingCombine'
      : this.currentView === 'oeebystation' ? 'OEEByStation'
      : this.currentView === 'oeestationranking' ? 'OEEByStationRanking'
      : this.currentView === 'oeestationrankingcombine' ? 'OEEByStationRankingCombine'
      : this.currentView == 'OutputVsDailyTarget' ? 'OutputVsDailyTarget'
      : this.currentView === 'attendance' ? 'attendance'
      : this.currentView === 'COCompletion' ? 'CustomerOrderCompletion'
      : this.currentView === 'uptimevsdowntime' ? 'UptimeVSDownTime'
      : this.currentView === 'oeestationdetailedperday' ? 'OEEByStationDetailedPerDay'
      : this.currentView === 'jtcprogress' ? 'JTCProgress'
      : this.currentView === 'table' ? 'TableDashboard' : 'TableDashboard2';
    }
  },
  methods: {
    setLoading(isLoading) {
      this.isLoading = isLoading
    },
    setError(message) {
      this.errorMessage = message
    },
    setConnected(connected) {
      this.apiConnected = connected
    },
    closeError() {
      this.errorMessage = ''
    },
    scrollNav(direction) {
      const c = this.$refs.navContainer
      if (!c) return

      const amount = 200
      const maxScroll = c.scrollWidth - c.clientWidth

      if (direction === "left") {
        if (c.scrollLeft <= 0) {
          // Jump instantly to end
          c.scrollLeft = maxScroll
        } else {
          c.scrollBy({ left: -amount, behavior: "smooth" })
        }
      }

      if (direction === "right") {
        if (c.scrollLeft >= maxScroll) {
          // Jump instantly to start
          c.scrollLeft = 0
        } else {
          c.scrollBy({ left: amount, behavior: "smooth" })
        }
      }
    }
  }
}
</script>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1a1a1a;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #2e2e2e;
  padding: 10px 20px;
  border-bottom: 2px solid #444;
  gap: 20px;
}

.nav-buttons {
  display: flex;
  gap: 10px;
  flex: 1;
}

.nav-buttons button {
  padding: 10px 15px;
  border: 2px solid #666;
  background-color: #1a1a1a;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.nav-buttons button:hover {
  background-color: #3a3a3a;
  border-color: #00baff;
}

.nav-buttons button.active {
  background-color: #00baff;
  border-color: #00baff;
  color: white;
  box-shadow: 0 0 12px #00baff88;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 15px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: bold;
  border: 2px solid #666;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.connection-status.connected {
  background-color: #1a3a1a;
  border-color: #00ff00;
  color: #00ff00;
}

.connection-status.disconnected {
  background-color: #3a1a1a;
  border-color: #ff4444;
  color: #ff4444;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  animation: pulse 2s infinite;
}

.status-dot.connected {
  background-color: #00ff00;
  box-shadow: 0 0 8px #00ff0088;
}

.status-dot.disconnected {
  background-color: #ff4444;
  box-shadow: 0 0 8px #ff444488;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.app-content {
  flex: 1;
  overflow: auto;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-popup {
  background-color: #2e2e2e;
  border: 2px solid #00baff;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 0 20px #00baff44;
  min-width: 300px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #444;
  border-top: 4px solid #00baff;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-popup p {
  color: #00baff;
  font-size: 16px;
  font-weight: bold;
  margin: 0;
}

/* Error Overlay */
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.error-popup {
  background-color: #2e2e2e;
  border: 2px solid #ff6666;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 0 20px #ff666644;
  min-width: 350px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.error-title {
  color: #ff6666;
  font-size: 18px;
  font-weight: bold;
}

.error-close {
  background: none;
  border: none;
  color: #ff6666;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.3s ease;
  padding: 0;
}

.error-close:hover {
  color: #ff8888;
}

.error-text {
  color: #cccccc;
  font-size: 14px;
  margin: 15px 0;
  line-height: 1.5;
}

.error-btn {
  background-color: #ff6666;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.error-btn:hover {
  background-color: #ff8888;
  box-shadow: 0 0 10px #ff666644;
}

.nav-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 92%;
}

.scroll-btn {
  background: #1a1a1a;
  color: white;
  border: 2px solid #666;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
}

.scroll-btn:hover {
  background: #00baff;
  border-color: #00baff;
  color: black;
}

.nav-buttons {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  white-space: nowrap;
  scrollbar-width: none;  /* Firefox */
}

.nav-buttons::-webkit-scrollbar {
  display: none; /* Chrome/Edge */
}

</style>