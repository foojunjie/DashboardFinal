<template>
  <div>
    <button @click="currentView = 'dashboard'">Dashboard</button>
    <button @click="currentView = 'table'">Table E24-100-WF</button>
    <button @click="currentView = 'table2'">Table E25-100-WF</button>
    <component :is="currentComponent" />
  </div>
</template>

<script>
import MainDashboard from './components/MainDashboard.vue'
import TableDashboard from './components/tableDashboard.vue'
import TableDashboard2 from './components/tableDashboard2.vue'

export default {
  name: 'App',
  components: {
    MainDashboard,
    TableDashboard,
    TableDashboard2
  },
  data() {
    return {
      currentView: 'dashboard'
    }
  },
  computed: {
    currentComponent() {
      return this.currentView === 'dashboard' ? 'MainDashboard' 
      : this.currentView === 'table'
      ? 'TableDashboard'
      : 'TableDashboard2';
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  height: 100vh;
  background-color: #f5f5f5;
}
button {
  margin: 10px;
  padding: 8px 16px;
  border: none;
  background-color: #3498db;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #2980b9;
}
</style>