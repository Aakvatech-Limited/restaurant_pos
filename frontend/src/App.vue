<template>
  <div class="min-h-screen flex flex-col">
    <!-- Main Header -->
    <header class="bg-[#121224] border-b border-white/5 py-4 px-6 flex justify-between items-center shadow-xl">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-xl font-bold text-white shadow-lg shadow-indigo-500/20">
          R
        </div>
        <div>
          <h1 class="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">BistroPOS</h1>
          <span class="text-[10px] text-indigo-400 tracking-widest uppercase font-semibold">ERPNext v15 Engine</span>
        </div>
      </div>
      
      <div class="flex gap-2">
        <button 
          @click="currentView = 'terminal'" 
          :class="['px-5 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all duration-300', currentView === 'terminal' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-white/5 hover:bg-white/10 text-slate-300']"
        >
          <i class="fa-solid fa-cash-register"></i> Terminal
        </button>
        <button 
          @click="currentView = 'kds'" 
          :class="['px-5 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all duration-300', currentView === 'kds' ? 'bg-pink-600 text-white shadow-lg shadow-pink-600/30' : 'bg-white/5 hover:bg-white/10 text-slate-300']"
        >
          <i class="fa-solid fa-utensils"></i> KDS Screen
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-hidden">
      <Terminal v-if="currentView === 'terminal'" />
      <Kds v-else />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Terminal from './views/Terminal.vue'
import Kds from './views/Kds.vue'

const currentView = ref('terminal')
</script>

<style>
/* Custom Scrollbars */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
