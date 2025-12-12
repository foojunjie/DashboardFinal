<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY WC (OVERALL)
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

    <!-- Grid: 4 top + 4 bottom -->
    <div class="boxes-grid">
      <!-- Top Row (4 boxes) -->
      <div class="row">
        <WCBox v-for="wc in wcList.slice(0, 4)" :key="wc.id" :wc="wc" :period="activePeriod" />
      </div>
      <!-- Bottom Row (4 boxes) -->
      <div class="row">
        <WCBox v-for="wc in wcList.slice(4, 8)" :key="wc.id" :wc="wc" :period="activePeriod" />
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
      tabs: ['FAKE', 'TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
      activePeriod: 'FAKE',
      selectedDate: todayISO,
      refreshInterval: null,
      fakeWcList: [
        {
          id: 1,
          title: 'M.WC 1',
          status: 'Running',
          connection: 'Connected',
          oee: 95.5,
          availability: 92,
          performance: 96,
          quality: 98,
          bars: 'green',
          hourlyData: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50]
        },
        {
          id: 2,
          title: 'M.WC 2',
          status: 'Running',
          connection: 'Manual',
          oee: 89.3,
          availability: 85,
          performance: 91,
          quality: 92,
          bars: 'green',
          hourlyData: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42]
        },
        {
          id: 3,
          title: 'M.WC 3',
          status: 'Not Running',
          connection: 'Not Connected',
          oee: 0,
          availability: 0,
          performance: 0,
          quality: 0,
          bars: 'red',
          hourlyData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
          id: 4,
          title: 'M.WC 4',
          status: 'Running',
          connection: 'Connected',
          oee: 92.7,
          availability: 90,
          performance: 94,
          quality: 96,
          bars: 'green',
          hourlyData: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55]
        },
        {
          id: 5,
          title: 'HB.WC 1',
          status: 'Running',
          connection: 'Connected',
          oee: 88.2,
          availability: 86,
          performance: 89,
          quality: 90,
          bars: 'green',
          hourlyData: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40]
        },
        {
          id: 6,
          title: 'HB.WC 2',
          status: 'Not Running',
          connection: 'Manual',
          oee: 45.5,
          availability: 40,
          performance: 50,
          quality: 48,
          bars: 'yellow',
          hourlyData: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0]
        },
        {
          id: 7,
          title: 'Pipe Bending',
          status: 'Running',
          connection: 'Connected',
          oee: 91.8,
          availability: 89,
          performance: 93,
          quality: 94,
          bars: 'green',
          hourlyData: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50]
        },
        {
          id: 8,
          title: 'Wet Paint',
          status: 'Running',
          connection: 'Connected',
          oee: 85.4,
          availability: 82,
          performance: 87,
          quality: 88,
          bars: 'green',
          hourlyData: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35]
        }
      ],
      wcList: [
        {
          id: 1,
          title: 'M.WC 1',
          status: 'Running',
          connection: 'Connected',
          oee: 95.5,
          availability: 92,
          performance: 96,
          quality: 98,
          bars: 'green',
          hourlyData: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50]
        },
        {
          id: 2,
          title: 'M.WC 2',
          status: 'Running',
          connection: 'Manual',
          oee: 89.3,
          availability: 85,
          performance: 91,
          quality: 92,
          bars: 'green',
          hourlyData: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42]
        },
        {
          id: 3,
          title: 'M.WC 3',
          status: 'Not Running',
          connection: 'Not Connected',
          oee: 0,
          availability: 0,
          performance: 0,
          quality: 0,
          bars: 'red',
          hourlyData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
          id: 4,
          title: 'M.WC 4',
          status: 'Running',
          connection: 'Connected',
          oee: 92.7,
          availability: 90,
          performance: 94,
          quality: 96,
          bars: 'green',
          hourlyData: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55]
        },
        {
          id: 5,
          title: 'HB.WC 1',
          status: 'Running',
          connection: 'Connected',
          oee: 88.2,
          availability: 86,
          performance: 89,
          quality: 90,
          bars: 'green',
          hourlyData: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40]
        },
        {
          id: 6,
          title: 'HB.WC 2',
          status: 'Not Running',
          connection: 'Manual',
          oee: 45.5,
          availability: 40,
          performance: 50,
          quality: 48,
          bars: 'yellow',
          hourlyData: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0]
        },
        {
          id: 7,
          title: 'Pipe Bending',
          status: 'Running',
          connection: 'Connected',
          oee: 91.8,
          availability: 89,
          performance: 93,
          quality: 94,
          bars: 'green',
          hourlyData: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50]
        },
        {
          id: 8,
          title: 'Wet Paint',
          status: 'Running',
          connection: 'Connected',
          oee: 85.4,
          availability: 82,
          performance: 87,
          quality: 88,
          bars: 'green',
          hourlyData: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35]
        }
      ]
    }
  },
  mounted() {
    // Initialize with fake data on mount
    this.wcList = JSON.parse(JSON.stringify(this.fakeWcList))
    
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
  },
  beforeUnmount() {
    // Clear interval on component unmount
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    selectPeriod(period) {
      this.activePeriod = period
      if (period === 'FAKE') {
        this.wcList = JSON.parse(JSON.stringify(this.fakeWcList))
        this.$emit('api-connected', false)
      } else if (period === 'DAY') {
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
            title: item.workcell || `WC ${index + 1}`,
            status: item.status || 'Running',
            connection: item.connection || 'Connected',
            oee: oeeValue,
            availability: availValue,
            performance: perfValue,
            quality: qualValue,
            bars: oeeValue >= 80 ? 'green' : oeeValue >= 50 ? 'yellow' : 'red',
            hourlyData: chartData
          }
        })
        
        // Mark API as connected on success
        this.$emit('api-connected', true)
      } catch (error) {
        console.error(`Error fetching ${period} data:`, error)
        this.$emit('api-connected', false)
        this.$emit('api-error', `Failed to fetch ${period} data: ${error.message}`)
        // Fall back to fake data on error
        this.wcList = JSON.parse(JSON.stringify(this.fakeWcList))
      } finally {
        this.$emit('api-loading', false)
      }
    },
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
</style>