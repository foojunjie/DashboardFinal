<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY STATION (OVERALL)
    </div>
    <!-- 📌 Workcell Buttons -->
    <div class="wc-btn-group" style="margin: 10px 0; display: flex; align-items: center; gap: 8px; justify-content: center;">
        <!-- Left Arrow -->
        <button class="arrow-btn" @click="scrollWCs('left')">⬅</button>

        <!-- WC Buttons -->
        <div class="wc-buttons-wrapper" ref="wcWrapper" style="display: flex; gap: 8px; overflow-x: auto; scroll-behavior: smooth;">
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

    <!-- Right Arrow -->
    <button class="arrow-btn" @click="scrollWCs('right')">➡</button>
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

    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
        <button class="nav-btn" @click="prevBoxes" >◀ Prev 8</button>
        <span style="font-weight: bold; color: #00baff;">
            Showing {{ boxStartIndex + 1 }} - {{ Math.min(boxStartIndex + 8, filteredWcList.length) }} of {{ filteredWcList.length }}
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
            tabs: ['TODAY', 'DAY', 'WEEKLY', 'MONTHLY', 'ALL TIME'],
            tabWCs:[],
            activePeriod: 'ALL TIME',
            selectedDate: todayISO,
            refreshInterval: null,
            WC: null,
            wcList: []
        }
    },
    async mounted() {
        // Load initial data on mount
        await this.LoadWC()
        // Fetch data for active period
        this.fetchPeriodData(this.WC, this.activePeriod)

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
        }, 60 * 1000) // every 30 seconds
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
                list = list.filter(item => {
                const fullName = `${item.workcellName} Zone ${item.zone}`;
                return fullName.trim().toLowerCase() === this.WC.trim().toLowerCase();});
            }
            return list;
        },
        // Use the filtered list for the rows
        topRow() { 
            return this.filteredWcList.slice(this.boxStartIndex, this.boxStartIndex + 4); 
        },
        bottomRow() { 
            return this.filteredWcList.slice(this.boxStartIndex + 4, this.boxStartIndex + 8); 
        }
    },
    methods: {
        sortWcList() {
            // Sort by workcellID then zone then sequence
            this.wcList.sort((a, b) => {
              if (a.workcellID !== b.workcellID) return a.workcellID - b.workcellID
              if (a.zone !== b.zone) return a.zone - b.zone
              return a.sequence - b.sequence
            })
        },
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
            if (period === 'DAY') {
                // Load today's data when DAY tab is selected
                this.fetchDayData()
            } else {
                this.fetchPeriodData(this.WC, period)
            }
        },
        scrollWCs(direction) {
            const wrapper = this.$refs.wcWrapper;
            if (!wrapper) return;

            const scrollAmount = 150; // Adjust scroll per click
            if (direction === 'left') {
                wrapper.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            } else if (direction === 'right') {
                wrapper.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
        },
        // Add async here
        async LoadWC() {
            try {
                this.$emit('api-loading', true)
                this.$emit('api-error', '')
                const response = await fetch('http://127.0.0.1:8000/api/OEE_by_Station')
                if (!response.ok) throw new Error(`API error: ${response.status}`)

                const data = await response.json()
                // Must use this. to access data property
                this.tabWCs = data.List 
                // Mark API as connected on success
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
            this.fetchPeriodData(this.WC, this.activePeriod);
        },
        fetchDayData() {
            this.fetchPeriodData(this.WC,'DAY', this.selectedDate)
        },
        async fetchPeriodData(WC,period, dateParam) {
            this.$emit('api-loading', true)
            this.$emit('api-error', '')
            console.log('fetchPeriodData called with period:', period, 'dateParam:', dateParam)
            
            try {
            let endpoint = 'http://127.0.0.1:8000/api'
            let params = {}

            if (period === 'TODAY') {
                endpoint += '/OEE_by_Station_per_Day'
            } else if (period === 'DAY') {
                endpoint += '/OEE_by_Station_per_Day'
                params.date = dateParam
            } else if (period === 'WEEKLY') {
                endpoint += '/OEE_by_Station_per_Week'
            } else if (period === 'MONTHLY') {
                endpoint += '/OEE_by_Station_per_Month'
            } else if (period === 'ALL TIME') {
                endpoint += '/OEE_by_Station'
            }

            // Build query string
            const queryString = new URLSearchParams(params).toString()
            const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint

            const response = await fetch(fullUrl)
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`)
            }

            const data = await response.json()
            console.log('API response for period', period, ':', data)
            
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
                    workcellID: Number(item.workcellID) || Number(item.workcell_id) || 0,
                    sequence: Number(item.sequence) || 0,
                    workcellName: item.workcell,
                    zone: Number(item.zone) || 0,
                    station: item.station,
                    // Display title shows both Name and Zone
                    title: item.name,
                    status: item.status || 'Idle',
                    connection: item.connection || 'Not Connected',
                    oee: Number(item.oee) || Number(item.OEE) || 0,
                    availability: Number(item.availability) || 0,
                    performance: Number(item.performance) || 0,
                    quality: Number(item.quality) || 0,
                    bars: (item.oee || item.OEE) > 80 ? 'green' : (item.oee || item.OEE) > 50 ? 'yellow' : 'red',
                    hourlyData: chartData,
                    stationId: item.station || item.station_id || item.id
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
                this.$emit('api-loading', true)
                this.$emit('api-error', '')
                const response = await fetch('http://127.0.0.1:8000/api/Running_Status_Station')
                if (!response.ok) throw new Error(`API error: ${response.status}`)

                const data = await response.json()
                const statusList = data.Status

                // Update wcList status based on API
                this.wcList = this.wcList.map(wc => {
                    // Find all API entries matching this workcell
                    const matches = statusList.filter(
                        s => s.name && wc.workcellName &&
                            s.name.trim().toLowerCase() === wc.workcellName.trim().toLowerCase() &&
                            s.zone === wc.zone && s.station === wc.title)

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

.arrow-btn {
  background-color: #2e2e2e;
  color: white;
  border: 2px solid #666;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.arrow-btn:hover {
  background-color: #3a3a3a;
  border-color: #00baff;
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