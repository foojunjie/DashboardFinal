<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY WorkCell (OVERALL)
    </div>

    <!-- Date Picker for DAY tab -->
    <div v-if="activePeriod === 'DAY'" class="date-picker-section">
      <input 
        type="date" 
        v-model="selectedDate" 
        class="date-input"
        @change="fetchDayData"
      />
    </div>

    <div v-if="wcList.length > 8" class="nav-controls">
        <button class="swipe-btn" @click="prevBoxes">◀ PREV</button>
        
        <div class="page-indicator">
            <span class="current">{{ boxStartIndex + 1 }}-{{ Math.min(boxStartIndex + 8, wcList.length) }}</span>
            <span class="total">of {{ wcList.length }}</span>
        </div>

        <button class="swipe-btn" @click="nextBoxes">NEXT ▶</button>
    </div>

    <div class="boxes-grid">
      <div class="row">
        <WCBox 
          v-for="wc in topRow" 
          :key="wc.id + '-' + activePeriod" 
          :wc="wc" 
          :period="activePeriod" 
        />
      </div>
      <div class="row">
        <WCBox 
          v-for="wc in bottomRow" 
          :key="wc.id + '-' + activePeriod" 
          :wc="wc" 
          :period="activePeriod" 
        />
      </div>
    </div>

    <!-- Footer with Tabs -->
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
  </div>
</template>

<script>
import WCBox from './WCBox.vue'

export default {
  components: { WCBox },
  data() {
    const today = new Date()
    const todayISO = today.toISOString().split('T')[0]
    return {
      boxStartIndex: 0,
      tabs: ['TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
      activePeriod: 'ALL TIME',
      selectedDate: todayISO,
      refreshInterval: null,
      wcList: []
    }
  },
  mounted() {
    // Load initial data with TODAY period on mount
    this.fetchPeriodData(this.activePeriod)
    
    // Start auto-refresh every 5 minutes
    this.refreshInterval = setInterval(() => {
      if (this.activePeriod !== 'FAKE') {
        console.log('Auto-refreshing data...')
        if (this.activePeriod === 'DAY') {
          this.fetchDayData()
        } else {
          this.fetchPeriodData(this.activePeriod)
        }
      }
    }, 5 * 60 * 1000) // 5 minutes in milliseconds
    setInterval(() => {
            this.loadStatus()
        }, 30 * 1000) // every 30 seconds
  },
  beforeUnmount() {
    // Clear interval on component unmount
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  computed: {
    currentSet() {
      return this.wcList || [];
    },
    topRow() {
      return this.currentSet.slice(this.boxStartIndex, this.boxStartIndex + 4);
    },
    bottomRow() {
      return this.currentSet.slice(this.boxStartIndex + 4, this.boxStartIndex + 8);
    }
  },
  methods: {
    sortWcList() {
      // Sort by workcellID
      this.wcList.sort((a, b) => {
        if (a.workcellID !== b.workcellID) return a.workcellID - b.workcellID
        return a.sequence - b.sequence
      })
    },
    nextBoxes() {
      if (this.boxStartIndex + 8 >= this.wcList.length) {
        this.boxStartIndex = 0;
      } else {
        this.boxStartIndex += 8;
      }
    },
    prevBoxes() {
      if (this.boxStartIndex - 8 < 0) {
        this.boxStartIndex = Math.floor((this.wcList.length - 1) / 8) * 8;
      } else {
        this.boxStartIndex -= 8;
      }
    },
    selectPeriod(period) {
      this.activePeriod = period
      this.boxStartIndex = 0;
      if (period === 'DAY') {
        // Load today's data when DAY tab is selected
        this.fetchDayData()
      } else {
        this.fetchPeriodData(period)
      }
    },
    fetchDayData() {
      this.fetchPeriodData('DAY', this.selectedDate)
    },
    async fetchPeriodData(period, dateParam) {
      this.$emit('api-loading', true)
      this.$emit('api-error', '')
      
      try {
        let endpoint = 'http://127.0.0.1:8000/api'
        let params = {}

        if (period === 'TODAY') {
          endpoint += '/OEE_by_WorkCell_per_Day'
        } else if (period === 'DAY') {
          endpoint += '/OEE_by_WorkCell_per_Day'
          params.date = dateParam
        } else if (period === 'WEEKLY') {
          endpoint += '/OEE_by_WorkCell_per_Week'
        } else if (period === 'MONTHLY') {
          endpoint += '/OEE_by_WorkCell_per_Month'
        } else if (period === 'ALL TIME') {
          endpoint += '/OEE_by_WorkCell'
        }

        // Build query string
        const queryString = new URLSearchParams(params).toString()
        const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint

        const response = await fetch(fullUrl)
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const data = await response.json()
        
        // Normalize response and map API data to wcList format
        let apiData = []
        
        // Handle new API format: { Oee_per_Month/Week/Day: { workcell, oee, availability, performance, quality, weekly/monthly/daily/hourly } }
        if (data.Oee_per_Month && !Array.isArray(data.Oee_per_Month)) {
          // Single object wrapped - convert to array
          apiData = [data.Oee_per_Month]
        } else if (data.Oee_per_Week && !Array.isArray(data.Oee_per_Week)) {
          apiData = [data.Oee_per_Week]
        } else if (data.Oee_per_Day && !Array.isArray(data.Oee_per_Day)) {
          apiData = [data.Oee_per_Day]
        } else if (data.Oee && !Array.isArray(data.Oee)) {
          apiData = [data.Oee]
        }
        // Handle array formats
        else if (Array.isArray(data)) {
          apiData = data
        } else if (data.data && Array.isArray(data.data)) {
          apiData = data.data
        } else if (data.wcList && Array.isArray(data.wcList)) {
          apiData = data.wcList
        } else if (data.Oee_per_Month && Array.isArray(data.Oee_per_Month)) {
          apiData = data.Oee_per_Month
        } else if (data.Oee_per_Day && Array.isArray(data.Oee_per_Day)) {
          apiData = data.Oee_per_Day
        } else if (data.Oee && Array.isArray(data.Oee)) {
          apiData = data.Oee
        } else if (data.Oee_per_Week && Array.isArray(data.Oee_per_Week)) {
          apiData = data.Oee_per_Week
        } else {
          throw new Error('Unexpected API response format')
        }

        // Map API response to wcList format
        // API returns: { workcell, availability, performance, quality, oee, weekly/monthly/daily/hourly: [...] }
        this.wcList = apiData.map((item, index) => {
          // Determine which data array to use based on period
          let chartData = Array(24).fill(0)
          
          if (period === 'TODAY' || period === 'DAY') {
            // Use hourly data (24 hours)
            chartData = (item.hourly && Array.isArray(item.hourly)) 
              ? item.hourly.map(h => Number(h) || 0)
              : Array(24).fill(0)
          } else if (period === 'WEEKLY') {
            // Use daily data (7 days)
            chartData = (item.daily && Array.isArray(item.daily)) 
              ? item.daily.map(d => Number(d) || 0)
              : Array(7).fill(0)
          } else if (period === 'MONTHLY') {
            // Use weekly data (4-5 weeks)
            chartData = (item.weekly && Array.isArray(item.weekly)) 
              ? item.weekly.map(w => Number(w) || 0)
              : Array(5).fill(0)
          } else if (period === 'ALL TIME') {
            // Use monthly data (12 months)
            chartData = (item.monthly && Array.isArray(item.monthly)) 
              ? item.monthly.map(m => Number(m) || 0)
              : Array(12).fill(0)
          }

          // Convert string values to numbers
          const oeeValue = Number(item.oee) || Number(item.OEE) || 0
          const availValue = Number(item.availability) || 0
          const perfValue = Number(item.performance) || 0
          const qualValue = Number(item.quality) || 0

          return {
            id: index + 1,
            workcellID: Number(item.workcellID) || Number(item.workcell_id) || 0,
            sequence: Number(item.sequence) || 0,
            title: item.workcell || `WC ${index + 1}`,
            status: item.status || 'Idle',
            connection: item.connection || 'Not Connected',
            oee: oeeValue,
            availability: availValue,
            performance: perfValue,
            quality: qualValue,
            bars: oeeValue >= 80 ? 'green' : oeeValue >= 50 ? 'yellow' : 'red',
            hourlyData: chartData
          }
        })

        this.sortWcList()

        this.loadStatus()
        
        // Mark API as connected on success
        this.$emit('api-connected', true)
      } catch (error) {
        console.error(`Error fetching ${period} data:`, error)
        this.$emit('api-connected', false)
        this.$emit('api-error', `Failed to fetch ${period} data: ${error.message}`)
      } finally {
        this.$emit('api-loading', false)
      }
    },
    async loadStatus() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/Running_Status_Workcell')
        if (!response.ok) throw new Error(`API error: ${response.status}`)

        this.$emit('api-loading', true)
        this.$emit('api-error', '')

        const data = await response.json()
        const statusList = data.Status

        // Update wcList status based on API
        this.wcList = this.wcList.map(wc => {
            // Find all API entries matching this workcell
            const matches = statusList.filter(s => s.name.trim().toLowerCase() === wc.title.trim().toLowerCase())

            if (matches.length === 0) {
                // No match found, keep existing status
                return wc
            }

            const allTrue = matches.every(s => s.is_running)
            const allFalse = matches.every(s => !s.is_running)

            let newStatus = 'Idle'
            if (allTrue) {
                newStatus = 'Running'
            } else if (!allFalse) {
                newStatus = 'Partially Running'
            }
            return { ...wc, status: newStatus, connection: 'Connected'}
        })
        this.$emit('api-connected', true)
      } catch (error) {
        console.error("Failed to load WC status:", error)
        this.$emit('api-connected', false)
        this.$emit('api-error', `Failed to fetch status data: ${error.message}`)
      } finally {
          this.$emit('api-loading', false)
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  background: #1a1a1a;
  color: white;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #4b0082;
  color: white;
  font-size: 24px;
  font-weight: bold;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.boxes-grid {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  width: 100%;
}

.footer {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  border-top: 2px solid #333;
  margin-top: 20px;
}

.tab-btn {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #666;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
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

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.card {
  border-radius: 12px;
  padding: 16px;
  background: #f5f5f5;
}

.date-picker-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 20px 0;
  padding: 15px;
  background-color: #2e2e2e;
  border-radius: 8px;
  border: 2px solid #444;
}

.date-input {
  background-color: #1a1a1a;
  border: 2px solid #00baff;
  color: white;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 14px;
  font-family: Arial, sans-serif;
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

.nav-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  margin-bottom: 20px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.nav-btn {
  background: #2e2e2e;
  color: #00baff;
  border: 2px solid #00baff;
  padding: 10px 25px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.nav-btn:hover {
  background: #00baff;
  color: white;
  box-shadow: 0 0 15px rgba(0, 186, 255, 0.4);
}

.page-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-indicator .count {
  font-size: 20px;
  font-weight: bold;
  color: #00baff;
  font-family: monospace;
}

.page-indicator .total {
  font-size: 11px;
  color: #888;
  margin-top: 2px;
}
</style>