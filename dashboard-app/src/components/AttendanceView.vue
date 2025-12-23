<template>
  <div class="inventory-table-container">
    <table class="inventory-table">
      <thead>
        <tr>
          <th></th>
          <th>YISB</th>
          <th>YAP</th>
          <th>YMP</th>
          <th>BKT F1</th>
          <th>BKY F2</th>
          <th>PGS</th>
        </tr>
      </thead>
      <tbody>
        <tr class="odd-row">
            <td>Total Employee</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="odd-row">
            <td>Today</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td>Indirect Absent</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="odd-row">
            <td>Direct Absent</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="odd-row">
            <td>Indirect On Leave</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td>Direct On Leave</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="odd-row">
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td>Next Week</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="odd-row">
            <td>Indirect Plan Leave</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        <tr class="even-row">
            <td>Direct Plan Leave</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const tableData = ref([])

onMounted(() => {
  const fetchData = async () => {
    try {
      const { quantity, this_month } = (await axios.get('http://127.0.0.1:8000/api/parts_liveE24')).data

      // 🔄 transform SQL rows to table format
      tableData.value = quantity.map(allTimeItem => {
        const todayItem = this_month.find(s => s.PartNumber === allTimeItem.PartNumber)

        return {
          part: allTimeItem.PartNumber,
          name: allTimeItem.Name,
          image: `/picture/${encodeURIComponent(allTimeItem.PartNumber)}.jpg`,

          // qty = all time stock in - all time stock out
          qty: (allTimeItem.stockInAllTime || 0) - (allTimeItem.stockOutAllTime || 0),

          stock_in:todayItem?.stockIn || 0,
          stock_in_times: todayItem?.stockInTimes || 0,
          doc_in: todayItem?.DocStockIn || "-",

          stock_out: todayItem?.stockOut || 0,
          stock_out_times: todayItem?.stockOutTimes || 0,
          doc_out: todayItem?.DocStockOut || "-",

          // balance = today stock in - today stock out
          balance: 0,

          // 👉 If your SQL does not provide these yet, set them zero or later map them
          fg: 0,
          wip: 0,
          doi: 0
        }
      })
    } catch (error) {
      console.error('❌ Failed to load inventory data:', error)
    }
  }

  fetchData() // initial fetch

  const interval = setInterval(fetchData, 5000) // refresh every 5s

  // cleanup on unmount
  onUnmounted(() => clearInterval(interval))

})
</script>

<style scoped>
.inventory-table-container {
  position: relative;
  background-size: 100%;     
  background-position: center;
  background-repeat: no-repeat;
  background-color: white;
  border: 2px solid #512f87;
  border-radius: 6px;
  overflow: hidden;
  height: 100%;
  width: 100%;
}

.inventory-table-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.6); /* white overlay, 60% opacity */
  z-index: 1;
}

.inventory-table {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  border-collapse: collapse;
  text-align: center;
  font-family: 'Segoe UI', sans-serif;
}

.inventory-table th {
  background-color: #7b2cbf;
  color: white;
  padding: 10px;
  font-weight: bold;
  border-bottom: 2px solid #512f87;
   border: 1px solid white;
}

.inventory-table td {
  padding: 8px;
  border: 1px solid white; 
}

/* Alternate row colors */
.odd-row td {
  background-color:rgba(230, 230, 250, 0.8); /* light purple */
}

.even-row td {
  background-color:rgba(211, 211, 211, 0.8); /* light grey */
}

.inventory-table .alt-row {
  background-color: rgba(123, 44, 191, 0.08);
}

.item-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-img {
  width: 50px;
  height: 50px;
  position: relative;
  object-fit: contain;
  opacity: 0.8; /* 60% transparent */
  border-radius: 4px;
}

.inventory-table th,
.inventory-table td {
  font-weight: bold;
}
</style>
