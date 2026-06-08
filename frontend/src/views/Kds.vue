<template>
  <div class="h-full flex flex-col p-6 bg-[#0c0c16]">
    <div class="flex justify-between items-center mb-6 shrink-0">
      <div>
        <h2 class="text-2xl font-bold text-white flex items-center gap-2">
          <i class="fa-solid fa-utensils text-pink-500"></i> Kitchen & Bar Display (KDS)
        </h2>
        <p class="text-xs text-slate-500 mt-1">Real-time status controls sync'd to customer tracking notifications.</p>
      </div>
      <button @click="fetchKOTs" class="bg-white/5 border border-white/5 px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:bg-white/10 flex items-center gap-2 transition">
        <i class="fa-solid fa-rotate animate-spin"></i> Refresh Board
      </button>
    </div>

    <!-- Columns layout for prep stages -->
    <div class="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
      <!-- Column 1: Pending Orders -->
      <div class="flex flex-col bg-white/[0.02] border border-white/5 rounded-3xl p-4 overflow-hidden">
        <h3 class="font-bold text-sm text-indigo-400 uppercase tracking-wider mb-4 flex justify-between items-center shrink-0">
          <span>Pending Orders</span>
          <span class="bg-indigo-600/20 text-indigo-400 px-2 py-0.5 rounded-lg text-xs">{{ pendingOrders.length }}</span>
        </h3>
        
        <div class="flex-1 overflow-y-auto space-y-4 pr-1">
          <div v-for="kot in pendingOrders" :key="kot.name" class="bg-[#121224] p-4 rounded-2xl border border-white/5 space-y-3">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-xs font-bold text-white bg-indigo-600/20 text-indigo-300 px-2 py-0.5 rounded-lg mr-2">{{ kot.order_type }}</span>
                <span class="font-bold text-sm text-white">{{ kot.table_id || 'Quick Service' }}</span>
              </div>
              <span class="text-[10px] text-slate-500">{{ kot.name }}</span>
            </div>

            <div class="text-xs space-y-1.5 py-2 border-y border-white/5 text-slate-300">
              <div v-for="(item, idx) in kot.items" :key="idx" class="flex justify-between">
                <span>{{ item.qty }}x {{ item.item_name }}</span>
                <span class="text-slate-500 italic text-[10px]">{{ item.remarks }}</span>
              </div>
            </div>

            <button @click="updateStatus(kot.name, 'Preparing')" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 rounded-xl transition">
              Accept & Start Prep
            </button>
          </div>
        </div>
      </div>

      <!-- Column 2: Preparing -->
      <div class="flex flex-col bg-white/[0.02] border border-white/5 rounded-3xl p-4 overflow-hidden">
        <h3 class="font-bold text-sm text-amber-400 uppercase tracking-wider mb-4 flex justify-between items-center shrink-0">
          <span>Preparing</span>
          <span class="bg-amber-600/20 text-amber-400 px-2 py-0.5 rounded-lg text-xs">{{ preparingOrders.length }}</span>
        </h3>
        
        <div class="flex-1 overflow-y-auto space-y-4 pr-1">
          <div v-for="kot in preparingOrders" :key="kot.name" class="bg-[#121224] p-4 rounded-2xl border border-white/5 space-y-3">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-xs font-bold text-white bg-amber-600/20 text-amber-300 px-2 py-0.5 rounded-lg mr-2">{{ kot.order_type }}</span>
                <span class="font-bold text-sm text-white">{{ kot.table_id || 'Quick Service' }}</span>
              </div>
              <span class="text-[10px] text-slate-500">{{ kot.name }}</span>
            </div>

            <div class="text-xs space-y-1.5 py-2 border-y border-white/5 text-slate-300">
              <div v-for="(item, idx) in kot.items" :key="idx" class="flex justify-between">
                <span>{{ item.qty }}x {{ item.item_name }}</span>
                <span class="text-slate-500 italic text-[10px]">{{ item.remarks }}</span>
              </div>
            </div>

            <button @click="updateStatus(kot.name, 'Ready')" class="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs py-2 rounded-xl transition">
              Mark as Ready
            </button>
          </div>
        </div>
      </div>

      <!-- Column 3: Ready for Pickup / Served -->
      <div class="flex flex-col bg-white/[0.02] border border-white/5 rounded-3xl p-4 overflow-hidden">
        <h3 class="font-bold text-sm text-emerald-400 uppercase tracking-wider mb-4 flex justify-between items-center shrink-0">
          <span>Ready & Served</span>
          <span class="bg-emerald-600/20 text-emerald-400 px-2 py-0.5 rounded-lg text-xs">{{ readyOrders.length }}</span>
        </h3>
        
        <div class="flex-1 overflow-y-auto space-y-4 pr-1">
          <div v-for="kot in readyOrders" :key="kot.name" class="bg-[#121224] p-4 rounded-2xl border border-white/5 space-y-3">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-xs font-bold text-white bg-emerald-600/20 text-emerald-300 px-2 py-0.5 rounded-lg mr-2">{{ kot.order_type }}</span>
                <span class="font-bold text-sm text-white">{{ kot.table_id || 'Quick Service' }}</span>
              </div>
              <span class="text-[10px] text-slate-500">{{ kot.name }}</span>
            </div>

            <div class="text-xs space-y-1.5 py-2 border-y border-white/5 text-slate-300">
              <div v-for="(item, idx) in kot.items" :key="idx" class="flex justify-between">
                <span>{{ item.qty }}x {{ item.item_name }}</span>
              </div>
            </div>

            <button @click="updateStatus(kot.name, 'Served')" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-2 rounded-xl transition">
              Complete / Served
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const kots = ref([])

const pendingOrders = computed(() => kots.value.filter(k => k.status === 'Pending'))
const preparingOrders = computed(() => kots.value.filter(k => k.status === 'Preparing'))
const readyOrders = computed(() => kots.value.filter(k => k.status === 'Ready'))

const fetchKOTs = async () => {
  try {
    const res = await fetch('/api/method/frappe.client.get_list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'KOT Entry',
        fields: ['name', 'table_id', 'order_type', 'status', 'items_json'],
        limit: 30
      })
    })
    
    if (res.ok) {
      const data = await res.json()
      kots.value = (data.message || []).map(k => ({
        ...k,
        items: JSON.parse(k.items_json || '[]')
      }))
    } else {
      loadMockKots()
    }
  } catch (e) {
    loadMockKots()
  }
}

const loadMockKots = () => {
  kots.value = [
    { name: 'KOT-101', table_id: 'Table 2', order_type: 'Dine-In', status: 'Pending', items: [{ qty: 1, item_name: 'Cheeseburger Delight', remarks: 'no onions' }] },
    { name: 'KOT-102', table_id: 'Delivery Order', order_type: 'Delivery', status: 'Preparing', items: [{ qty: 2, item_name: 'Tender Strips', remarks: 'with Ranch' }] },
    { name: 'KOT-103', table_id: 'Table 5', order_type: 'Dine-In', status: 'Ready', items: [{ qty: 1, item_name: 'Old Fashioned Peg (30ml)', remarks: '' }] }
  ]
}

const updateStatus = async (name, nextStatus) => {
  try {
    // If name starts with Mock, just local update
    if (name.startsWith('KOT-')) {
      const idx = kots.value.findIndex(k => k.name === name)
      if (idx > -1) {
        if (nextStatus === 'Served') {
          kots.value.splice(idx, 1)
        } else {
          kots.value[idx].status = nextStatus
        }
      }
      return
    }

    const res = await fetch('/api/method/frappe.client.set_value', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'KOT Entry',
        name: name,
        fieldname: 'status',
        value: nextStatus
      })
    })

    if (res.ok) {
      fetchKOTs()
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchKOTs()
})
</script>
