<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY ZONE (OVERALL)
    </div>
    <!-- 📌 Workcell Buttons -->
    <div class="wc-btn-group" style="margin: 10px 0; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
        <button 
            @click="selectWC(null)" 
            :class="WC === null ? 'active-wc-btn' : 'wc-btn'">
            ALL
        </button>

        <button
            v-for="wc in tabWCs"
            :key="wc"
            @click="selectWC(wc)" 
            :class="WC === wc ? 'active-wc-btn' : 'wc-btn'"
        >
            {{ wc }}
        </button>
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

    <div v-if="filteredWcList.length > 8" style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 15px;">
        <button class="nav-btn" @click="prevBoxes">◀ Prev 8</button>
        
        <span style="font-family: monospace; color: #00baff; font-weight: bold;">
            {{ boxStartIndex + 1 }}-{{ Math.min(boxStartIndex + 8, filteredWcList.length) }} of {{ filteredWcList.length }}
        </span>
        
        <button class="nav-btn" @click="nextBoxes">Next 8 ▶</button>
    </div>

    <div class="boxes-grid">
        <div class="row">
            <WCBox v-for="wc in topRow" :key="wc.id" :wc="wc" :period="activePeriod" />
        </div>
        <div class="row">
            <WCBox v-for="wc in bottomRow" :key="wc.id" :wc="wc" :period="activePeriod" />
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
            tabs: ['FAKE', 'TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
            tabWCs:[],
            activePeriod: 'FAKE',
            selectedDate: todayISO,
            refreshInterval: null,
            WC: null,
            fakeWcList: [
            {
                id: 1,
                title: 'Zone 1',
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
                title: 'Zone 2',
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
                title: 'Zone 3',
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
                title: 'Zone 4',
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
                title: 'Zone 1',
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
                title: 'Zone 2',
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
                title: 'Zone 7',
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
                title: 'Leak Test',
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
                title: 'Zone 1',
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
                title: 'Zone 2',
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
                title: 'Zone 3',
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
                title: 'Zone 4',
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
                title: 'Zone 1',
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
                title: 'Zone 2',
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
                title: 'Zone 7',
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
                title: 'Leak Test',
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

        this.LoadWC()

        // Start auto-refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            if (this.activePeriod !== 'FAKE') {
                console.log('Auto-refreshing data...')
            if (this.activePeriod === 'DAY') {
                this.fetchDayData()
            } else {
                this.fetchPeriodData(this.WC,this.activePeriod)
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
        filteredWcList() {
            // 1. Start with the full list
            let list = this.wcList;

            // 2. If a specific Workcell is selected, filter by workcellName
            if (this.WC) {
                list = list.filter(item => item.workcellName === this.WC);
            }
            return list;
        },
        currentSet() {
            return this.filteredWcList.slice(this.boxStartIndex, this.boxStartIndex + 8);
        },
        topRow() { 
            return this.currentSet.slice(0, 4); 
        },
        bottomRow() { 
            return this.currentSet.slice(4, 8); 
        }
    },
    methods: {
        nextBoxes() {
            if (this.boxStartIndex + 8 >= this.filteredWcList.length) {
                this.boxStartIndex = 0; 
            } else {
                this.boxStartIndex += 8;
            }
        },
        prevBoxes() {
            if (this.boxStartIndex - 8 < 0) {
                this.boxStartIndex = Math.floor((this.filteredWcList.length - 1) / 8) * 8;
            } else {
                this.boxStartIndex -= 8;
            }
        },
        selectPeriod(period) {
            this.activePeriod = period
            this.boxStartIndex = 0;
            if (period === 'FAKE') {
            this.wcList = JSON.parse(JSON.stringify(this.fakeWcList))
            this.$emit('api-connected', false)
            } else if (period === 'DAY') {
            // Load today's data when DAY tab is selected
            this.fetchDayData()
            } else {
            this.fetchPeriodData(this.WC,period)
            }
        },
        // Add async here
        async LoadWC() {
            try {
                this.$emit('api-loading', true)
                this.$emit('api-error', '')
                const response = await fetch('http://127.0.0.1:8000/api/OEE_by_Zone')
                if (!response.ok) throw new Error(`API error: ${response.status}`)

                const data = await response.json()
                // Must use this. to access data property
                this.tabWCs = data.List 
                this.$emit('api-connected', true)
            } catch (error) {
                console.error("Failed to load WC list:", error)
                this.$emit('api-connected', false)
                this.$emit('api-error', `Failed to fetch List data: ${error.message}`)
            } finally {
                this.$emit('api-loading', false)
            }
        },
        selectWC(WC) {
            this.WC = WC;
            this.boxStartIndex = 0;
            if (this.activePeriod !== 'FAKE') {
                this.fetchPeriodData(this.WC, this.activePeriod);
            }
        },
        fetchDayData() {
            this.fetchPeriodData(this.WC,'DAY', this.selectedDate)
        },
        async fetchPeriodData(WC,period, dateParam) {
            this.$emit('api-loading', true)
            this.$emit('api-error', '')
            
            try {
            let endpoint = 'http://127.0.0.1:8000/api'
            let params = {}

            if (period === 'TODAY') {
                endpoint += '/OEE_by_Zone_per_Day'
            } else if (period === 'DAY') {
                endpoint += '/OEE_by_Zone_per_Day'
                params.date = dateParam
            } else if (period === 'WEEKLY') {
                endpoint += '/OEE_by_Zone_per_Week'
            } else if (period === 'MONTHLY') {
                endpoint += '/OEE_by_Zone_per_Month'
            } else if (period === 'ALL TIME') {
                endpoint += '/OEE_by_Zone'
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
                let chartData = Array(24).fill(0)

                if (period === 'TODAY' || period === 'DAY') {
                    chartData = (item.hourly && Array.isArray(item.hourly)) ? item.hourly.map(Number) : Array(24).fill(0)
                } else if (period === 'WEEKLY') {
                    chartData = (item.daily && Array.isArray(item.daily)) ? item.daily.map(Number) : Array(7).fill(0)
                } else if (period === 'MONTHLY') {
                    chartData = (item.weekly && Array.isArray(item.weekly)) ? item.weekly.map(Number) : Array(5).fill(0)
                } else if (period === 'ALL TIME') {
                    chartData = (item.monthly && Array.isArray(item.monthly)) ? item.monthly.map(Number) : Array(12).fill(0)
                }

                return {
                    id: index + 1,
                    workcellName: item.workcell, 
                    zone: item.zone,
                    // Display title shows both Name and Zone
                    title: `${item.workcell} - Zone ${item.zone}`,
                    status: item.status || 'Idle',
                    connection: item.connection || 'Not Connected',
                    oee: Number(item.oee) || Number(item.OEE) || 0,
                    availability: Number(item.availability) || 0,
                    performance: Number(item.performance) || 0,
                    quality: Number(item.quality) || 0,
                    bars: (item.oee || item.OEE) > 80 ? 'green' : (item.oee || item.OEE) > 50 ? 'yellow' : 'red',
                    hourlyData: chartData
                }
            })

            // Sort highest OEE → lowest (top = highest)
            this.wcList.sort((a, b) => b.oee - a.oee)

            this.loadStatus()
            
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
        created() {
            // ❗AUTO LOAD WC LIST NOW
            this.LoadWC()
        },
        async loadStatus() {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/Running_Status_Zone')
                if (!response.ok) throw new Error(`API error: ${response.status}`)

                this.$emit('api-loading', true)
                this.$emit('api-error', '')

                const data = await response.json()
                const statusList = data.Status

                // Update wcList status based on API
                this.wcList = this.wcList.map(wc => {
                    // Find all API entries matching this workcell
                    const matches = statusList.filter(s => s.name.trim().toLowerCase() === wc.workcellName.trim().toLowerCase() &&
                                                            s.zone === wc.zone)

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
                // Mark API as connected on success
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

.wc-btn {
  padding: 8px 14px;
  border-radius: 8px;
  background: #ddd;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.active-wc-btn {
  padding: 8px 14px;
  border-radius: 8px;
  background: #2196F3; /* blue */
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
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

.nav-btn {
    background: #2e2e2e;
    color: #00baff;
    border: 1px solid #00baff;
    padding: 5px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.2s;
}

.nav-btn:hover {
    background: #00baff;
    color: white;
}

.nav-btn:active {
    transform: scale(0.95);
}
</style>