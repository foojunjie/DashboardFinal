<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      OEE BY STATION (DETAILED PER DAY)
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



    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
        <button class="nav-btn" @click="prevBoxes" >◀ Prev 8</button>
        <span style="font-weight: bold; color: #00baff;">
            Showing {{ boxStartIndex + 1 }} - {{ Math.min(boxStartIndex + 8, filteredWcList.length) }} of {{ filteredWcList.length }}
        </span>
        <button class="nav-btn" @click="nextBoxes">Next 8 ▶</button>
    </div>

    <div class="boxes-grid">
        <div class="row">
            <WCBoxDetailedPerDay v-for="wc in topRow" :key="wc.id" :wc="wc" :period="activePeriod" />
        </div>
        <div class="row">
            <WCBoxDetailedPerDay v-for="wc in bottomRow" :key="wc.id" :wc="wc" :period="activePeriod" />
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
import WCBoxDetailedPerDay from './WCBoxDetailedPerDay.vue'

export default {
    components: { WCBoxDetailedPerDay },
    data() {
        
        const today = new Date()
        const todayISO = today.toISOString().split('T')[0]
        return {
            boxStartIndex: 0,
            tabs: ['TODAY'],
            tabWCs:[],
            activePeriod: 'TODAY',
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
                hourlyData: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50],
                missed_quantity: 5,
                output_done: 150,
                actual_duration: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42],
                missed_quantity: 8,
                output_done: 142,
                actual_duration: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                missed_quantity: 0,
                output_done: 0,
                actual_duration: Array(24).fill(0),
                ideal_duration: Array(24).fill(0)
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
                hourlyData: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55],
                missed_quantity: 3,
                output_done: 157,
                actual_duration: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40],
                missed_quantity: 10,
                output_done: 140,
                actual_duration: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0],
                missed_quantity: 25,
                output_done: 125,
                actual_duration: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50],
                missed_quantity: 4,
                output_done: 146,
                actual_duration: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35],
                missed_quantity: 6,
                output_done: 144,
                actual_duration: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50],
                missed_quantity: 5,
                output_done: 150,
                actual_duration: [45, 52, 48, 55, 60, 65, 70, 75, 80, 85, 88, 90, 92, 90, 88, 85, 82, 78, 75, 70, 65, 60, 55, 50],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42],
                missed_quantity: 8,
                output_done: 142,
                actual_duration: [40, 45, 42, 48, 52, 58, 62, 68, 72, 78, 82, 85, 88, 86, 84, 80, 76, 72, 68, 64, 58, 52, 48, 42],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                missed_quantity: 0,
                output_done: 0,
                actual_duration: Array(24).fill(0),
                ideal_duration: Array(24).fill(0)
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
                hourlyData: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55],
                missed_quantity: 3,
                output_done: 157,
                actual_duration: [50, 55, 52, 58, 62, 68, 72, 78, 82, 88, 90, 93, 95, 93, 91, 88, 85, 82, 78, 75, 70, 65, 60, 55],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40],
                missed_quantity: 10,
                output_done: 140,
                actual_duration: [35, 40, 38, 42, 48, 52, 58, 62, 68, 72, 76, 80, 82, 80, 78, 75, 72, 68, 65, 60, 55, 50, 45, 40],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0],
                missed_quantity: 25,
                output_done: 125,
                actual_duration: [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 35, 32, 30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 0],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50],
                missed_quantity: 4,
                output_done: 146,
                actual_duration: [42, 48, 45, 52, 58, 64, 70, 75, 80, 85, 88, 91, 93, 91, 89, 86, 83, 80, 76, 72, 68, 62, 56, 50],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
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
                hourlyData: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35],
                missed_quantity: 6,
                output_done: 144,
                actual_duration: [30, 35, 32, 38, 42, 48, 52, 58, 62, 68, 72, 75, 78, 76, 74, 71, 68, 65, 60, 55, 50, 45, 40, 35],
                ideal_duration: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
            }
            ]
        }
    },
    async mounted() {
        // Load initial data on mount
        await this.LoadWC()
        // Fetch data for active period (TODAY)
        this.fetchPeriodData(this.WC, this.activePeriod)

        // Start auto-refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            if (this.activePeriod !== 'FAKE') {
                console.log('Auto-refreshing data...')
            this.fetchPeriodData(this.WC,this.activePeriod)
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
            this.fetchPeriodData(this.WC,period)
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
            // API returns: { workcell, availability, performance, quality, oee, weekly/monthly/daily/hourly } ...and actual_duration/ideal_duration arrays
            this.wcList = apiData.map((item, index) => {
                let chartData = Array(24).fill(0)
                let actualDurationData = Array(24).fill(0)
                let idealDurationData = Array(24).fill(0)

                if (period === 'TODAY' || period === 'DAY') {
                    chartData = (item.hourly && Array.isArray(item.hourly)) ? item.hourly.map(Number) : Array(24).fill(0)
                    actualDurationData = (item.actual_duration && Array.isArray(item.actual_duration)) ? item.actual_duration.map(Number) : Array(24).fill(0)
                    idealDurationData = (item.ideal_duration && Array.isArray(item.ideal_duration)) ? item.ideal_duration.map(Number) : Array(24).fill(0)
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
                    actual_duration: actualDurationData,
                    ideal_duration: idealDurationData,
                    // Add production details when available
                    missed_quantity: Number(item.missed_quantity) || Number(item.missed_qty) || 0,
                    output_done: Number(item.output_done) || Number(item.output) || 0,
                    stationId: item.station || item.station_id || item.id
                }
            })

            // Sort highest OEE → lowest (top = highest)
            this.wcList.sort((a, b) => b.oee - a.oee)

            // If user selected TODAY, fetch Track_Output_Quantity and merge missed/output counts and duration data
            if (period === 'TODAY') {
                try {
                    const trackRes = await fetch('http://127.0.0.1:8000/api/Track_Output_Quantity')
                    if (trackRes.ok) {
                        const trackJson = await trackRes.json()
                        const qty = trackJson.Quantity || {}
                        // qty is an object keyed by station id
                        this.wcList = this.wcList.map(wc => {
                            const key = String(wc.station || wc.stationId || wc.id)
                            const data = qty[key]
                            if (data) {
                                const missed = Number(data.missed_quantity ?? data['missed_quantity'] ?? data.missed_qty ?? 0) || 0
                                const output = Number(data.output_done ?? data['output_done'] ?? data.output ?? 0) || 0
                                
                                // Extract hourly actual_duration and ideal_duration from track data
                                let actualDurationArray = Array(24).fill(0)
                                let idealDurationArray = Array(24).fill(0)
                                
                                if (data.hourly && typeof data.hourly === 'object') {
                                    for (let hour = 0; hour < 24; hour++) {
                                        const hourData = data.hourly[hour]
                                        if (hourData) {
                                            actualDurationArray[hour] = Number(hourData.output_done) || 0
                                            idealDurationArray[hour] = Number(hourData.ideal_quantity) || 0
                                        }
                                    }
                                }
                                
                                return { 
                                    ...wc, 
                                    missed_quantity: missed, 
                                    output_done: output,
                                    actual_duration: actualDurationArray,
                                    ideal_duration: idealDurationArray
                                }
                            }
                            return { ...wc, missed_quantity: wc.missed_quantity || 0, output_done: wc.output_done || 0 }
                        })
                    }
                } catch (e) {
                    console.warn('Failed to fetch Track_Output_Quantity', e)
                }
            }

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
  background: rgba(3, 23, 57, 0.8);
  border: 1px solid rgba(0, 186, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 0 12px rgba(0, 186, 255, 0.15);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
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
